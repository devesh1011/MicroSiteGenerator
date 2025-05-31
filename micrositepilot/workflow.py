from agno.workflow import Workflow, RunResponse, RunEvent
from .agents.transcription_agent import transcription_agent, Transcription

# from .agents.info_extractor_agent import (
#     info_extractor,
#     DemoSummary,
# )  # Import DemoSummary
from textwrap import dedent
from agno.agent import Agent
from typing import Iterator, Union, Optional
from logging import Logger
from pathlib import Path
from agno.media import Audio
import os
from dotenv import load_dotenv
import requests  # Added for basic URL downloading

load_dotenv()

# It's good practice to get a logger instance here, though `logging` module needs configuration
logger = Logger(__name__)


class MicroSiteGenerator(Workflow):
    description: str = dedent(
        """\
        An intelligent AI agent that seamlessly transforms product demo call recordings into personalized, interactive recap websites. This workflow orchestrates multiple AI agents to transcribe the demo, intelligently extract key discussion points and features, and dynamically assemble compelling, shareable microsites.
    """
    )

    transcriber: Agent = transcription_agent
    # info_extractor: Agent = info_extractor

    def run(
        self,
        audio_source: str,
        audio_format: str,
        use_transcription_cache: bool = True,
    ) -> Iterator[RunResponse]:
        logger.info("Microsite generation initiated.")

        transcription_results = self.transcribe_audio(audio_source, audio_format)
        if transcription_results:
            yield RunResponse(
                content=transcription_results.transcription,  # The transcription text
                event=RunEvent.workflow_completed,
            )
        else:
            yield RunResponse(
                content="Transcription failed.", event=RunEvent.workflow_completed
            )

    # --- Caching Functions ---
    def get_cached_transcription(
        self, audio_source: Union[str, Path, bytes]
    ) -> Optional[Transcription]:
        """
        Retrieves a cached transcription result for a given audio source.
        """
        # For caching, audio_source needs to be hashable. If it's bytes, convert to a string key.
        cache_key = (
            str(audio_source)
            if isinstance(audio_source, (str, Path))
            else f"bytes_hash_{hash(audio_source)}"
        )
        logger.info(f"Checking if cached transcription exists for {cache_key}.")
        transcription_result = self.session_state.get("transcription_cache", {}).get(
            cache_key
        )
        # Use model_validate to convert dict from cache back to Transcription object
        return (
            Transcription.model_validate(transcription_result)
            if transcription_result and isinstance(transcription_result, dict)
            else None
        )

    def _add_transcription_to_cache(
        self, audio_source: Union[str, Path, bytes], transcription_result: Transcription
    ):
        """
        Adds a transcription result to the session cache.
        """
        cache_key = (
            str(audio_source)
            if isinstance(audio_source, (str, Path))
            else f"bytes_hash_{hash(audio_source)}"
        )
        logger.info(f"Saving transcription results for audio source: {cache_key}")
        self.session_state.setdefault("transcription_cache", {})
        # Store the Pydantic model as a dictionary
        self.session_state["transcription_cache"][
            cache_key
        ] = transcription_result.model_dump()

    # --- Audio Handling Function ---
    def _download_audio(self, url: str) -> bytes:
        """
        Downloads audio from a given URL.
        """
        logger.info(f"Attempting to download audio from URL: {url}")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download audio from {url}: {e}")
            raise ValueError(f"Could not download audio from URL: {e}")

    def _get_audio_bytes(self, source: Union[str, Path, bytes]) -> bytes:
        """
        Retrieves audio content as bytes from various sources (path, URL, or raw bytes).
        """
        if isinstance(source, bytes):
            return source
        elif isinstance(source, (str, Path)):
            str_source = str(source)
            if str_source.startswith(("http://", "https://")):
                return self._download_audio(str_source)
            return Path(str_source).read_bytes()
        raise ValueError("Unsupported audio source type.")

    # --- Transcription Execution Functions ---
    def _run_transcription_agent(
        self,
        audio_source_bytes: bytes,
        audio_format: str,
    ):
        """
        Executes the transcription agent with the given audio bytes.
        """
        logger.info(f"Running transcription agent for audio format: {audio_format}")
        try:
            # self.transcriber.run returns a RunResponse, so access its .content
            run_response: RunResponse = self.transcriber.run(
                input="Transcribe this audio exactly as heard",  # This input might need to be dynamic or removed if agent is purely audio-driven
                audio=[Audio(content=audio_source_bytes, format=audio_format)],
            )
            return run_response.content
        except Exception as e:
            logger.error(f"Transcription agent failed: {str(e)}")
            return None

    def transcribe_audio(
        self,
        audio_source: Union[str, Path, bytes],
        audio_format: str = "wav",
        num_attempts: int = 3,
    ):
        """
        Manages the transcription process, including getting audio bytes and retrying the agent.
        """
        logger.info("Initiating audio transcription process.")
        try:
            audio_bytes = self._get_audio_bytes(audio_source)
        except (ValueError, NotImplementedError) as e:
            logger.error(f"Failed to get audio bytes: {str(e)}")
            return None

        for attempt in range(num_attempts):
            transcription_response = self._run_transcription_agent(
                audio_bytes, audio_format
            )
            if transcription_response:
                logger.info(f"Transcription successful after {attempt + 1} attempt(s).")
                return transcription_response
            else:
                logger.warning(
                    f"Transcription attempt {attempt + 1}/{num_attempts} failed."
                )
        logger.error(
            f"Transcription failed after {num_attempts} attempts for {audio_source}."
        )
        return None

        # # --- Transcription Phase ---
        # transcription_results: Optional[Transcription] = None
        # if use_transcription_cache:
        #     transcription_results = self.get_cached_transcription(audio_source)
        #     if transcription_results:
        #         logger.info(f"Using cached transcription for {audio_source}")
        #         # Yield cached transcription as RunResponse
        #         yield RunResponse(
        #             content=f"Using cached transcription: {transcription_results.transcription}",
        #             event=RunEvent.workflow_completed,
        #         )
        #         return
        #     else:
        #         logger.info(
        #             f"No cached transcription found for {audio_source}, transcribing now."
        #         )
        #         transcription_results = self.transcribe_audio(
        #             audio_source, audio_format
        #         )
        #         if transcription_results:
        #             self._add_transcription_to_cache(
        #                 audio_source, transcription_results
        #             )
        # else:
        #     logger.info(
        #         f"Transcription cache disabled, transcribing {audio_source} now."
        #     )
        #     transcription_results = self.transcribe_audio(audio_source, audio_format)
        #     if transcription_results:
        #         self._add_transcription_to_cache(audio_source, transcription_results)

        # if transcription_results is None:
        #     logger.error("Transcription was not successful. Workflow halted.")
        #     yield RunResponse(
        #         content="Transcription failed. Workflow halted.",
        #         event=RunEvent.workflow_completed,
        #     )
        #     return

        # # --- Information Extraction Phase ---
        # logger.info("Transcription successful. Proceeding to information extraction.")
        # # Run the info_extractor agent and yield its response
        # yield from self.info_extractor.run(
        #     input=transcription_results.transcription,  # Pass the raw string transcription to the extractor
        #     stream=True,
        # )

        # # Cache the final result
        # if (
        #     self.info_extractor.run_response
        #     and self.info_extractor.run_response.content
        # ):
        #     logger.info("Information extraction successful. Workflow completed.")

from agno.agent import Agent
from agno.models.google import Gemini
from textwrap import dedent
from pydantic import BaseModel


class Transcription(BaseModel):
    transcription: str


transcription_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-lite", response_modalities=["text"]),
    description=dedent(
        """\
                Highly accurate, verbatim audio-to-text transcription service.
                Converts spoken words into a detailed textual record, preserving crucial temporal context and speaker identification."""
    ),
    instructions=dedent(
        """\
                Strictly follow these rules for verbatim transcription with timestamps and speaker identification.
                Output the transcription as a continuous string, with each segment on a new line.

                **Output Format:**
                [HH:MM:SS - HH:MM:SS] Speaker Name: Transcribed verbatim speech

                **Transcription Rules (Strictly Adhere to All):**

                1.  **Verbatim Accuracy:** Transcribe every single word exactly as heard.
                2.  **No Interpretation/Summarization:** Do not summarize, interpret, or rephrase speech. Transcribe only what is explicitly said.
                3.  **Unclear Speech:** Use '[inaudible]' for any speech that cannot be clearly understood.
                4.  **Pauses:** Indicate pauses longer than 2 seconds with '...' (three periods) directly within the transcribed text.
                5.  **No Punctuation/Formatting:** Do not add any punctuation (commas, periods, question marks, etc.) or apply any text formatting (bold, italics).
                6.  **Preserve Filler Words:** Include all filler words (e.g., 'um', 'uh', 'like', 'you know').

                **Example of Desired Output:**
                [00:00:00 - 00:00:05] Sales Rep: Good morning Jane thanks for joining the call
                [00:00:05 - 00:00:12] Prospect: Hi Alice excited to learn more about the Microsite Pilot
                [00:00:12 - 00:00:25] Sales Rep: Great today we're going to focus on how we automate post-demo follow-ups
                [00:00:25 - 00:00:30] Prospect: My biggest pain point is the time spent summarizing
                [00:00:30 - 00:00:45] Sales Rep: Exactly our key feature is the 'Instant Microsite Generation' let me show you that
                """
    ),
    response_model=Transcription,
)

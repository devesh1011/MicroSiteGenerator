from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
from .workflow import MicroSiteGenerator
from typing import Optional
import datetime
from typing import AsyncIterator
from agno.workflow import RunResponse

app = FastAPI(
    title="Audio Transcription API with Workflow",
    description="API for converting audio to text using the MicroSiteGenerator workflow",
    version="1.0.0",
)

workflow = MicroSiteGenerator()
executor = ThreadPoolExecutor(max_workers=4)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
async def health_check():
    """Health check endpoint to verify application status."""
    try:
        # Check if upload directory exists and is writable
        upload_dir_status = UPLOAD_DIR.exists() and UPLOAD_DIR.is_dir()

        return {
            "status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "workflow": "operational",
                "upload_directory": "operational" if upload_dir_status else "error",
                "executor": "operational" if executor else "error",
            },
            "uptime": "running",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "error": str(e),
            },
        )


@app.post("/transcribe")
async def generate_microsite_data(file: UploadFile, format: Optional[str] = None):
    """Endpoint for audio file upload and microsite data generation using the workflow."""
    temp_path = None
    try:
        if not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400, detail="Only audio files are supported"
            )

        temp_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
        with temp_path.open("wb") as buffer:
            buffer.write(await file.read())

        audio_format_to_use = format or file.filename.split(".")[-1]

        # Define a function to run the workflow and consume the generator
        def run_workflow():
            responses = list(
                workflow.run(
                    audio_source=str(temp_path),
                    audio_format=audio_format_to_use,
                )
            )
            if responses:
                return responses[
                    -1
                ].content  # Return the content of the final RunResponse
            return None

        site_html = await asyncio.get_event_loop().run_in_executor(
            executor, run_workflow
        )

        if site_html:
            return site_html
        else:
            raise HTTPException(
                status_code=500,
                detail="Workflow failed: No responses returned.",
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /transcribe: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)

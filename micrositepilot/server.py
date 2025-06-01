from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
from .workflow import MicroSiteGenerator
from typing import Optional
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MicroSite Generator API",
    description="API for converting audio recordings to deployed microsites via transcription, content extraction, HTML generation, and Netlify deployment",
    version="1.0.0",
)

origins = [
    "*",  # Allows all origins
    # You can specify specific origins like:
    # "http://localhost",
    # "http://localhost:8000",
    # "https://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
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
async def transcribe_and_deploy_microsite(
    file: UploadFile, format: Optional[str] = None
):
    """Endpoint for audio file upload, transcription, microsite generation, and Netlify deployment."""
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
                # Return the content of the final RunResponse (deployment details)
                final_response = responses[-1].content
                return final_response
            return None

        deployment_result = await asyncio.get_event_loop().run_in_executor(
            executor, run_workflow
        )

        if deployment_result:
            # Format the response to include both deployment and workflow information
            if isinstance(deployment_result, dict) and deployment_result.get("success"):
                return {
                    "status": "success",
                    "message": "Audio successfully transcribed, microsite generated, and deployed to Netlify",
                    "deployment": deployment_result,
                    "workflow_completed": True,
                }
            else:
                return {
                    "status": "partial_success",
                    "message": "Workflow completed but deployment may have failed",
                    "deployment": deployment_result,
                    "workflow_completed": True,
                }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "Workflow failed: No responses returned from transcription and deployment process.",
                    "workflow_completed": False,
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /transcribe: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Transcription and deployment workflow failed: {str(e)}",
                "workflow_completed": False,
            },
        )
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)

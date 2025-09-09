import asyncio
import os
import base64
import aiohttp # Added for aiohttp.ClientSession
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from volc_tts import generate_audio_async

# Load environment variables from .env file (if it exists)
load_dotenv()

# --- Default Configuration ---
DEFAULT_CONCURRENCY = int(os.getenv("VOLCENGINE_TTS_CONCURRENCY", "10"))

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Volcano Engine Concurrent TTS",
    description="A high-performance application for concurrent text-to-speech generation using Volcano Engine, with intelligent batch processing and concurrency management.",
    version="1.0.0",
)

# --- Semaphore for Concurrency Control ---
# This semaphore will be initialized dynamically based on request or default
semaphore = asyncio.Semaphore(DEFAULT_CONCURRENCY)

# --- Pydantic Models for API Data Structure ---
class TaskItem(BaseModel):
    task_id: str = Field(..., description="Unique identifier for the task.")
    text: str = Field(..., description="The text to be converted to speech.")
    voice_type: str = Field("BV001_streaming", description="The voice type to use for synthesis.")
    output_filename: Optional[str] = Field(None, description="Optional: Desired output filename (not used by the application, but can be useful for client-side tracking).")

class VolcanoEngineCredentials(BaseModel):
    volcengine_tts_appid: Optional[str] = Field(None, description="Volcano Engine App ID")
    volcengine_tts_access_key: Optional[str] = Field(None, description="Volcano Engine Access Key")
    volcengine_tts_secret_key: Optional[str] = Field(None, description="Volcano Engine Secret Key")
    volcengine_tts_concurrency: Optional[int] = Field(None, description="Maximum concurrent requests (default: 10)")

class BatchRequest(BaseModel):
    tasks: List[TaskItem]
    credentials: Optional[VolcanoEngineCredentials] = Field(None, description="Optional Volcano Engine credentials (overrides environment variables)")

class TaskResult(BaseModel):
    task_id: str
    audio_base64: str

class BatchResponse(BaseModel):
    results: List[TaskResult]

# --- Helper Functions ---
def get_credentials(request_credentials: Optional[VolcanoEngineCredentials]) -> tuple[str, str, str]:
    """
    Get credentials with priority: request payload > .env > None
    Returns (app_id, access_key, secret_key)
    """
    if request_credentials:
        app_id = request_credentials.volcengine_tts_appid or os.getenv("VOLCENGINE_TTS_APPID")
        access_key = request_credentials.volcengine_tts_access_key or os.getenv("VOLCENGINE_TTS_ACCESS_KEY")
        secret_key = request_credentials.volcengine_tts_secret_key or os.getenv("VOLCENGINE_TTS_SECRET_KEY")
    else:
        app_id = os.getenv("VOLCENGINE_TTS_APPID")
        access_key = os.getenv("VOLCENGINE_TTS_ACCESS_KEY")
        secret_key = os.getenv("VOLCENGINE_TTS_SECRET_KEY")
    
    return app_id, access_key, secret_key

async def process_one_task(session: aiohttp.ClientSession, task: TaskItem, app_id: str, access_key: str, secret_key: str, task_semaphore: asyncio.Semaphore) -> TaskResult:
    """
    Processes a single TTS task, respecting the concurrency semaphore.
    """
    async with task_semaphore:
        try:
            audio_bytes = await generate_audio_async(
                session=session,
                app_id=app_id,
                access_key=access_key,
                secret_key=secret_key,
                text=task.text,
                voice_type=task.voice_type
            )
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            return TaskResult(task_id=task.task_id, audio_base64=audio_base64)
        except Exception as e:
            return TaskResult(task_id=task.task_id, audio_base64="")


# --- API Endpoint ---
@app.post("/generate-batch", response_model=BatchResponse)
async def generate_batch(request: BatchRequest):
    """
    Accepts a batch of TTS tasks and processes them concurrently.
    Credentials priority: request payload > environment variables > error
    """
    # Get credentials with priority: request > .env
    app_id, access_key, secret_key = get_credentials(request.credentials)
    
    # Validate credentials
    if not all([app_id, access_key, secret_key]):
        missing = []
        if not app_id: missing.append("volcengine_tts_appid")
        if not access_key: missing.append("volcengine_tts_access_key") 
        if not secret_key: missing.append("volcengine_tts_secret_key")
        
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required credentials: {', '.join(missing)}. Provide them in the request payload or set environment variables."
        )

    if not request.tasks:
        return BatchResponse(results=[])

    # Get concurrency setting with priority: request > .env > default
    concurrency = DEFAULT_CONCURRENCY
    if request.credentials and request.credentials.volcengine_tts_concurrency is not None:
        concurrency = request.credentials.volcengine_tts_concurrency
    
    # Create a semaphore for this specific request
    request_semaphore = asyncio.Semaphore(concurrency)

    # Create a single aiohttp session for all tasks in this batch
    async with aiohttp.ClientSession() as session:
        # Create a list of asyncio tasks
        asyncio_tasks = [
            process_one_task(session, task_item, app_id, access_key, secret_key, request_semaphore) 
            for task_item in request.tasks
        ]

        # Run all tasks concurrently and wait for them to complete
        results = await asyncio.gather(*asyncio_tasks)

    # Sort results by task_id before returning
    results.sort(key=lambda x: x.task_id)

    return BatchResponse(results=results)

@app.get("/")
def read_root():
    return {"message": f"Volcano Engine Concurrent TTS is running. Default concurrency limit: {DEFAULT_CONCURRENCY}. You can override credentials and concurrency in API requests."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
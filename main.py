import asyncio
import os
import base64
import aiohttp # Added for aiohttp.ClientSession
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from volc_tts import generate_audio_async

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
APP_ID = os.getenv("VOLCENGINE_TTS_APPID")
ACCESS_KEY = os.getenv("VOLCENGINE_TTS_ACCESS_KEY")
SECRET_KEY = os.getenv("VOLCENGINE_TTS_SECRET_KEY")
CONCURRENCY = int(os.getenv("VOLCENGINE_TTS_CONCURRENCY", "10"))

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Volcano Engine Concurrent TTS",
    description="A high-performance application for concurrent text-to-speech generation using Volcano Engine, with intelligent batch processing and concurrency management.",
    version="1.0.0",
)

# --- Semaphore for Concurrency Control ---
# This semaphore limits the number of concurrent calls to the TTS API
semaphore = asyncio.Semaphore(CONCURRENCY)

# --- Pydantic Models for API Data Structure ---
class TaskItem(BaseModel):
    task_id: str = Field(..., description="Unique identifier for the task.")
    text: str = Field(..., description="The text to be converted to speech.")
    voice_type: str = Field("BV001_streaming", description="The voice type to use for synthesis.")
    output_filename: Optional[str] = Field(None, description="Optional: Desired output filename (not used by the application, but can be useful for client-side tracking).")

class BatchRequest(BaseModel):
    tasks: List[TaskItem]

class TaskResult(BaseModel):
    task_id: str
    audio_base64: str

class BatchResponse(BaseModel):
    results: List[TaskResult]

# --- Helper Function for Processing a Single Task ---
async def process_one_task(session: aiohttp.ClientSession, task: TaskItem) -> TaskResult:
    """
    Processes a single TTS task, respecting the concurrency semaphore.
    """
    async with semaphore:
        try:
            audio_bytes = await generate_audio_async(
                session=session,
                app_id=APP_ID,
                access_key=ACCESS_KEY,
                secret_key=SECRET_KEY,
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
    """
    if not all([APP_ID, ACCESS_KEY, SECRET_KEY]):
        raise HTTPException(status_code=500, detail="Server is not configured. Missing Volcano Engine credentials.")

    if not request.tasks:
        return BatchResponse(results=[])

    # Create a single aiohttp session for all tasks in this batch
    async with aiohttp.ClientSession() as session:
        # Create a list of asyncio tasks
        asyncio_tasks = [process_one_task(session, task_item) for task_item in request.tasks]

        # Run all tasks concurrently and wait for them to complete
        results = await asyncio.gather(*asyncio_tasks)

    # Sort results by task_id before returning
    results.sort(key=lambda x: x.task_id)

    return BatchResponse(results=results)

@app.get("/")
def read_root():
    return {"message": f"Volcano Engine Concurrent TTS is running. Concurrency limit is set to {CONCURRENCY}."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
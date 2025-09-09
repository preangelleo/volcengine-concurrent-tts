import os
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from volcengine_client import VolcengineConcurrentTTS, TaskItem as ClientTaskItem, TaskResult as ClientTaskResult

# Load environment variables from .env file (if it exists)
load_dotenv()

# --- Global Concurrency Control ---
# This is the KEY: ONE global semaphore shared across ALL requests
# This ensures total API calls never exceed the account limit
DEFAULT_GLOBAL_CONCURRENCY = int(os.getenv("VOLCENGINE_TTS_CONCURRENCY", "10"))
global_semaphore = None  # Will be created in startup event

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Volcano Engine Concurrent TTS",
    description="A high-performance application for concurrent text-to-speech generation using Volcano Engine, with intelligent batch processing and concurrency management.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    """Initialize global semaphore in the correct event loop"""
    global global_semaphore
    global_semaphore = asyncio.Semaphore(DEFAULT_GLOBAL_CONCURRENCY)
    print(f"🚀 Global concurrency semaphore initialized with limit: {DEFAULT_GLOBAL_CONCURRENCY}")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    global global_semaphore
    global_semaphore = None
    print("🛑 Global concurrency semaphore cleaned up")

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

    # Ensure global semaphore is initialized
    if global_semaphore is None:
        raise HTTPException(
            status_code=500,
            detail="Global concurrency semaphore not initialized. Server may still be starting up."
        )

    # NOTE: Concurrency is now controlled by the GLOBAL semaphore
    # Individual request concurrency settings are ignored for global control
    # This ensures total API calls across ALL requests never exceed account limit
    
    # Create client instance (concurrency parameter is not used when external_semaphore is provided)
    client = VolcengineConcurrentTTS(
        app_id=app_id,
        access_key=access_key, 
        secret_key=secret_key,
        concurrency=10  # This is ignored when using external_semaphore
    )
    
    # Convert API TaskItems to Client TaskItems
    client_tasks = [
        ClientTaskItem(
            task_id=task.task_id,
            text=task.text,
            voice_type=task.voice_type,
            output_filename=task.output_filename
        )
        for task in request.tasks
    ]
    
    # CRITICAL: Pass global_semaphore to ensure all requests share the same concurrency limit
    client_results = await client.generate_batch_async(client_tasks, external_semaphore=global_semaphore)
    
    # Convert Client TaskResults to API TaskResults
    results = [
        TaskResult(task_id=result.task_id, audio_base64=result.audio_base64)
        for result in client_results
    ]

    return BatchResponse(results=results)

@app.get("/")
def read_root():
    available_slots = global_semaphore._value if global_semaphore else "Not initialized"
    return {
        "message": f"Volcano Engine Concurrent TTS is running with GLOBAL concurrency control.",
        "global_concurrency_limit": DEFAULT_GLOBAL_CONCURRENCY,
        "current_available_slots": available_slots,
        "architecture": "All requests share a single global semaphore to prevent exceeding account limits",
        "note": "Individual request concurrency settings are ignored in server mode for global control",
        "semaphore_status": "initialized" if global_semaphore else "not_initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
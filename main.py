import os
import asyncio
from typing import List, Optional, Tuple
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from volcengine_client import VolcengineConcurrentTTS, TaskItem as ClientTaskItem, TaskResult as ClientTaskResult

# Load environment variables from .env file (if it exists)
load_dotenv()

# --- Service Configuration ---
# Admin API Key for trusted, internal requests
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')

# Server's own Volcano Engine credentials (optional)
# Can be used by requests authenticated with the Admin API Key
SERVER_VOLCENGINE_TTS_APPID = os.getenv('VOLCENGINE_TTS_APPID')
SERVER_VOLCENGINE_TTS_ACCESS_KEY = os.getenv('VOLCENGINE_TTS_ACCESS_KEY')

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
    print("✅ Volcano Engine Concurrent TTS started.")
    print(f"🚦 Global concurrency limit set to: {DEFAULT_GLOBAL_CONCURRENCY}")
    if ADMIN_API_KEY:
        print("🔑 Admin API Key is configured.")
    if SERVER_VOLCENGINE_TTS_APPID and SERVER_VOLCENGINE_TTS_ACCESS_KEY:
        print("🔑 Server's own Volcano Engine credentials are configured.")

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
    volcengine_tts_concurrency: Optional[int] = Field(None, description="Maximum concurrent requests (default: 10)")

class BatchRequest(BaseModel):
    tasks: List[TaskItem]
    credentials: Optional[VolcanoEngineCredentials] = Field(None, description="Optional Volcano Engine credentials (overrides environment variables)")

class TaskResult(BaseModel):
    task_id: str
    audio_base64: str

class BatchResponse(BaseModel):
    results: List[TaskResult]

# --- Authentication Helper ---
def get_credentials_from_request(request: Request, request_credentials: Optional[VolcanoEngineCredentials]) -> Tuple[str, str, Optional[str], Optional[int]]:
    """
    Determines the appropriate Volcano Engine credentials based on a 3-tier authentication logic.

    Tier 1: Admin Key in Header -> Uses Server's Credentials
    Tier 2: Credentials in Payload -> Uses User's Credentials  
    Tier 3: Environment Variables -> Uses Server's Credentials
    Tier 4: Failure

    Returns:
        A tuple of (app_id, access_key, error_message, status_code).
        On success, app_id and access_key are strings and the other two are None.
        On failure, app_id and access_key are None and the other two have values.
    """
    # Tier 1: Check for Admin API Key in headers
    admin_key_from_header = request.headers.get('Admin-API-Key')
    if ADMIN_API_KEY and admin_key_from_header == ADMIN_API_KEY:
        if SERVER_VOLCENGINE_TTS_APPID and SERVER_VOLCENGINE_TTS_ACCESS_KEY:
            # Admin is authenticated and server has credentials
            return SERVER_VOLCENGINE_TTS_APPID, SERVER_VOLCENGINE_TTS_ACCESS_KEY, None, None
        else:
            # Admin is authenticated, but server is not configured with credentials
            error_msg = "Admin authenticated, but the service is not configured with VOLCENGINE_TTS_APPID and VOLCENGINE_TTS_ACCESS_KEY."
            return None, None, error_msg, 500  # Internal Server Error

    # Tier 2: Check for user-provided credentials in the request payload
    if request_credentials:
        app_id = request_credentials.volcengine_tts_appid 
        access_key = request_credentials.volcengine_tts_access_key
        if app_id and access_key:
            return app_id, access_key, None, None

    # Tier 3: Fallback to environment variables (for backward compatibility)
    app_id = os.getenv("VOLCENGINE_TTS_APPID")
    access_key = os.getenv("VOLCENGINE_TTS_ACCESS_KEY")
    if app_id and access_key:
        return app_id, access_key, None, None

    # Tier 4: Authentication failed
    error_msg = "Authentication failed. Provide 'Admin-API-Key' in headers or complete credentials in payload."
    return None, None, error_msg, 401  # Unauthorized

# --- Legacy Helper Function (for backward compatibility) ---
def get_credentials(request_credentials: Optional[VolcanoEngineCredentials]) -> tuple[str, str]:
    """
    Legacy function for backward compatibility.
    Get credentials with priority: request payload > .env > None
    Returns (app_id, access_key)
    """
    if request_credentials:
        app_id = request_credentials.volcengine_tts_appid or os.getenv("VOLCENGINE_TTS_APPID")
        access_key = request_credentials.volcengine_tts_access_key or os.getenv("VOLCENGINE_TTS_ACCESS_KEY")
    else:
        app_id = os.getenv("VOLCENGINE_TTS_APPID")
        access_key = os.getenv("VOLCENGINE_TTS_ACCESS_KEY")
    
    return app_id, access_key


# --- API Endpoint ---
@app.post("/generate-batch", response_model=BatchResponse)
async def generate_batch(request: BatchRequest, http_request: Request):
    """
    Accepts a batch of TTS tasks and processes them concurrently.
    Authentication: Admin API Key in header OR credentials in payload OR environment variables
    """
    # Get credentials using new authentication logic
    app_id, access_key, error_msg, status_code = get_credentials_from_request(http_request, request.credentials)
    
    if error_msg:
        raise HTTPException(status_code=status_code, detail=error_msg)

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
        "status": "ok",
        "service": "volcengine-concurrent-tts",
        "message": f"Volcano Engine Concurrent TTS is running with GLOBAL concurrency control.",
        "global_concurrency_limit": DEFAULT_GLOBAL_CONCURRENCY,
        "current_available_slots": available_slots,
        "architecture": "All requests share a single global semaphore to prevent exceeding account limits",
        "note": "Individual request concurrency settings are ignored in server mode for global control",
        "semaphore_status": "initialized" if global_semaphore else "not_initialized",
        "admin_key_configured": bool(ADMIN_API_KEY),
        "server_credentials_configured": bool(SERVER_VOLCENGINE_TTS_APPID and SERVER_VOLCENGINE_TTS_ACCESS_KEY),
        "authentication": {
            "admin_api_key": "Admin-API-Key header authentication supported",
            "user_credentials": "User-provided credentials in payload supported", 
            "environment_variables": "Environment variable fallback supported"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
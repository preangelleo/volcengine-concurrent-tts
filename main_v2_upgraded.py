"""
Volcano Engine Concurrent TTS v2.0 - Enhanced with External Semaphore Pattern
Upgraded to match Replicate's advanced architecture with perfect input/output correspondence
"""

import os
import asyncio
import threading
from typing import List, Optional, Tuple, Dict, Any
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
SERVER_VOLCENGINE_TTS_APPID = os.getenv('VOLCENGINE_TTS_APPID')
SERVER_VOLCENGINE_TTS_ACCESS_KEY = os.getenv('VOLCENGINE_TTS_ACCESS_KEY')

# --- Global Concurrency Control ---
DEFAULT_GLOBAL_CONCURRENCY = int(os.getenv("VOLCENGINE_TTS_CONCURRENCY", "10"))
global_semaphore = None  # Will be created in startup event

# --- External Semaphore Pattern Support ---
# Global semaphore registry for cross-service coordination
_global_semaphores: Dict[str, asyncio.Semaphore] = {}
_global_semaphores_lock = asyncio.Lock()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Volcano Engine Concurrent TTS v2.0",
    description="Enhanced text-to-speech generation with External Semaphore Pattern, perfect input/output correspondence, and advanced batch processing.",
    version="2.0.0-external-semaphore-enhanced",
)

@app.on_event("startup")
async def startup_event():
    """Initialize global semaphore and external semaphore registry"""
    global global_semaphore
    global _global_semaphores_lock
    _global_semaphores_lock = asyncio.Lock()
    global_semaphore = asyncio.Semaphore(DEFAULT_GLOBAL_CONCURRENCY)
    
    print("✅ Volcano Engine Concurrent TTS v2.0 Enhanced started.")
    print(f"🚦 Global concurrency limit set to: {DEFAULT_GLOBAL_CONCURRENCY}")
    print(f"🌐 External Semaphore Pattern: ✅ Enabled")
    if ADMIN_API_KEY:
        print("🔑 Admin API Key is configured.")
    if SERVER_VOLCENGINE_TTS_APPID and SERVER_VOLCENGINE_TTS_ACCESS_KEY:
        print("🔑 Server's own Volcano Engine credentials are configured.")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    global global_semaphore, _global_semaphores
    global_semaphore = None
    _global_semaphores.clear()
    print("🛑 All semaphores cleaned up")

# --- Enhanced Pydantic Models for Advanced Architecture ---
class TaskItem(BaseModel):
    """Enhanced task item with Replicate-style structure"""
    prompt: str = Field(..., description="The text to be converted to speech (renamed from 'text' for consistency)")
    output_filename: Optional[str] = Field(None, description="Desired output filename (with or without extension)")
    voice_type: str = Field("BV001_streaming", description="The voice type to use for synthesis")
    # Task-specific parameters (following Replicate pattern)
    task_id: Optional[str] = Field(None, description="Optional unique identifier for tracking (auto-generated if not provided)")
    
    # Advanced TTS parameters
    speed: Optional[float] = Field(None, description="Speech speed (0.5 - 2.0)")
    volume: Optional[float] = Field(None, description="Volume level (0.0 - 1.0)")
    pitch: Optional[float] = Field(None, description="Pitch adjustment (-12 to +12 semitones)")

class VolcanoEngineCredentials(BaseModel):
    volcengine_tts_appid: Optional[str] = Field(None, description="Volcano Engine App ID")
    volcengine_tts_access_key: Optional[str] = Field(None, description="Volcano Engine Access Key")
    volcengine_tts_concurrency: Optional[int] = Field(None, description="Maximum concurrent requests (default: 10)")

class BatchRequest(BaseModel):
    """Enhanced batch request with External Semaphore Pattern support"""
    tasks: List[TaskItem] = Field(..., description="List of TTS generation tasks")
    credentials: Optional[VolcanoEngineCredentials] = Field(None, description="Optional credentials (overrides environment)")
    external_semaphore_id: Optional[str] = Field(None, description="Optional external semaphore ID for cross-service coordination")

class GeneratedFile(BaseModel):
    """Generated file information following Replicate pattern"""
    url: Optional[str] = Field(None, description="Direct URL to generated audio (if URL mode enabled)")
    filename: str = Field(..., description="Generated filename")
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio data (if not using URL mode)")
    duration_seconds: Optional[float] = Field(None, description="Audio duration in seconds")

class TaskResult(BaseModel):
    """Enhanced task result with perfect input/output correspondence"""
    task_index: int = Field(..., description="Index corresponding to input task")
    prompt: str = Field(..., description="Original text prompt")
    output_filename: str = Field(..., description="Requested output filename")
    generated_files: List[GeneratedFile] = Field(..., description="Generated audio files")
    count: int = Field(..., description="Number of generated files")
    task_id: Optional[str] = Field(None, description="Task identifier (if provided)")
    voice_type: str = Field(..., description="Voice type used")
    success: bool = Field(True, description="Whether generation was successful")

class BatchResponse(BaseModel):
    """Enhanced batch response following Replicate pattern"""
    success: bool = Field(True, description="Overall batch success status")
    total_tasks: int = Field(..., description="Total number of input tasks")
    successful_count: int = Field(..., description="Number of successful generations")
    failed_count: int = Field(..., description="Number of failed generations")
    successful_results: List[TaskResult] = Field(..., description="Successfully generated results")
    failed_results: List[Dict[str, Any]] = Field(default_factory=list, description="Failed tasks with error details")
    external_semaphore_used: bool = Field(False, description="Whether external semaphore was used")
    semaphore_id: Optional[str] = Field(None, description="External semaphore ID used")

class ExternalSemaphoreRequest(BaseModel):
    """Request to register external semaphore"""
    semaphore_id: str = Field(..., description="Unique identifier for the semaphore")
    limit: int = Field(..., description="Maximum concurrent operations", ge=1, le=1000)

class ExternalSemaphoreResponse(BaseModel):
    """Response for semaphore operations"""
    success: bool = Field(True)
    message: str = Field(...)
    semaphore_id: str = Field(...)
    limit: Optional[int] = Field(None)
    all_semaphores: List[str] = Field(default_factory=list)

# --- External Semaphore Pattern Functions ---
async def register_global_semaphore(semaphore_id: str, limit: int) -> asyncio.Semaphore:
    """Register a global semaphore for cross-service coordination"""
    async with _global_semaphores_lock:
        if semaphore_id in _global_semaphores:
            print(f"⚠️ Global semaphore '{semaphore_id}' already exists, returning existing one")
            return _global_semaphores[semaphore_id]
        
        semaphore = asyncio.Semaphore(limit)
        _global_semaphores[semaphore_id] = semaphore
        print(f"🌐 Global semaphore '{semaphore_id}' registered with limit {limit}")
        return semaphore

async def get_global_semaphore(semaphore_id: str) -> Optional[asyncio.Semaphore]:
    """Get a registered global semaphore by ID"""
    async with _global_semaphores_lock:
        return _global_semaphores.get(semaphore_id)

async def list_global_semaphores() -> List[str]:
    """List all registered global semaphores"""
    async with _global_semaphores_lock:
        return list(_global_semaphores.keys())

# --- Enhanced Authentication Helper ---
def get_credentials_from_request(request: Request, request_credentials: Optional[VolcanoEngineCredentials]) -> Tuple[str, str, Optional[str], Optional[int]]:
    """
    Enhanced 3-tier authentication system
    
    Tier 1: Admin Key in Header -> Uses Server's Credentials
    Tier 2: Credentials in Payload -> Uses User's Credentials  
    Tier 3: Environment Variables -> Uses Server's Credentials
    Tier 4: Failure
    """
    # Tier 1: Check for Admin API Key in headers
    admin_key_from_header = request.headers.get('Admin-API-Key')
    if ADMIN_API_KEY and admin_key_from_header == ADMIN_API_KEY:
        if SERVER_VOLCENGINE_TTS_APPID and SERVER_VOLCENGINE_TTS_ACCESS_KEY:
            return SERVER_VOLCENGINE_TTS_APPID, SERVER_VOLCENGINE_TTS_ACCESS_KEY, None, None
        else:
            error_msg = "Admin authenticated, but server lacks VOLCENGINE_TTS_APPID and VOLCENGINE_TTS_ACCESS_KEY."
            return None, None, error_msg, 500

    # Tier 2: Check for user-provided credentials in the request payload
    if request_credentials:
        app_id = request_credentials.volcengine_tts_appid 
        access_key = request_credentials.volcengine_tts_access_key
        if app_id and access_key:
            return app_id, access_key, None, None

    # Tier 3: Fallback to environment variables
    app_id = os.getenv("VOLCENGINE_TTS_APPID")
    access_key = os.getenv("VOLCENGINE_TTS_ACCESS_KEY")
    if app_id and access_key:
        return app_id, access_key, None, None

    # Tier 4: Authentication failed
    error_msg = "Authentication failed. Provide 'Admin-API-Key' in headers or complete credentials in payload."
    return None, None, error_msg, 401

# --- Enhanced API Endpoints ---
@app.get("/")
def read_root():
    """Enhanced health check with External Semaphore Pattern info"""
    available_slots = global_semaphore._value if global_semaphore else "Not initialized"
    return {
        "status": "healthy",
        "service": "volcengine-concurrent-tts",
        "version": "2.0.0-external-semaphore-enhanced",
        "message": "Enhanced Volcano Engine Concurrent TTS with External Semaphore Pattern",
        "architecture": {
            "external_semaphore_pattern": "✅ Enabled",
            "perfect_input_output_correspondence": "✅ Enabled", 
            "advanced_batch_processing": "✅ Enabled",
            "cross_service_coordination": "✅ Enabled"
        },
        "concurrency_status": {
            "global_concurrency_limit": DEFAULT_GLOBAL_CONCURRENCY,
            "current_available_slots": available_slots,
            "external_semaphores_count": len(_global_semaphores)
        },
        "semaphore_status": "initialized" if global_semaphore else "not_initialized",
        "admin_key_configured": bool(ADMIN_API_KEY),
        "server_credentials_configured": bool(SERVER_VOLCENGINE_TTS_APPID and SERVER_VOLCENGINE_TTS_ACCESS_KEY),
        "authentication": {
            "admin_api_key": "✅ Admin-API-Key header authentication",
            "user_credentials": "✅ User-provided credentials in payload", 
            "environment_variables": "✅ Environment variable fallback"
        }
    }

@app.get("/_admin/semaphores")
async def list_semaphores():
    """List all registered external semaphores (Admin endpoint)"""
    semaphores = await list_global_semaphores()
    return {
        "global_semaphores": semaphores,
        "count": len(semaphores)
    }

@app.post("/_admin/semaphores", response_model=ExternalSemaphoreResponse)
async def register_semaphore(request: ExternalSemaphoreRequest, http_request: Request):
    """Register a new external semaphore (Admin only)"""
    # Verify admin API key
    admin_key = http_request.headers.get('Admin-API-Key')
    if admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Admin API key required")
    
    try:
        semaphore = await register_global_semaphore(request.semaphore_id, request.limit)
        all_semaphores = await list_global_semaphores()
        
        return ExternalSemaphoreResponse(
            success=True,
            message=f"Global semaphore '{request.semaphore_id}' registered successfully",
            semaphore_id=request.semaphore_id,
            limit=request.limit,
            all_semaphores=all_semaphores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-batch", response_model=BatchResponse)
async def generate_batch_enhanced(request: BatchRequest, http_request: Request):
    """
    Enhanced batch generation with External Semaphore Pattern and perfect input/output correspondence
    
    Features:
    - Perfect input/output correspondence with task_index mapping
    - External semaphore support for cross-service coordination
    - Enhanced file naming with proper extensions
    - Detailed success/failure tracking
    - Replicate-style response structure
    """
    # Enhanced 3-tier authentication
    app_id, access_key, error_msg, status_code = get_credentials_from_request(http_request, request.credentials)
    
    if error_msg:
        raise HTTPException(status_code=status_code, detail=error_msg)

    if not request.tasks:
        return BatchResponse(
            success=True,
            total_tasks=0,
            successful_count=0,
            failed_count=0,
            successful_results=[],
            failed_results=[]
        )

    # Determine which semaphore to use
    semaphore_to_use = global_semaphore
    external_semaphore_used = False
    
    if request.external_semaphore_id:
        external_semaphore = await get_global_semaphore(request.external_semaphore_id)
        if not external_semaphore:
            available_semaphores = await list_global_semaphores()
            raise HTTPException(
                status_code=400,
                detail=f"External semaphore '{request.external_semaphore_id}' not found. Available: {available_semaphores}"
            )
        semaphore_to_use = external_semaphore
        external_semaphore_used = True

    # Ensure semaphore is initialized
    if semaphore_to_use is None:
        raise HTTPException(
            status_code=500,
            detail="Concurrency semaphore not initialized. Server may still be starting up."
        )

    # Create client instance
    client = VolcengineConcurrentTTS(
        app_id=app_id,
        access_key=access_key,
        concurrency=10  # This is ignored when using external_semaphore
    )
    
    # Convert enhanced TaskItems to Client TaskItems with auto-generated task_ids
    client_tasks = []
    for i, task in enumerate(request.tasks):
        # Auto-generate task_id if not provided
        task_id = task.task_id or f"task_{i+1}_{hash(task.prompt) % 10000}"
        
        client_task = ClientTaskItem(
            task_id=task_id,
            text=task.prompt,  # Map prompt to text for client compatibility
            voice_type=task.voice_type,
            output_filename=task.output_filename
        )
        client_tasks.append(client_task)
    
    # Execute with proper semaphore control
    try:
        client_results = await client.generate_batch_async(client_tasks, external_semaphore=semaphore_to_use)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
    
    # Process results with perfect input/output correspondence
    successful_results = []
    failed_results = []
    
    for i, (task, result) in enumerate(zip(request.tasks, client_results)):
        try:
            # Determine output filename with proper extension
            if task.output_filename:
                base_filename = task.output_filename
                if not base_filename.endswith(('.mp3', '.wav', '.m4a')):
                    base_filename += '.mp3'  # Default to mp3
            else:
                base_filename = f"generated_audio_{i+1}.mp3"
            
            # Create generated file info
            generated_file = GeneratedFile(
                filename=base_filename,
                audio_base64=result.audio_base64 if result.audio_base64 else None,
                # Note: URL mode not implemented yet, but structure ready
                url=None,
                duration_seconds=None  # Could be calculated if needed
            )
            
            # Create task result with perfect correspondence
            task_result = TaskResult(
                task_index=i,
                prompt=task.prompt,
                output_filename=base_filename,
                generated_files=[generated_file],
                count=1,
                task_id=client_tasks[i].task_id,
                voice_type=task.voice_type,
                success=bool(result.audio_base64)
            )
            
            if result.audio_base64:
                successful_results.append(task_result)
            else:
                # Mark as failed if no audio data
                failed_results.append({
                    "task_index": i,
                    "prompt": task.prompt,
                    "output_filename": base_filename,
                    "error": "Empty audio data returned",
                    "task_id": client_tasks[i].task_id
                })
                
        except Exception as e:
            failed_results.append({
                "task_index": i,
                "prompt": task.prompt,
                "output_filename": task.output_filename or f"generated_audio_{i+1}.mp3",
                "error": str(e),
                "task_id": client_tasks[i].task_id if i < len(client_tasks) else None
            })
    
    # Create enhanced response
    return BatchResponse(
        success=len(failed_results) == 0,
        total_tasks=len(request.tasks),
        successful_count=len(successful_results),
        failed_count=len(failed_results),
        successful_results=successful_results,
        failed_results=failed_results,
        external_semaphore_used=external_semaphore_used,
        semaphore_id=request.external_semaphore_id
    )

# Legacy endpoint for backward compatibility
@app.post("/generate-batch-legacy")
async def generate_batch_legacy(request: BatchRequest, http_request: Request):
    """Legacy endpoint maintaining old response format for backward compatibility"""
    # Get credentials using new authentication logic
    app_id, access_key, error_msg, status_code = get_credentials_from_request(http_request, request.credentials)
    
    if error_msg:
        raise HTTPException(status_code=status_code, detail=error_msg)

    if not request.tasks:
        return {"results": []}

    if global_semaphore is None:
        raise HTTPException(
            status_code=500,
            detail="Global concurrency semaphore not initialized."
        )

    # Create client instance
    client = VolcengineConcurrentTTS(
        app_id=app_id,
        access_key=access_key,
        concurrency=10
    )
    
    # Convert API TaskItems to Client TaskItems (legacy format)
    client_tasks = [
        ClientTaskItem(
            task_id=task.task_id or f"legacy_task_{i+1}",
            text=task.prompt,
            voice_type=task.voice_type,
            output_filename=task.output_filename
        )
        for i, task in enumerate(request.tasks)
    ]
    
    # Execute with global semaphore
    client_results = await client.generate_batch_async(client_tasks, external_semaphore=global_semaphore)
    
    # Convert to legacy format
    results = [
        {"task_id": result.task_id, "audio_base64": result.audio_base64}
        for result in client_results
    ]

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import asyncio
import base64
from typing import List, Optional
import aiohttp
from volc_tts import generate_audio_async


class TaskItem:
    """Task item for TTS generation"""
    def __init__(self, task_id: str, text: str, voice_type: str = "BV001_streaming", output_filename: Optional[str] = None):
        self.task_id = task_id
        self.text = text
        self.voice_type = voice_type
        self.output_filename = output_filename


class TaskResult:
    """Result of TTS generation"""
    def __init__(self, task_id: str, audio_base64: str):
        self.task_id = task_id
        self.audio_base64 = audio_base64
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "audio_base64": self.audio_base64
        }


class VolcengineConcurrentTTS:
    """
    Volcengine Concurrent TTS Client
    
    A high-performance client for concurrent text-to-speech generation using Volcano Engine's TTS API.
    Supports both synchronous and asynchronous batch processing with intelligent concurrency management.
    
    Usage:
        # Initialize client
        client = VolcengineConcurrentTTS(
            app_id="your_app_id",
            access_key="your_access_key", 
            secret_key="your_secret_key",
            concurrency=10
        )
        
        # Create tasks
        tasks = [
            TaskItem("task1", "Hello world", "BV001_streaming"),
            TaskItem("task2", "How are you?", "BV002_streaming")
        ]
        
        # Async usage
        results = await client.generate_batch_async(tasks)
        
        # Sync usage
        results = client.generate_batch_sync(tasks)
    """
    
    def __init__(self, app_id: str, access_key: str, secret_key: str, concurrency: int = 10):
        """
        Initialize the Volcengine TTS client
        
        Args:
            app_id: Volcano Engine App ID
            access_key: Volcano Engine Access Key
            secret_key: Volcano Engine Secret Key
            concurrency: Maximum concurrent requests (default: 10)
        """
        self.app_id = app_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.concurrency = concurrency
        
        if not all([app_id, access_key, secret_key]):
            raise ValueError("app_id, access_key, and secret_key are required")
    
    async def _process_one_task(self, session: aiohttp.ClientSession, task: TaskItem, semaphore: asyncio.Semaphore) -> TaskResult:
        """
        Process a single TTS task with concurrency control
        
        Args:
            session: aiohttp ClientSession
            task: TaskItem to process
            semaphore: Semaphore for concurrency control
            
        Returns:
            TaskResult with generated audio
        """
        async with semaphore:
            try:
                audio_bytes = await generate_audio_async(
                    session=session,
                    app_id=self.app_id,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    text=task.text,
                    voice_type=task.voice_type
                )
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                return TaskResult(task_id=task.task_id, audio_base64=audio_base64)
            except Exception as e:
                # Return empty result on error
                return TaskResult(task_id=task.task_id, audio_base64="")
    
    async def generate_batch_async(self, tasks: List[TaskItem]) -> List[TaskResult]:
        """
        Asynchronously generate TTS for a batch of tasks
        
        Args:
            tasks: List of TaskItem objects to process
            
        Returns:
            List of TaskResult objects with generated audio
        """
        if not tasks:
            return []
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.concurrency)
        
        # Create a single aiohttp session for all tasks
        async with aiohttp.ClientSession() as session:
            # Create asyncio tasks
            asyncio_tasks = [
                self._process_one_task(session, task, semaphore)
                for task in tasks
            ]
            
            # Run all tasks concurrently
            results = await asyncio.gather(*asyncio_tasks)
        
        # Sort results by task_id
        results.sort(key=lambda x: x.task_id)
        return results
    
    def generate_batch_sync(self, tasks: List[TaskItem]) -> List[TaskResult]:
        """
        Synchronously generate TTS for a batch of tasks
        
        Args:
            tasks: List of TaskItem objects to process
            
        Returns:
            List of TaskResult objects with generated audio
        """
        return asyncio.run(self.generate_batch_async(tasks))
    
    async def generate_single_async(self, text: str, voice_type: str = "BV001_streaming", task_id: Optional[str] = None) -> TaskResult:
        """
        Asynchronously generate TTS for a single text
        
        Args:
            text: Text to convert to speech
            voice_type: Voice type to use (default: BV001_streaming)
            task_id: Optional task ID (auto-generated if not provided)
            
        Returns:
            TaskResult with generated audio
        """
        if task_id is None:
            task_id = f"single_{hash(text) % 100000}"
        
        task = TaskItem(task_id=task_id, text=text, voice_type=voice_type)
        results = await self.generate_batch_async([task])
        return results[0] if results else TaskResult(task_id=task_id, audio_base64="")
    
    def generate_single_sync(self, text: str, voice_type: str = "BV001_streaming", task_id: Optional[str] = None) -> TaskResult:
        """
        Synchronously generate TTS for a single text
        
        Args:
            text: Text to convert to speech
            voice_type: Voice type to use (default: BV001_streaming)
            task_id: Optional task ID (auto-generated if not provided)
            
        Returns:
            TaskResult with generated audio
        """
        return asyncio.run(self.generate_single_async(text, voice_type, task_id))
    
    def get_audio_bytes(self, result: TaskResult) -> bytes:
        """
        Get audio bytes from a TaskResult
        
        Args:
            result: TaskResult containing base64 encoded audio
            
        Returns:
            Raw audio bytes
        """
        if not result.audio_base64:
            return b""
        return base64.b64decode(result.audio_base64)
    
    def save_audio_file(self, result: TaskResult, filename: str) -> bool:
        """
        Save audio from TaskResult to a file
        
        Args:
            result: TaskResult containing base64 encoded audio
            filename: Output filename (should end with .mp3)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            audio_bytes = self.get_audio_bytes(result)
            if not audio_bytes:
                return False
            
            with open(filename, 'wb') as f:
                f.write(audio_bytes)
            return True
        except Exception:
            return False


# Factory function for easier client creation
def create_client(app_id: str, access_key: str, secret_key: str, concurrency: int = 10) -> VolcengineConcurrentTTS:
    """
    Factory function to create a VolcengineConcurrentTTS client
    
    Args:
        app_id: Volcano Engine App ID
        access_key: Volcano Engine Access Key
        secret_key: Volcano Engine Secret Key
        concurrency: Maximum concurrent requests (default: 10)
        
    Returns:
        Initialized VolcengineConcurrentTTS client
    """
    return VolcengineConcurrentTTS(app_id, access_key, secret_key, concurrency)
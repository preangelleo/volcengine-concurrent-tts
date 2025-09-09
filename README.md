# Volcano Engine Concurrent TTS

A high-performance, self-hosted FastAPI application for concurrent text-to-speech generation using Volcano Engine's TTS API, featuring intelligent batch processing and concurrency management.

## Purpose and Use Cases

When developing with Volcano Engine's TTS API, developers face common challenges:

- **Concurrency Limits**: Most Volcano Engine TTS accounts have a maximum concurrency limit (typically ~10 concurrent requests)
- **Character-based Billing**: TTS services are billed per character, making efficient usage crucial
- **Multiple Projects**: When multiple applications under the same API account need TTS generation, managing concurrency becomes complex
- **API Rate Limiting**: Exceeding concurrency limits results in API errors and failed requests

**This application solves these problems by:**

🎯 **Maximizing Concurrency Utilization**: Efficiently uses your full concurrency quota without exceeding limits

🚦 **Built-in Queue Management**: Automatically queues requests when concurrency limit is reached, preventing API errors

🏢 **Multi-Project Support**: All your applications can use this single endpoint, sharing the concurrency pool intelligently

⚡ **High Efficiency**: Processes multiple TTS tasks concurrently while respecting API limitations

📊 **Cost Optimization**: Maximizes your API quota utilization for better cost-effectiveness

**Perfect for scenarios where:**
- You have multiple applications requiring TTS generation
- You want to maximize your Volcano Engine API concurrency quota
- You need reliable TTS processing without API limit errors
- You want centralized TTS processing for better resource management

## Features

- **Dual Usage Modes**: Use as a Python client library OR as a FastAPI server
- **Batch Processing**: Submit multiple TTS tasks in a single operation
- **Concurrency Control**: Intelligent queue management to respect API limits
- **Flexible Credentials**: API payload or environment variables with priority system
- **No Environment Required**: Can run without any .env file
- **Official Voice Support**: Supports all official Volcano Engine TTS voices
- **PyPI Package**: Install with pip for easy integration
- **Sync & Async Support**: Both synchronous and asynchronous APIs available

## Quick Start

### Prerequisites

- Python 3.8+
- Conda environment named `animagent`
- Valid Volcano Engine TTS API credentials

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd volcengine-concurrent-tts
   ```

2. **Activate conda environment and install dependencies:**
   ```bash
   conda activate animagent
   pip install -r requirements.txt
   ```

3. **Configure credentials (Optional):**
   
   **Option A - Environment Variables (Optional):**
   Create a `.env` file in the project root with:
   ```
   VOLCENGINE_TTS_APPID=your_app_id
   VOLCENGINE_TTS_ACCESS_KEY=your_access_key
   VOLCENGINE_TTS_SECRET_KEY=your_secret_key
   VOLCENGINE_TTS_CONCURRENCY=10
   ```
   
   **Option B - No Configuration Required:**
   Skip this step and provide credentials directly in API requests (see API Usage section).

### Running the Application

Start the FastAPI server:
```bash
conda activate animagent
python main.py
```

The application will be available at `http://localhost:8000`

### Testing

Run the test script to verify the application:
```bash
conda activate animagent
python test_volc_tts_logic.py
```

For detailed testing instructions, see `PRIVATE/TEST_GUIDE.md`

## Usage Modes

This application supports **two usage modes** with **different concurrency control behaviors**:

## 🚦 **Critical Concurrency Control Differences**

### 🌐 **Mode 1: FastAPI Server (GLOBAL Concurrency Control)**
**✅ Recommended for Multiple Applications/Users**

```bash
# Start the server - ALL requests share ONE global semaphore
python main.py
```

**🔒 Concurrency Behavior:**
- **Global Limit**: ALL requests across ALL applications share the same concurrency pool
- **Account Safe**: Total concurrent API calls NEVER exceed your Volcengine account limit
- **Example**: 10 applications × 20 requests each = 200 total requests, but only 10 run concurrently
- **Result**: ✅ No API limit violations, no 429 errors from Volcengine

```python
# Multiple applications can safely call the server simultaneously
# App 1: requests.post("http://server:8000/generate-batch", json={"tasks": [...]})
# App 2: requests.post("http://server:8000/generate-batch", json={"tasks": [...]})  
# App 3: requests.post("http://server:8000/generate-batch", json={"tasks": [...]})
# → Server ensures max 10 concurrent Volcengine API calls total
```

**Advantages:**
- ✅ **Account Protection**: Never exceeds API limits regardless of load
- ✅ Language-agnostic HTTP API
- ✅ Multiple applications can share safely
- ✅ Acts as a "gatekeeper" for your API quota
- ✅ Centralized concurrency management

**⚠️ Use This Mode When:**
- You have multiple applications using TTS
- You want to prevent API limit violations
- You need centralized quota management
- You have team members using the same API account

---

### 📦 **Mode 2: Direct Client (INDEPENDENT Concurrency Control)**
**✅ Recommended for Single Application Usage**

```python
from volcengine_client import VolcengineConcurrentTTS, TaskItem

# Each client instance manages its OWN concurrency independently
client1 = VolcengineConcurrentTTS(..., concurrency=10)  # Client 1: up to 10 concurrent
client2 = VolcengineConcurrentTTS(..., concurrency=10)  # Client 2: up to 10 concurrent  
client3 = VolcengineConcurrentTTS(..., concurrency=10)  # Client 3: up to 10 concurrent

# Async usage
results = await client1.generate_batch_async(tasks)

# Sync usage  
results = client2.generate_batch_sync(tasks)
```

**🔒 Concurrency Behavior:**
- **Independent Limits**: Each client instance has its own concurrency pool
- **Risk of Overload**: Multiple clients can exceed total account limits
- **Example**: 3 clients × 10 concurrent each = up to 30 concurrent API calls
- **Result**: ⚠️ Potential 429 errors if total exceeds your Volcengine account limit

**Advantages:**
- ✅ No server setup required
- ✅ Lower latency (no HTTP overhead)
- ✅ Direct Python integration  
- ✅ Both sync and async support
- ✅ Simpler for single-application use

**⚠️ Use This Mode When:**
- You have only ONE application using TTS
- You control all TTS usage in your system
- You want maximum performance for a single use case
- You can ensure total concurrency stays within limits

---

## 🎯 **Which Mode Should You Choose?**

| Scenario | Recommended Mode | Reason |
|----------|------------------|---------|
| **Multiple apps/users** | 🌐 **FastAPI Server** | Global concurrency control prevents API limit violations |
| **Team development** | 🌐 **FastAPI Server** | Centralized quota management, no conflicts |
| **Production deployment** | 🌐 **FastAPI Server** | Account protection, better resource management |
| **Single Python app** | 📦 **Direct Client** | Simpler integration, lower latency |
| **Prototyping/testing** | 📦 **Direct Client** | Faster setup, direct control |

## ⚡ **Quick Start Examples**

### 🌐 FastAPI Server Mode
```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Use from any language
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [{"task_id": "test", "text": "Hello world", "voice_type": "BV001_streaming"}],
    "credentials": {
      "volcengine_tts_appid": "your_app_id",
      "volcengine_tts_access_key": "your_access_key",
      "volcengine_tts_secret_key": "your_secret_key"
    }
  }'
```

### 📦 Direct Client Mode
```python
from volcengine_client import VolcengineConcurrentTTS, TaskItem

client = VolcengineConcurrentTTS(
    app_id="your_app_id",
    access_key="your_access_key", 
    secret_key="your_secret_key",
    concurrency=10  # This client's individual limit
)

tasks = [TaskItem("task1", "Hello world", "BV001_streaming")]
results = await client.generate_batch_async(tasks)
```

### 📦 Installation

**Option 1: Install from PyPI (when published):**
```bash
pip install volcengine-concurrent-tts
```

**Option 2: Install from source:**
```bash
git clone <repository-url>
cd volcengine-concurrent-tts
pip install -e .

# Install with server dependencies
pip install -e .[server]
```

**Option 3: Use without installation:**
Just download the files and import directly:
```python
from volcengine_client import VolcengineConcurrentTTS
```

## API Usage (Mode 2: FastAPI Server)

Send a `POST` request to the `/generate-batch` endpoint.

**Endpoint**: `POST /generate-batch`

### Credential Priority System

The application supports flexible credential management with the following priority:

1. **API Request Credentials** (Highest Priority) - Provided in request payload
2. **Environment Variables** (Medium Priority) - From `.env` file
3. **Error** (Lowest Priority) - Missing credentials will return error

### Usage Examples

**Example 1 - Using Environment Variables (.env file):**

```json
{
  "tasks": [
    {
      "task_id": "scene_01",
      "text": "Hello, this is a test.",
      "voice_type": "en_male_jason_conversation_wvae_bigtts"
    }
  ]
}
```

**Example 2 - Using API Request Credentials (No .env required):**

```json
{
  "tasks": [
    {
      "task_id": "scene_01",
      "text": "Hello, this is a test.",
      "voice_type": "en_male_jason_conversation_wvae_bigtts"
    }
  ],
  "credentials": {
    "volcengine_tts_appid": "your_app_id",
    "volcengine_tts_access_key": "your_access_key",
    "volcengine_tts_secret_key": "your_secret_key",
    "volcengine_tts_concurrency": 15
  }
}
```

**Example 3 - Mixed Mode (Override specific credentials):**

```json
{
  "tasks": [
    {
      "task_id": "scene_01", 
      "text": "Hello, this is a test.",
      "voice_type": "BV001_streaming"
    }
  ],
  "credentials": {
    "volcengine_tts_concurrency": 20
  }
}
```

### Request Parameters

**tasks** (required):
- `task_id`: Unique identifier for the task
- `text`: The text to be converted to speech (supports multiple languages)  
- `voice_type`: The desired official voice ID. Examples:
  - Official voices: `BV001_streaming`, `en_male_jason_conversation_wvae_bigtts`, `zh_female_qingxin_conversation`, `BV002_streaming`

**credentials** (optional):
- `volcengine_tts_appid`: Your Volcano Engine App ID
- `volcengine_tts_access_key`: Your Volcano Engine Access Key
- `volcengine_tts_secret_key`: Your Volcano Engine Secret Key
- `volcengine_tts_concurrency`: Maximum concurrent requests (default: 10)

**Success Response Example**:

The API will return a list of results, each containing the `task_id` and the base64-encoded audio data.

```json
{
  "results": [
    {
      "task_id": "scene_01",
      "audio_base64": "..."
    },
    {
      "task_id": "scene_02",
      "audio_base64": "..."
    }
  ]
}
```

## Client API Reference (Mode 1)

### VolcengineConcurrentTTS Class

#### Constructor
```python
client = VolcengineConcurrentTTS(app_id, access_key, secret_key, concurrency=10)
```

**Parameters:**
- `app_id` (str): Your Volcano Engine App ID
- `access_key` (str): Your Volcano Engine Access Key  
- `secret_key` (str): Your Volcano Engine Secret Key
- `concurrency` (int, optional): Maximum concurrent requests (default: 10)

#### Methods

##### Batch Generation

```python
# Asynchronous batch generation (recommended)
results = await client.generate_batch_async(tasks: List[TaskItem]) -> List[TaskResult]

# Synchronous batch generation
results = client.generate_batch_sync(tasks: List[TaskItem]) -> List[TaskResult]
```

##### Single Generation

```python
# Asynchronous single generation
result = await client.generate_single_async(
    text: str, 
    voice_type: str = "BV001_streaming", 
    task_id: Optional[str] = None
) -> TaskResult

# Synchronous single generation  
result = client.generate_single_sync(
    text: str,
    voice_type: str = "BV001_streaming",
    task_id: Optional[str] = None
) -> TaskResult
```

##### Utility Methods

```python
# Get raw audio bytes from result
audio_bytes = client.get_audio_bytes(result: TaskResult) -> bytes

# Save audio to file
success = client.save_audio_file(result: TaskResult, filename: str) -> bool
```

### Data Classes

#### TaskItem
```python
task = TaskItem(
    task_id="unique_id",
    text="Text to synthesize", 
    voice_type="BV001_streaming",
    output_filename="optional_filename"  # Optional
)
```

#### TaskResult
```python
# TaskResult attributes:
result.task_id          # str: Task identifier
result.audio_base64     # str: Base64 encoded audio data
result.to_dict()        # dict: Convert to dictionary
```

### Factory Function

```python
# Alternative way to create client
from volcengine_client import create_client

client = create_client(app_id, access_key, secret_key, concurrency=10)
```

## Testing Both Modes

Run the comprehensive test script to see both usage modes in action:

```bash
python test_client_usage.py
```

This script demonstrates:
- Direct client usage with various methods
- FastAPI server usage with HTTP requests  
- Performance comparison between modes
- Installation and setup instructions

## Error Handling

### Direct Client Mode
```python
try:
    results = await client.generate_batch_async(tasks)
    for result in results:
        if result.audio_base64:
            print(f"✅ {result.task_id}: Success")
        else:
            print(f"❌ {result.task_id}: Failed (empty audio)")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Generation error: {e}")
```

### FastAPI Server Mode
HTTP status codes indicate success/failure:
- `200`: Success with audio data
- `400`: Missing or invalid credentials
- `422`: Invalid request format
- `500`: Internal server error
```
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

- **Batch Processing**: Submit multiple TTS tasks in a single API call.
- **Concurrency Control**: Manages a queue to not exceed the API concurrency limit set in your Volcano Engine account.
- **Easy to Deploy**: Run as a standard FastAPI application.
- **Flexible Credentials**: Supports credentials via API payload or environment variables with priority system.
- **No Environment Required**: Can run without any .env file - just provide credentials in API requests.
- **Official Voice Support**: Supports all official Volcano Engine TTS voices.

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

## API Usage

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
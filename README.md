# Volcano Engine Concurrent TTS v2.0

A next-generation, high-performance FastAPI application for concurrent text-to-speech generation using Volcano Engine's TTS API, featuring **External Semaphore Pattern**, **Perfect Input/Output Correspondence**, and **Advanced Cross-Service Coordination**.

## 🚀 What's New in v2.0

### ✨ **External Semaphore Pattern**
- **Cross-service concurrency control** - Share concurrency limits across multiple services
- **Global semaphore registry** - Centralized management of external semaphores
- **Admin-only semaphore creation** - Secure semaphore lifecycle management
- **Zero-conflict coordination** - Multiple services can share the same concurrency pool

### 🎯 **Perfect Input/Output Correspondence**
- **Task index mapping** - Maintains exact order correspondence between input and output
- **Enhanced TaskItem structure** - Support for `prompt` (renamed from `text`) and `output_filename`
- **Structured results** - Each result includes task_index, original prompt, and generated files
- **Batch processing integrity** - No more lost or mismatched results in concurrent processing

### 🏗️ **Advanced Architecture Design**
- **List of Dictionaries format** - Consistent with Replicate's advanced design patterns
- **3-tier authentication** - Admin API Key → User Credentials → Environment Variables
- **Enhanced health monitoring** - Comprehensive service status reporting
- **Backward compatibility** - Legacy endpoints still supported

## Purpose and Use Cases

When developing with Volcano Engine's TTS API, developers face common challenges:

- **Concurrency Limits**: Most Volcano Engine TTS accounts have a maximum concurrency limit (typically ~10 concurrent requests)
- **Character-based Billing**: TTS services are billed per character, making efficient usage crucial
- **Multiple Projects**: When multiple applications under the same API account need TTS generation, managing concurrency becomes complex
- **Cross-Service Coordination**: Need to share concurrency limits across different microservices
- **API Rate Limiting**: Exceeding concurrency limits results in API errors and failed requests

**This v2.0 application solves these problems by:**

🎯 **Maximizing Concurrency Utilization**: Efficiently uses your full concurrency quota without exceeding limits

🚦 **Built-in Queue Management**: Automatically queues requests when concurrency limit is reached, preventing API errors

🏢 **Multi-Service Support**: All your microservices can share the same concurrency pool through External Semaphore Pattern

⚡ **High Efficiency**: Processes multiple TTS tasks concurrently while respecting API limitations

📊 **Cost Optimization**: Maximizes your API quota utilization for better cost-effectiveness

🔗 **Cross-Service Coordination**: Share concurrency limits across multiple services and applications

**Perfect for scenarios where:**
- You have multiple microservices requiring TTS generation
- You want to maximize your Volcano Engine API concurrency quota across services
- You need reliable TTS processing without API limit errors
- You want centralized concurrency management for better resource coordination
- You need perfect input/output correspondence in batch processing

## Features

### v2.0 Enhanced Features
- **🔗 External Semaphore Pattern**: Cross-service concurrency sharing
- **📊 Perfect Input/Output Correspondence**: Exact task index mapping
- **🏗️ Advanced Architecture**: List of dictionaries format matching Replicate design
- **🔐 Enhanced Authentication**: 3-tier security system
- **📈 Comprehensive Monitoring**: Detailed service health and status reporting
- **🔄 Backward Compatibility**: Legacy API endpoints still supported

### Core Features
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
- Valid Volcano Engine TTS API credentials

### Installation

1. **Clone and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd volcengine-concurrent-tts
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure credentials (Optional):**
   
   **Option A - Environment Variables (Optional):**
   Create a `.env` file in the project root with:
   ```env
   VOLCENGINE_TTS_APPID=your_app_id
   VOLCENGINE_TTS_ACCESS_KEY=your_access_key
   VOLCENGINE_TTS_CONCURRENCY=10
   ```
   
   **Option B - Admin API Key (Recommended for Production):**
   For internal services and production deployments, configure an Admin API Key:
   ```env
   # Add to your .env file
   ADMIN_API_KEY=your_custom_admin_key_here
   VOLCENGINE_TTS_APPID=your_app_id
   VOLCENGINE_TTS_ACCESS_KEY=your_access_key
   VOLCENGINE_TTS_CONCURRENCY=10
   ```
   
   With Admin API Key configured, internal services can authenticate using the `Admin-API-Key` header without exposing individual API credentials in requests.
   
   **Option C - No Configuration Required:**
   Skip this step and provide credentials directly in API requests (see API Usage section).

### Running the Application

**Method 1 - Direct Python execution (Development):**
```bash
python main_v2_upgraded.py
```

**Method 2 - Using uvicorn directly:**
```bash
uvicorn main_v2_upgraded:app --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000`

### Testing v2.0 Features

**Health Check (Enhanced v2.0):**
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
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
    "global_concurrency_limit": 10,
    "current_available_slots": 10,
    "external_semaphores_count": 0
  }
}
```

## v2.0 API Usage

### Enhanced Batch Generation API

**Endpoint**: `POST /generate-batch`

**v2.0 Enhanced Request Format (List of Dictionaries):**

```json
{
  "tasks": [
    {
      "prompt": "Hello, this is a test message.",
      "output_filename": "test_audio_001.mp3",
      "voice_type": "en_male_jason_conversation_wvae_bigtts"
    },
    {
      "prompt": "This is another test message.",
      "output_filename": "test_audio_002.mp3",
      "voice_type": "BV001_streaming"
    }
  ],
  "credentials": {
    "volcengine_tts_appid": "your_app_id",
    "volcengine_tts_access_key": "your_access_key"
  }
}
```

**v2.0 Enhanced Response Format (Perfect Correspondence):**

```json
{
  "results": [
    {
      "task_index": 0,
      "prompt": "Hello, this is a test message.",
      "output_filename": "test_audio_001.mp3",
      "generated_files": [
        {
          "filename": "test_audio_001.mp3",
          "url": "data:audio/mp3;base64,UklGRnoGAABXQVZFZm10IBAAAA...",
          "format": "mp3"
        }
      ],
      "success": true
    },
    {
      "task_index": 1,
      "prompt": "This is another test message.",
      "output_filename": "test_audio_002.mp3",
      "generated_files": [
        {
          "filename": "test_audio_002.mp3",
          "url": "data:audio/mp3;base64,UklGRnoGAABXQVZFZm10IBAAAA...",
          "format": "mp3"
        }
      ],
      "success": true
    }
  ]
}
```

### External Semaphore Pattern (v2.0 Feature)

**Create External Semaphore** (Admin only):
```bash
curl -X POST http://localhost:8000/external-semaphores \
  -H "Admin-API-Key: your_admin_key" \
  -H "Content-Type: application/json" \
  -d '{
    "semaphore_id": "shared-tts-pool",
    "max_concurrent": 10,
    "description": "Shared TTS semaphore across services"
  }'
```

**Use External Semaphore in Batch Generation:**
```json
{
  "tasks": [
    {
      "prompt": "Test with external semaphore",
      "output_filename": "test.mp3"
    }
  ],
  "external_semaphore_id": "shared-tts-pool",
  "credentials": {
    "volcengine_tts_appid": "your_app_id",
    "volcengine_tts_access_key": "your_access_key"
  }
}
```

### Authentication Methods (3-Tier System)

**Tier 1 - Admin API Key (Highest Priority):**
```bash
curl -X POST http://localhost:8000/generate-batch \
  -H "Admin-API-Key: your_admin_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "prompt": "Admin authenticated request",
        "output_filename": "admin_test.mp3"
      }
    ]
  }'
```

**Tier 2 - User Credentials in Payload:**
```json
{
  "tasks": [...],
  "credentials": {
    "volcengine_tts_appid": "user_app_id",
    "volcengine_tts_access_key": "user_access_key"
  }
}
```

**Tier 3 - Environment Variables:**
```bash
# With .env file configured
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{"tasks": [...]}'
```

## Legacy API Support (Backward Compatibility)

**Legacy Format Still Supported:**
```json
{
  "tasks": [
    {
      "task_id": "test_1",
      "text": "Hello world",
      "voice_type": "BV001_streaming"
    }
  ]
}
```

**Legacy Response Format:**
```json
{
  "results": [
    {
      "task_id": "test_1",
      "audio_base64": "UklGRnoGAABXQVZFZm10IBAAAA..."
    }
  ]
}
```

## Docker Deployment v2.0

### Docker Hub Repository
🐳 **Official Docker Image**: [`betashow/volcengine-concurrent-tts:latest`](https://hub.docker.com/repository/docker/betashow/volcengine-concurrent-tts/general)

### Quick Docker Usage
```bash
# Pull the latest v2.0 image
docker pull betashow/volcengine-concurrent-tts:latest

# Run with environment variables
docker run -d \
  --name volcengine-tts-v2 \
  -p 8000:8000 \
  -e VOLCENGINE_TTS_APPID=your_app_id \
  -e VOLCENGINE_TTS_ACCESS_KEY=your_access_key \
  -e VOLCENGINE_TTS_CONCURRENCY=10 \
  -e ADMIN_API_KEY=your_admin_key \
  betashow/volcengine-concurrent-tts:latest

# Verify v2.0 deployment
curl http://localhost:8000/
```

### Production Deployment (v2.0 Enhanced)

**Environment Configuration:**
```env
# Core TTS Configuration
VOLCENGINE_TTS_APPID=your_app_id
VOLCENGINE_TTS_ACCESS_KEY=your_access_key
VOLCENGINE_TTS_CONCURRENCY=10

# v2.0 Enhanced Features
ADMIN_API_KEY=your_secure_admin_key

# Production Settings
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_DEBUG=false
```

**Production Features:**
- ✅ **External Semaphore Support** - Cross-service coordination
- ✅ **Perfect Input/Output Correspondence** - Enhanced batch processing
- ✅ **3-Tier Authentication** - Secure credential management
- ✅ **Health Monitoring** - Comprehensive service status
- ✅ **Backward Compatibility** - Legacy API support
- ✅ **Container Health Checks** - Built-in for orchestration

## Architecture Comparison

### v1.0 vs v2.0 Architecture

| Feature | v1.0 | v2.0 Enhanced |
|---------|------|---------------|
| **Concurrency Control** | Local semaphore only | ✅ Local + External Semaphore Pattern |
| **Input/Output Mapping** | Basic task_id mapping | ✅ Perfect correspondence with task_index |
| **Data Format** | Simple key-value | ✅ List of dictionaries (Replicate-style) |
| **Cross-Service Support** | No | ✅ External semaphore sharing |
| **Authentication** | 2-tier (payload/env) | ✅ 3-tier (admin/payload/env) |
| **Monitoring** | Basic health check | ✅ Comprehensive status reporting |
| **Backward Compatibility** | N/A | ✅ Full legacy API support |

### External Semaphore Pattern Benefits

1. **Cross-Service Coordination**: Multiple microservices can share the same concurrency pool
2. **Global Resource Management**: Centralized control over API usage across services
3. **Zero-Conflict Processing**: Services coordinate automatically without manual intervention
4. **Scalable Architecture**: Add/remove services without reconfiguring concurrency limits
5. **Admin-Controlled**: Secure semaphore lifecycle management with admin authentication

## Performance & Monitoring

### v2.0 Enhanced Monitoring

**Service Status Endpoint:**
```bash
curl http://localhost:8000/
```

**Comprehensive Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0-external-semaphore-enhanced",
  "architecture": {
    "external_semaphore_pattern": "✅ Enabled",
    "perfect_input_output_correspondence": "✅ Enabled",
    "advanced_batch_processing": "✅ Enabled"
  },
  "concurrency_status": {
    "global_concurrency_limit": 10,
    "current_available_slots": 8,
    "external_semaphores_count": 2
  },
  "authentication": {
    "admin_api_key": "✅ Configured",
    "user_credentials": "✅ Supported",
    "environment_variables": "✅ Fallback"
  }
}
```

### Performance Optimization

- **Perfect Correspondence**: Eliminates result sorting overhead
- **External Semaphore**: Reduces coordination latency between services
- **Advanced Batching**: Optimized for high-throughput scenarios
- **Efficient Memory Usage**: Streaming audio processing with cleanup

## Migration Guide (v1.0 → v2.0)

### API Changes
1. **New Enhanced Format**: Use `prompt` instead of `text`, add `output_filename`
2. **Legacy Support**: Old format still works (backward compatibility)
3. **Enhanced Response**: New response includes `task_index` and `generated_files`

### Code Migration Example

**v1.0 Format (Still Supported):**
```json
{
  "tasks": [
    {"task_id": "1", "text": "Hello", "voice_type": "BV001_streaming"}
  ]
}
```

**v2.0 Enhanced Format (Recommended):**
```json
{
  "tasks": [
    {"prompt": "Hello", "output_filename": "hello.mp3", "voice_type": "BV001_streaming"}
  ]
}
```

### Docker Migration
```bash
# Pull v2.0 image
docker pull betashow/volcengine-concurrent-tts:latest

# Stop v1.0 container
docker stop volcengine-tts

# Start v2.0 container
docker run -d --name volcengine-tts-v2 \
  -p 8000:8000 \
  --env-file .env \
  betashow/volcengine-concurrent-tts:latest
```

## Error Handling

### Enhanced v2.0 Error Responses

**Authentication Error:**
```json
{
  "detail": "Authentication failed. Provide 'Admin-API-Key' in headers or complete credentials in payload.",
  "error_code": "AUTH_FAILED",
  "suggested_action": "Check your Admin-API-Key header or credentials in payload"
}
```

**External Semaphore Error:**
```json
{
  "detail": "External semaphore 'shared-pool' not found or access denied.",
  "error_code": "SEMAPHORE_NOT_FOUND",
  "available_semaphores": ["default-pool", "premium-pool"]
}
```

### HTTP Status Codes
- `200`: Success with audio data
- `400`: Missing or invalid credentials
- `401`: Authentication failed
- `403`: Access denied (admin required)
- `404`: External semaphore not found
- `422`: Invalid request format
- `500`: Internal server error

## Testing

### v2.0 Feature Testing

**Test External Semaphore Pattern:**
```bash
# Create external semaphore (admin required)
curl -X POST http://localhost:8000/external-semaphores \
  -H "Admin-API-Key: your_admin_key" \
  -d '{"semaphore_id": "test-pool", "max_concurrent": 5}'

# Use external semaphore
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [{"prompt": "Test", "output_filename": "test.mp3"}],
    "external_semaphore_id": "test-pool",
    "credentials": {"volcengine_tts_appid": "...", "volcengine_tts_access_key": "..."}
  }'
```

**Test Perfect Correspondence:**
```bash
# Submit multiple tasks and verify task_index mapping
curl -X POST http://localhost:8000/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {"prompt": "First", "output_filename": "first.mp3"},
      {"prompt": "Second", "output_filename": "second.mp3"},
      {"prompt": "Third", "output_filename": "third.mp3"}
    ],
    "credentials": {"volcengine_tts_appid": "...", "volcengine_tts_access_key": "..."}
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/v2-enhancement`)
3. Commit your changes (`git commit -am 'Add v2.0 feature'`)
4. Push to the branch (`git push origin feature/v2-enhancement`)
5. Create a Pull Request

## License

[Your License Here]

## Changelog

### v2.0.0 (2025-09-10)
- ✅ **Added**: External Semaphore Pattern for cross-service coordination
- ✅ **Added**: Perfect Input/Output Correspondence with task_index mapping
- ✅ **Added**: Advanced architecture matching Replicate design patterns
- ✅ **Added**: 3-tier authentication system (Admin → User → Environment)
- ✅ **Enhanced**: Health monitoring with comprehensive status reporting
- ✅ **Enhanced**: Docker deployment with v2.0 features
- ✅ **Maintained**: Full backward compatibility with v1.0 API

### v1.0.0
- Initial release with basic concurrent TTS processing
- Local semaphore-based concurrency control
- FastAPI server and direct client modes
- Docker support
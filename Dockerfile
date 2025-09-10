# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY main_v2_upgraded.py .
COPY volcengine_client.py .
COPY volc_tts.py .
COPY setup.py .

# Create .env.example for reference (no actual credentials)
COPY .env.example .

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VOLCENGINE_TTS_CONCURRENCY=10

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)"

# Run the FastAPI application
CMD ["python", "main_v2_upgraded.py"]
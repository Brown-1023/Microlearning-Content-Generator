# Backend Dockerfile for the Microlearning Content Generator API
# This creates a container for the Python FastAPI backend with streaming support

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies AND gunicorn for production
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn uvicorn[standard]

# Copy application code
COPY . .

# Create necessary directories for prompts and config
RUN mkdir -p /app/prompts /app/config /app/samples

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

# Default environment variables (can be overridden at runtime)
ENV MAX_FORMATTER_RETRIES=1
ENV MODEL_TEMPERATURE=0.51
ENV MODEL_TOP_P=0.95
ENV MODEL_TIMEOUT=300
ENV MAX_REQUEST_SIZE_MB=10
ENV RATE_LIMIT_REQUESTS=10
ENV RATE_LIMIT_PERIOD=minute

# Health check to ensure the service is running (uses PORT env)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", \"8080\")}/healthz')" || exit 1

# Expose the API port
EXPOSE 8080

# Run with gunicorn for production (fallback to python run.py for dev)
CMD if [ -f gunicorn.conf.py ]; then exec gunicorn app:app --config gunicorn.conf.py; else exec python run.py; fi

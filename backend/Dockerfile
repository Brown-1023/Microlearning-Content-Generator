# Backend-only Dockerfile for the Microlearning Content Generator API
# This creates a lightweight container for the Python FastAPI backend

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories for prompts and config
RUN mkdir -p /app/prompts /app/config /app/samples

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=4000

# Default environment variables (can be overridden at runtime)
ENV MAX_FORMATTER_RETRIES=1
ENV MODEL_TEMPERATURE=0.51
ENV MODEL_TOP_P=0.95
ENV MODEL_MAX_TOKENS=8000
ENV MODEL_TIMEOUT=300
ENV MAX_REQUEST_SIZE_MB=10
ENV RATE_LIMIT_REQUESTS=10
ENV RATE_LIMIT_PERIOD=minute

# Health check to ensure the service is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/healthz')" || exit 1

# Expose the API port
EXPOSE 4000

# Run the application
CMD ["python", "run.py"]

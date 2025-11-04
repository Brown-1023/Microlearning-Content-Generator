#!/bin/bash

# Emergency fix and deploy script
set -e

echo "🔧 Fixing port configuration and deploying..."

# Configuration
PROJECT_ID="reviewbytes-microlearning"
REGION="us-central1"
SERVICE_NAME="reviewbytes-app"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/containers/${SERVICE_NAME}"
SERVICE_ACCOUNT="run-runtime@${PROJECT_ID}.iam.gserviceaccount.com"

echo "📦 Building with production fixes..."

# Create a temporary Dockerfile with fixes
cat > Dockerfile.fixed << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies AND gunicorn
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn uvicorn[standard]

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

# IMPORTANT: Override the default port from config.py
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", \"8080\")}/healthz')" || exit 1

# Expose port 8080 (Cloud Run standard)
EXPOSE 8080

# Use gunicorn for production
CMD exec gunicorn app:app --config gunicorn.conf.py
EOF

# Build with the fixed Dockerfile
echo "🔨 Building Docker image with fixes..."
sudo docker build -f Dockerfile.fixed -t ${IMAGE_NAME}:fixed .

# Push to registry
echo "⬆️ Pushing fixed image..."
docker push ${IMAGE_NAME}:fixed

# Deploy with all necessary environment variables
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:fixed \
  --region ${REGION} \
  --service-account ${SERVICE_ACCOUNT} \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 100 \
  --min-instances 0 \
  --concurrency 1000 \
  --no-cpu-throttling \
  --execution-environment gen2 \
  --set-env-vars "PORT=8080,PYTHONUNBUFFERED=1,WEB_CONCURRENCY=4" \
  --allow-unauthenticated

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "🔗 Service URL: ${SERVICE_URL}"
echo ""
echo "📝 Next steps:"
echo "1. Update your frontend with this backend URL"
echo "2. Set CORS if needed: gcloud run services update ${SERVICE_NAME} --update-env-vars CORS_ALLOW_ALL=true --region ${REGION}"

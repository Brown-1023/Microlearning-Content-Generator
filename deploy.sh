#!/bin/bash

# Google Cloud Run Deployment Script

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
SERVICE_NAME="microlearning-generator"
REGION=${GCP_REGION:-"us-central1"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Deploying to Google Cloud Run"
echo "=============================="
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Check for required environment variables
if [ -z "$GOOGLE_API_KEY" ] || [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: Missing required API keys"
    echo "Please set GOOGLE_API_KEY and ANTHROPIC_API_KEY"
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

# Push to Container Registry
echo "Pushing to Container Registry..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8000 \
    --allow-unauthenticated \
    --set-env-vars "MAX_FORMATTER_RETRIES=1" \
    --set-secrets "GOOGLE_API_KEY=google-api-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest,EDITOR_PASSWORD=editor-password:latest,APP_SECRET=app-secret:latest" \
    --project ${PROJECT_ID}

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --format 'value(status.url)')

echo ""
echo "Deployment Complete!"
echo "===================="
echo "Service URL: ${SERVICE_URL}"
echo ""
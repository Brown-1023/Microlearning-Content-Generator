# Cloud Run Deployment Guide

This application is designed to run as a **single container on Google Cloud Run**, serving both the UI and API as specified in Milestone 2 requirements.

## Prerequisites

1. Google Cloud Project with billing enabled
2. APIs enabled:
   - Cloud Run API
   - Cloud Build API
   - Secret Manager API
   - Container Registry API
3. gcloud CLI installed and configured

## Setup Secrets

Create required secrets in Google Secret Manager:

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Create API key secrets
echo -n "your-google-api-key" | gcloud secrets create google-api-key --data-file=-
echo -n "your-anthropic-api-key" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "your-editor-password" | gcloud secrets create editor-password --data-file=-
```

## Deploy with Cloud Build

### One-time setup

```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create service account for Cloud Run
gcloud iam service-accounts create microlearning-sa \
  --display-name="Microlearning Generator Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Deploy

```bash
# Submit build and deploy
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_SERVICE_ACCOUNT=microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Manual Deployment

### Build and push Docker image

```bash
# Build the single container image
docker build -t gcr.io/$PROJECT_ID/microlearning-generator:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/microlearning-generator:latest
```

### Deploy to Cloud Run

```bash
gcloud run deploy microlearning-generator \
  --image gcr.io/$PROJECT_ID/microlearning-generator:latest \
  --region us-central1 \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 100 \
  --min-instances 0 \
  --max-instances 10 \
  --port 8080 \
  --allow-unauthenticated \
  --set-secrets="GOOGLE_API_KEY=google-api-key:latest" \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-secrets="EDITOR_PASSWORD=editor-password:latest" \
  --set-env-vars="APP_SECRET=your-app-secret" \
  --set-env-vars="MAX_FORMATTER_RETRIES=1" \
  --set-env-vars="MODEL_TEMPERATURE=0.51" \
  --set-env-vars="MODEL_TOP_P=0.95" \
  --set-env-vars="PORT=4000" \
  --set-env-vars="NEXT_PUBLIC_API_URL=http://localhost:4000" \
  --service-account=microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Configure Identity-Aware Proxy (IAP)

For production, enable IAP as mentioned in requirements:

```bash
# Enable IAP API
gcloud services enable iap.googleapis.com

# Configure OAuth consent screen
# (Must be done in Cloud Console)

# Enable IAP for Cloud Run service
gcloud iap web enable \
  --resource-type=backend-services \
  --oauth2-client-id=YOUR_CLIENT_ID \
  --oauth2-client-secret=YOUR_CLIENT_SECRET

# Add authorized users
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:editor@example.com" \
  --role="roles/iap.httpsResourceAccessor"

# Update Cloud Run to require authentication
gcloud run services update microlearning-generator \
  --no-allow-unauthenticated \
  --region us-central1
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI Studio API key | Yes |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Yes |
| `APP_SECRET` | Secret for session cookies | Yes |
| `EDITOR_PASSWORD` | Password for basic auth | Yes (until IAP) |
| `MAX_FORMATTER_RETRIES` | Max formatter retries | No (default: 1) |
| `MODEL_TEMPERATURE` | LLM temperature | No (default: 0.51) |
| `MODEL_TOP_P` | LLM top_p parameter | No (default: 0.95) |

## Local Testing

### With Docker

```bash
# Build the container
docker build -t microlearning-generator .

# Run locally
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY="your-key" \
  -e ANTHROPIC_API_KEY="your-key" \
  -e EDITOR_PASSWORD="password" \
  -e APP_SECRET="secret" \
  microlearning-generator
```

### With Docker Compose

```bash
# Copy environment file
cp backend/env.example .env
# Edit .env with your keys

# Run with docker-compose
docker-compose up
```

## Access the Application

After deployment, the application will be available at:
- Cloud Run URL: `https://microlearning-generator-xxxxx-uc.a.run.app`
- Frontend UI: Main URL
- API Docs: `/docs`
- Health Check: `/healthz`
- Version Info: `/version`

## Monitoring

View logs and metrics:

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=microlearning-generator" \
  --limit 50

# View metrics in Cloud Console
open https://console.cloud.google.com/run/detail/us-central1/microlearning-generator/metrics
```

## Security Notes

1. **Secrets**: Always use Secret Manager, never hardcode
2. **IAP**: Enable for production environments
3. **CORS**: Automatically handled since UI and API are in same container
4. **Rate Limiting**: Configured in application (10 requests/minute)
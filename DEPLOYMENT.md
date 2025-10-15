# Cloud Run Deployment Guide

This guide covers deploying the Microlearning Content Generator to Google Cloud Run.

## Prerequisites

1. Google Cloud Project with billing enabled
2. APIs enabled:
   - Cloud Run API
   - Cloud Build API
   - Secret Manager API
   - Container Registry API
3. gcloud CLI installed and configured
4. Required secrets created in Secret Manager

## Setup Secrets

First, create the required secrets in Google Secret Manager:

```bash
# Create API key secrets
echo -n "your-google-api-key" | gcloud secrets create google-api-key --data-file=-
echo -n "your-anthropic-api-key" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "your-editor-password" | gcloud secrets create editor-password --data-file=-
```

## Deploy Using Cloud Build

### 1. One-time setup

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create a service account for Cloud Run
gcloud iam service-accounts create microlearning-sa \
  --display-name="Microlearning Generator Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 2. Deploy with Cloud Build

```bash
# Submit build (replace with your values)
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_SERVICE_ACCOUNT=microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Manual Deployment

If you prefer to deploy manually:

### 1. Build and push Docker image

```bash
# Build the image
docker build -t gcr.io/$PROJECT_ID/microlearning-generator:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/microlearning-generator:latest
```

### 2. Deploy to Cloud Run

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
  --port 8000 \
  --allow-unauthenticated \
  --set-secrets="GOOGLE_API_KEY=google-api-key:latest" \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-secrets="EDITOR_PASSWORD=editor-password:latest" \
  --set-env-vars="APP_SECRET=your-app-secret" \
  --set-env-vars="MAX_FORMATTER_RETRIES=1" \
  --set-env-vars="MODEL_TEMPERATURE=0.51" \
  --set-env-vars="MODEL_TOP_P=0.95" \
  --set-env-vars="MAX_REQUEST_SIZE_MB=10" \
  --service-account=microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Configure Identity-Aware Proxy (IAP)

For production, enable IAP instead of password authentication:

### 1. Reserve external IP and configure domain

```bash
# Reserve a static IP
gcloud compute addresses create microlearning-ip --global

# Get the IP address
gcloud compute addresses describe microlearning-ip --global
```

### 2. Configure Cloud Load Balancer with IAP

```bash
# Create backend service
gcloud compute backend-services create microlearning-backend \
  --global \
  --load-balancing-scheme=EXTERNAL \
  --protocol=HTTP

# Add Cloud Run service as backend
gcloud compute backend-services add-backend microlearning-backend \
  --global \
  --network-endpoint-group=microlearning-generator-neg \
  --network-endpoint-group-region=us-central1
```

### 3. Enable IAP

```bash
# Enable IAP for the backend service
gcloud iap web enable \
  --resource-type=backend-services \
  --service=microlearning-backend

# Add IAP users
gcloud iap web add-iam-policy-binding \
  --resource-type=backend-services \
  --service=microlearning-backend \
  --member='user:editor@example.com' \
  --role='roles/iap.httpsResourceAccessor'
```

### 4. Update application configuration

Once IAP is enabled:
1. Remove `EDITOR_PASSWORD` from environment variables
2. Update frontend to remove password login
3. Set `--no-allow-unauthenticated` flag in Cloud Run

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI Studio API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Required |
| `APP_SECRET` | Secret for session cookies | Required |
| `EDITOR_PASSWORD` | Password for basic auth | Optional (use IAP instead) |
| `MAX_FORMATTER_RETRIES` | Max retries for formatter | 1 |
| `MODEL_TEMPERATURE` | LLM temperature parameter | 0.51 |
| `MODEL_TOP_P` | LLM top_p parameter | 0.95 |
| `MODEL_MAX_TOKENS` | Max tokens for generation | 8000 |
| `MAX_REQUEST_SIZE_MB` | Max request size in MB | 10 |
| `MAX_INPUT_CHARS` | Max input text characters | 150000 |

## Monitoring

View logs and metrics:

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=microlearning-generator" \
  --limit 50 \
  --format json

# View metrics in Cloud Console
open https://console.cloud.google.com/run/detail/us-central1/microlearning-generator/metrics
```

## Rollback

If needed, rollback to a previous revision:

```bash
# List revisions
gcloud run revisions list --service microlearning-generator --region us-central1

# Rollback to specific revision
gcloud run services update-traffic microlearning-generator \
  --to-revisions=microlearning-generator-00001-abc=100 \
  --region us-central1
```

## Security Best Practices

1. **Never commit secrets** - Use Secret Manager
2. **Enable IAP** for production environments
3. **Use least-privilege service accounts**
4. **Enable VPC Service Controls** for additional security
5. **Set up monitoring alerts** for suspicious activity
6. **Regular security audits** of dependencies
7. **Configure CORS strictly** for production
8. **Enable Cloud Armor** for DDoS protection

## Cost Optimization

1. Set minimum instances to 0 for development
2. Use Cloud Scheduler to warm up instances before peak hours
3. Monitor and adjust memory/CPU based on actual usage
4. Enable request logging sampling to reduce logging costs
5. Use Cloud CDN for static assets if traffic increases

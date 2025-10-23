# Complete Google Cloud Deployment Guide

This comprehensive guide will walk you through deploying your Microlearning Content Generator application (both backend and frontend) to Google Cloud.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Set Up Google Cloud Project](#step-1-set-up-google-cloud-project)
3. [Step 2: Install Required Tools](#step-2-install-required-tools)
4. [Step 3: Prepare Your Application](#step-3-prepare-your-application)
5. [Step 4: Create and Configure Secrets](#step-4-create-and-configure-secrets)
6. [Step 5: Deploy Using Cloud Run](#step-5-deploy-using-cloud-run)
7. [Step 6: Set Up Custom Domain](#step-6-set-up-custom-domain)
8. [Step 7: Configure CI/CD](#step-7-configure-cicd)
9. [Step 8: Monitoring and Maintenance](#step-8-monitoring-and-maintenance)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:
- A Google Cloud account with billing enabled
- A valid credit card (for billing, though you get $300 free credits)
- Your API keys ready (Google AI and Anthropic)
- Basic familiarity with command line

## Step 1: Set Up Google Cloud Project

### 1.1 Create a New Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project selector at the top
3. Click "New Project"
4. Enter project details:
   ```
   Project Name: microlearning-generator
   Project ID: microlearning-gen-[random-number]
   ```
5. Click "Create"

### 1.2 Enable Billing

1. In Console, go to "Billing" in the navigation menu
2. Link a billing account to your project
3. If new user, claim your $300 free credits

### 1.3 Enable Required APIs

Run these commands in Cloud Shell or your terminal:

```bash
# Set your project ID
export PROJECT_ID=your-project-id-here
gcloud config set project $PROJECT_ID

# Enable all required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com \
  iap.googleapis.com \
  cloudresourcemanager.googleapis.com
```

## Step 2: Install Required Tools

### 2.1 Install Google Cloud SDK

**Windows:**
1. Download from: https://cloud.google.com/sdk/docs/install-sdk#windows
2. Run the installer
3. Open PowerShell and run:
   ```powershell
   gcloud init
   ```

**Mac/Linux:**
```bash
# Download and install
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### 2.2 Authenticate

```bash
# Login to Google Cloud
gcloud auth login

# Set default project
gcloud config set project $PROJECT_ID

# Set default region
gcloud config set run/region us-central1
```

### 2.3 Install Docker (Optional, for local testing)

- Windows/Mac: Download Docker Desktop from https://www.docker.com/products/docker-desktop
- Linux: Follow instructions at https://docs.docker.com/engine/install/

## Step 3: Prepare Your Application

### 3.1 Update Environment Configuration

Create a `.env` file in your project root:

```bash
# Copy the example file
cp backend/env.example .env
```

Edit the `.env` file with your actual values:

```env
# API Keys (Required - will be stored in Google Secret Manager)
GOOGLE_API_KEY=your_actual_google_api_key_here
ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here

# Authentication (Required)
EDITOR_PASSWORD=choose_a_strong_password
ADMIN_PASSWORD=choose_another_strong_password
APP_SECRET=generate_random_32_char_string_here

# Model Configuration (Optional)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GEMINI_PRO=gemini-2.0-flash-exp
GEMINI_FLASH=gemini-2.0-flash-exp
```

To generate a secure APP_SECRET:
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows PowerShell:
-join ((1..32) | ForEach {'{0:X}' -f (Get-Random -Max 256)})
```

### 3.2 Update Frontend Configuration

Edit `frontend/next.config.js` to ensure proper API URL handling:

```javascript
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000',
  },
  // ... rest of your config
}
```

## Step 4: Create and Configure Secrets

### 4.1 Create Secrets in Google Secret Manager

```bash
# Create API key secrets
echo -n "your-google-api-key-here" | \
  gcloud secrets create google-api-key --data-file=-

echo -n "your-anthropic-api-key-here" | \
  gcloud secrets create anthropic-api-key --data-file=-

echo -n "your-editor-password-here" | \
  gcloud secrets create editor-password --data-file=-

echo -n "your-admin-password-here" | \
  gcloud secrets create admin-password --data-file=-

echo -n "your-32-char-app-secret" | \
  gcloud secrets create app-secret --data-file=-
```

### 4.2 Create Service Account

```bash
# Create service account
gcloud iam service-accounts create microlearning-sa \
  --display-name="Microlearning Generator Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

## Step 5: Deploy Using Cloud Run

### Option A: Deploy with Cloud Build (Recommended)

```bash
# From your project root directory
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1,_SERVICE_ACCOUNT=microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com,_APP_SECRET=$(openssl rand -hex 32)
```

### Option B: Manual Deployment

#### 5.1 Build and Push Docker Image

```bash
# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/microlearning-generator:latest .

# Configure Docker to use gcloud credentials
gcloud auth configure-docker

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/microlearning-generator:latest
```

#### 5.2 Deploy to Cloud Run

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
  --set-secrets="ADMIN_PASSWORD=admin-password:latest" \
  --set-secrets="APP_SECRET=app-secret:latest" \
  --set-env-vars="MAX_FORMATTER_RETRIES=1" \
  --set-env-vars="MODEL_TEMPERATURE=0.51" \
  --set-env-vars="MODEL_TOP_P=0.95" \
  --set-env-vars="PORT=4000" \
  --set-env-vars="NEXT_PUBLIC_API_URL=/api" \
  --service-account=microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com
```

### 5.3 Verify Deployment

After deployment, you'll get a URL like:
```
Service URL: https://microlearning-generator-xxxxx-uc.a.run.app
```

Test the deployment:
1. Visit the URL in your browser
2. Check API health: `https://your-url/api/healthz`
3. View API docs: `https://your-url/api/docs`

## Step 6: Set Up Custom Domain (Optional)

### 6.1 Configure Domain Mapping

```bash
# Map a custom domain
gcloud run domain-mappings create \
  --service microlearning-generator \
  --domain your-domain.com \
  --region us-central1
```

### 6.2 Update DNS Records

Add the provided DNS records to your domain provider:
- Type: A or AAAA records pointing to Google's IPs
- Type: TXT record for verification

### 6.3 Enable HTTPS

HTTPS is automatically enabled for Cloud Run services.

## Step 7: Configure CI/CD

### 7.1 Set Up GitHub Repository

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/microlearning-generator.git
git push -u origin main
```

### 7.2 Connect to Cloud Build

1. Go to Cloud Build in Google Console
2. Click "Triggers" → "Create Trigger"
3. Select "GitHub" and authenticate
4. Choose your repository
5. Configure trigger:
   - Name: `deploy-on-push`
   - Event: Push to branch
   - Branch: `^main$`
   - Build configuration: Cloud Build configuration file
   - Location: `/cloudbuild.yaml`

### 7.3 Add Build Substitutions

In the trigger settings, add substitution variables:
- `_REGION`: us-central1
- `_SERVICE_ACCOUNT`: microlearning-sa@your-project.iam.gserviceaccount.com

## Step 8: Monitoring and Maintenance

### 8.1 View Logs

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=microlearning-generator" \
  --limit 50 \
  --format json

# Stream logs in real-time
gcloud alpha logging tail "resource.type=cloud_run_revision \
  AND resource.labels.service_name=microlearning-generator"
```

### 8.2 Monitor Performance

1. Go to Cloud Console → Cloud Run
2. Click on your service
3. View tabs:
   - **Metrics**: Request count, latency, CPU usage
   - **Logs**: Application logs
   - **Revisions**: Deployment history
   - **Details**: Configuration

### 8.3 Set Up Alerts

```bash
# Create an alert policy for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition="rate(cloud_run_revision.request_count[1m]) > 0.1"
```

### 8.4 Update Application

To deploy updates:
```bash
# Make your code changes
git add .
git commit -m "Update description"
git push origin main
# Cloud Build will automatically deploy if CI/CD is configured

# Or manually:
gcloud builds submit --config=cloudbuild.yaml
```

## Cost Optimization

### Estimated Monthly Costs

- **Cloud Run**: ~$10-50/month (depending on usage)
  - First 2 million requests free
  - First 360,000 GB-seconds free
  - First 180,000 vCPU-seconds free
- **Secret Manager**: ~$0.06 per secret per month
- **Cloud Build**: First 120 build-minutes free per day
- **Container Registry**: ~$0.10/GB/month

### Cost Saving Tips

1. **Set maximum instances**: Prevent runaway costs
   ```bash
   gcloud run services update microlearning-generator \
     --max-instances=5
   ```

2. **Use minimum instances = 0**: No cost when not in use
   ```bash
   gcloud run services update microlearning-generator \
     --min-instances=0
   ```

3. **Optimize container size**: Smaller images = faster cold starts
4. **Monitor usage**: Set up billing alerts

## Troubleshooting

### Common Issues and Solutions

#### 1. Container fails to start
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Common fix: Ensure all environment variables are set
gcloud run services describe microlearning-generator --region us-central1
```

#### 2. "Permission denied" errors
```bash
# Grant necessary permissions to service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:microlearning-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### 3. Frontend can't reach backend
```bash
# Update NEXT_PUBLIC_API_URL environment variable
gcloud run services update microlearning-generator \
  --set-env-vars="NEXT_PUBLIC_API_URL=/api" \
  --region us-central1
```

#### 4. High latency on cold starts
- Increase minimum instances to 1
- Optimize Docker image size
- Use lighter dependencies

#### 5. Out of memory errors
```bash
# Increase memory allocation
gcloud run services update microlearning-generator \
  --memory=4Gi \
  --region us-central1
```

## Security Best Practices

1. **Never commit secrets**: Use Secret Manager
2. **Enable authentication**: For production, remove `--allow-unauthenticated`
3. **Use IAP**: Set up Identity-Aware Proxy for additional security
4. **Regular updates**: Keep dependencies updated
5. **Monitor access**: Review Cloud Audit Logs regularly

## Support and Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Google Cloud Free Tier](https://cloud.google.com/free)

## Next Steps

After successful deployment:
1. Set up a custom domain
2. Configure Identity-Aware Proxy (IAP) for authentication
3. Set up monitoring and alerting
4. Configure backup strategies
5. Implement rate limiting and DDoS protection

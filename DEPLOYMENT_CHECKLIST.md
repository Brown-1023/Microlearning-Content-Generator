# Google Cloud Deployment Checklist ✅

## Quick Start
**For automated deployment, run:**
- **Windows**: `.\deploy-to-gcloud.ps1`
- **Mac/Linux**: `./deploy-to-gcloud.sh`

## Manual Deployment Checklist

### ☐ Prerequisites
- [ ] Google Cloud account with billing enabled
- [ ] Google AI API key from [AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Anthropic API key from [Anthropic Console](https://console.anthropic.com/)
- [ ] Admin and Editor passwords ready

### ☐ Step 1: Install Tools
- [ ] Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [ ] Install [Docker Desktop](https://www.docker.com/products/docker-desktop) (optional)
- [ ] Open terminal/PowerShell

### ☐ Step 2: Initialize Project
```bash
# Login to Google Cloud
gcloud auth login

# Create or select project
gcloud projects create microlearning-gen-12345  # Or use existing
gcloud config set project microlearning-gen-12345

# Enable billing in Cloud Console
```

### ☐ Step 3: Enable APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com
```

### ☐ Step 4: Prepare Environment
```bash
# Copy environment template
cp backend/env.example .env

# Edit .env with your values:
# - GOOGLE_API_KEY=your_key
# - ANTHROPIC_API_KEY=your_key
# - EDITOR_PASSWORD=your_password
# - ADMIN_PASSWORD=your_password
```

### ☐ Step 5: Create Secrets
```bash
# Store secrets in Google Secret Manager
echo -n "your-google-api-key" | gcloud secrets create google-api-key --data-file=-
echo -n "your-anthropic-key" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "your-editor-pass" | gcloud secrets create editor-password --data-file=-
echo -n "your-admin-pass" | gcloud secrets create admin-password --data-file=-
```

### ☐ Step 6: Deploy Application
```bash
# Option A: Use Cloud Build (recommended)
gcloud builds submit --config=cloudbuild.yaml

# Option B: Deploy manually
docker build -t gcr.io/PROJECT_ID/microlearning-generator .
docker push gcr.io/PROJECT_ID/microlearning-generator
gcloud run deploy microlearning-generator --image gcr.io/PROJECT_ID/microlearning-generator
```

### ☐ Step 7: Verify Deployment
- [ ] Visit the Cloud Run URL provided
- [ ] Test API health: `https://your-url/api/healthz`
- [ ] Login with Editor/Admin credentials
- [ ] Generate test content

## Common Commands

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Update Application
```bash
git push origin main  # If CI/CD configured
# OR
gcloud builds submit --config=cloudbuild.yaml
```

### Check Service Status
```bash
gcloud run services describe microlearning-generator --region us-central1
```

### Update Environment Variables
```bash
gcloud run services update microlearning-generator \
  --update-env-vars KEY=value \
  --region us-central1
```

## Cost Estimates
- **Cloud Run**: ~$10-50/month (usage-based)
- **Secret Manager**: ~$0.30/month
- **Container Registry**: ~$0.10/GB/month
- **Total**: ~$15-60/month for moderate usage

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Build fails | Check API keys in secrets |
| Container won't start | Verify all environment variables |
| Frontend can't reach backend | Check NEXT_PUBLIC_API_URL |
| Permission denied | Grant service account permissions |
| High latency | Increase min instances to 1 |

## Security Checklist
- [ ] Secrets stored in Secret Manager (not in code)
- [ ] Strong passwords for Editor/Admin
- [ ] Consider enabling IAP for production
- [ ] Regular dependency updates
- [ ] Monitor access logs

## Support Resources
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud Build Docs](https://cloud.google.com/build/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

## Quick Links
- **Cloud Console**: https://console.cloud.google.com
- **Cloud Run Services**: https://console.cloud.google.com/run
- **Secret Manager**: https://console.cloud.google.com/security/secret-manager
- **Cloud Build History**: https://console.cloud.google.com/cloud-build/builds

---

**Need help?** Check the detailed [GOOGLE_CLOUD_DEPLOYMENT_GUIDE.md](GOOGLE_CLOUD_DEPLOYMENT_GUIDE.md) for comprehensive instructions.

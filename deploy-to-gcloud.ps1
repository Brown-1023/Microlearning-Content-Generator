# Google Cloud Deployment Script for Microlearning Content Generator (Windows PowerShell)
# This script automates the deployment process to Google Cloud Run

$ErrorActionPreference = "Stop"

# Color functions
function Write-Success {
    Write-Host "[✓] $args" -ForegroundColor Green
}

function Write-Error-Message {
    Write-Host "[✗] $args" -ForegroundColor Red
}

function Write-Warning-Message {
    Write-Host "[!] $args" -ForegroundColor Yellow
}

# ASCII Art Header
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Microlearning Generator - GCloud Deployer   " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    $null = gcloud version 2>$null
} catch {
    Write-Error-Message "gcloud CLI is not installed. Please install it first:"
    Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}
Write-Success "gcloud CLI detected"

# Check if Docker is installed (optional)
try {
    $null = docker version 2>$null
    Write-Success "Docker detected (optional)"
} catch {
    Write-Warning-Message "Docker is not installed. It's optional but recommended for local testing."
}

# Step 1: Get project configuration
Write-Host ""
Write-Host "Step 1: Project Configuration" -ForegroundColor Cyan
Write-Host "-----------------------------" -ForegroundColor Cyan

# Get current project or ask for one
$currentProject = gcloud config get-value project 2>$null
if ([string]::IsNullOrWhiteSpace($currentProject)) {
    $PROJECT_ID = Read-Host "Enter your Google Cloud Project ID"
} else {
    $useCurrentAnswer = Read-Host "Use current project '$currentProject'? (y/n)"
    if ($useCurrentAnswer -eq "y" -or $useCurrentAnswer -eq "Y") {
        $PROJECT_ID = $currentProject
    } else {
        $PROJECT_ID = Read-Host "Enter your Google Cloud Project ID"
    }
}

# Set the project
gcloud config set project $PROJECT_ID
Write-Success "Project set to: $PROJECT_ID"

# Set default region
$regionInput = Read-Host "Enter deployment region (press Enter for us-central1)"
$REGION = if ([string]::IsNullOrWhiteSpace($regionInput)) { "us-central1" } else { $regionInput }
gcloud config set run/region $REGION
Write-Success "Region set to: $REGION"

# Step 2: Enable required APIs
Write-Host ""
Write-Host "Step 2: Enabling Required APIs" -ForegroundColor Cyan
Write-Host "-------------------------------" -ForegroundColor Cyan

Write-Success "Enabling Cloud APIs (this may take a few minutes)..."
gcloud services enable `
  cloudbuild.googleapis.com `
  run.googleapis.com `
  secretmanager.googleapis.com `
  containerregistry.googleapis.com `
  artifactregistry.googleapis.com `
  --quiet

Write-Success "APIs enabled successfully"

# Step 3: Check for .env file
Write-Host ""
Write-Host "Step 3: Environment Configuration" -ForegroundColor Cyan
Write-Host "---------------------------------" -ForegroundColor Cyan

if (!(Test-Path ".env")) {
    Write-Warning-Message ".env file not found. Creating from template..."
    if (Test-Path "backend\env.example") {
        Copy-Item "backend\env.example" ".env"
        Write-Success "Created .env file from template"
        Write-Host ""
        Write-Warning-Message "IMPORTANT: Edit the .env file with your actual API keys before continuing!"
        Read-Host "Press Enter after you've updated the .env file"
    } else {
        Write-Error-Message "No env.example file found. Please create a .env file manually."
        exit 1
    }
} else {
    Write-Success ".env file found"
}

# Step 4: Create secrets
Write-Host ""
Write-Host "Step 4: Setting up Google Secret Manager" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan

# Function to create or update a secret
function Create-Or-Update-Secret {
    param(
        [string]$SecretName,
        [string]$SecretValue
    )
    
    # Check if secret exists
    $secretExists = $false
    try {
        gcloud secrets describe $SecretName --project=$PROJECT_ID 2>$null | Out-Null
        $secretExists = $true
    } catch {
        $secretExists = $false
    }
    
    if ($secretExists) {
        Write-Output $SecretValue | gcloud secrets versions add $SecretName --data-file=- --quiet
        Write-Success "Updated secret: $SecretName"
    } else {
        Write-Output $SecretValue | gcloud secrets create $SecretName --data-file=- --quiet
        Write-Success "Created secret: $SecretName"
    }
}

# Read values from .env file
$envVars = @{}
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $envVars[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
}

# Get API keys
$GOOGLE_API_KEY = $envVars['GOOGLE_API_KEY']
if ([string]::IsNullOrWhiteSpace($GOOGLE_API_KEY)) {
    $GOOGLE_API_KEY = Read-Host "Enter your Google API Key"
}

$ANTHROPIC_API_KEY = $envVars['ANTHROPIC_API_KEY']
if ([string]::IsNullOrWhiteSpace($ANTHROPIC_API_KEY)) {
    $ANTHROPIC_API_KEY = Read-Host "Enter your Anthropic API Key"
}

$EDITOR_PASSWORD = $envVars['EDITOR_PASSWORD']
if ([string]::IsNullOrWhiteSpace($EDITOR_PASSWORD)) {
    $EDITOR_PASSWORD = Read-Host "Enter Editor Password" -AsSecureString
    $EDITOR_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($EDITOR_PASSWORD))
}

$ADMIN_PASSWORD = $envVars['ADMIN_PASSWORD']
if ([string]::IsNullOrWhiteSpace($ADMIN_PASSWORD)) {
    $ADMIN_PASSWORD = Read-Host "Enter Admin Password" -AsSecureString
    $ADMIN_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($ADMIN_PASSWORD))
}

# Generate APP_SECRET if not provided
$APP_SECRET = $envVars['APP_SECRET']
if ([string]::IsNullOrWhiteSpace($APP_SECRET)) {
    $APP_SECRET = -join ((1..32) | ForEach {'{0:X}' -f (Get-Random -Max 256)})
    Write-Success "Generated random APP_SECRET"
}

# Create secrets in Google Secret Manager
Create-Or-Update-Secret -SecretName "google-api-key" -SecretValue $GOOGLE_API_KEY
Create-Or-Update-Secret -SecretName "anthropic-api-key" -SecretValue $ANTHROPIC_API_KEY
Create-Or-Update-Secret -SecretName "editor-password" -SecretValue $EDITOR_PASSWORD
Create-Or-Update-Secret -SecretName "admin-password" -SecretValue $ADMIN_PASSWORD
Create-Or-Update-Secret -SecretName "app-secret" -SecretValue $APP_SECRET

# Step 5: Create service account
Write-Host ""
Write-Host "Step 5: Setting up Service Account" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

$SERVICE_ACCOUNT_NAME = "microlearning-sa"
$SERVICE_ACCOUNT_EMAIL = "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account exists
$accountExists = $false
try {
    gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID 2>$null | Out-Null
    $accountExists = $true
} catch {
    $accountExists = $false
}

if ($accountExists) {
    Write-Success "Service account already exists: $SERVICE_ACCOUNT_EMAIL"
} else {
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME `
        --display-name="Microlearning Generator Service Account" `
        --quiet
    Write-Success "Created service account: $SERVICE_ACCOUNT_EMAIL"
}

# Grant necessary permissions
Write-Success "Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" `
  --role="roles/secretmanager.secretAccessor" `
  --quiet

# Step 6: Deploy to Cloud Run
Write-Host ""
Write-Host "Step 6: Deploying to Cloud Run" -ForegroundColor Cyan
Write-Host "-------------------------------" -ForegroundColor Cyan

Write-Host ""
Write-Host "Choose deployment method:"
Write-Host "1) Use Cloud Build (recommended)"
Write-Host "2) Build locally with Docker"
Write-Host "3) Skip deployment (configuration only)"
$DEPLOY_METHOD = Read-Host "Enter your choice (1-3)"

switch ($DEPLOY_METHOD) {
    "1" {
        Write-Success "Deploying with Cloud Build..."
        
        # Check if cloudbuild.yaml exists
        if (!(Test-Path "cloudbuild.yaml")) {
            Write-Error-Message "cloudbuild.yaml not found in current directory"
            exit 1
        }
        
        # Submit build
        gcloud builds submit `
          --config=cloudbuild.yaml `
          --substitutions="_REGION=$REGION,_SERVICE_ACCOUNT=$SERVICE_ACCOUNT_EMAIL,_APP_SECRET=$APP_SECRET" `
          --quiet
        
        Write-Success "Deployment submitted to Cloud Build"
    }
    
    "2" {
        Write-Success "Building Docker image locally..."
        
        # Check if Docker is running
        try {
            docker info 2>$null | Out-Null
        } catch {
            Write-Error-Message "Docker is not running. Please start Docker Desktop and try again."
            exit 1
        }
        
        # Build Docker image
        $IMAGE_NAME = "gcr.io/${PROJECT_ID}/microlearning-generator:latest"
        docker build -t $IMAGE_NAME .
        Write-Success "Docker image built: $IMAGE_NAME"
        
        # Configure Docker authentication
        gcloud auth configure-docker --quiet
        
        # Push image
        Write-Success "Pushing image to Container Registry..."
        docker push $IMAGE_NAME
        
        # Deploy to Cloud Run
        Write-Success "Deploying to Cloud Run..."
        gcloud run deploy microlearning-generator `
          --image $IMAGE_NAME `
          --region $REGION `
          --platform managed `
          --memory 2Gi `
          --cpu 2 `
          --timeout 300 `
          --concurrency 100 `
          --min-instances 0 `
          --max-instances 10 `
          --port 8080 `
          --allow-unauthenticated `
          --set-secrets="GOOGLE_API_KEY=google-api-key:latest" `
          --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" `
          --set-secrets="EDITOR_PASSWORD=editor-password:latest" `
          --set-secrets="ADMIN_PASSWORD=admin-password:latest" `
          --set-secrets="APP_SECRET=app-secret:latest" `
          --set-env-vars="MAX_FORMATTER_RETRIES=1" `
          --set-env-vars="MODEL_TEMPERATURE=0.51" `
          --set-env-vars="MODEL_TOP_P=0.95" `
          --set-env-vars="PORT=4000" `
          --set-env-vars="NEXT_PUBLIC_API_URL=/api" `
          --service-account=$SERVICE_ACCOUNT_EMAIL `
          --quiet
    }
    
    "3" {
        Write-Success "Skipping deployment. Configuration complete."
    }
    
    default {
        Write-Error-Message "Invalid choice"
        exit 1
    }
}

# Step 7: Get service URL
if ($DEPLOY_METHOD -ne "3") {
    Write-Host ""
    Write-Host "Step 7: Deployment Complete!" -ForegroundColor Cyan
    Write-Host "----------------------------" -ForegroundColor Cyan
    
    # Get the service URL
    try {
        $SERVICE_URL = gcloud run services describe microlearning-generator `
          --region $REGION `
          --format 'value(status.url)' 2>$null
    } catch {
        $SERVICE_URL = $null
    }
    
    if (![string]::IsNullOrWhiteSpace($SERVICE_URL)) {
        Write-Host ""
        Write-Success "Your application is deployed at:"
        Write-Host $SERVICE_URL -ForegroundColor Green
        Write-Host ""
        Write-Host "Test endpoints:"
        Write-Host "  - Frontend: $SERVICE_URL"
        Write-Host "  - API Health: $SERVICE_URL/api/healthz"
        Write-Host "  - API Docs: $SERVICE_URL/api/docs"
        Write-Host ""
        Write-Host "Credentials:"
        Write-Host "  - Editor login: Use the EDITOR_PASSWORD you set"
        Write-Host "  - Admin login: Use the ADMIN_PASSWORD you set"
    } else {
        Write-Warning-Message "Could not retrieve service URL. Check Cloud Console for details."
    }
}

# Final instructions
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "            Deployment Summary                  " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service Account: $SERVICE_ACCOUNT_EMAIL"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Visit your application URL"
Write-Host "2. Test the API endpoints"
Write-Host "3. Set up monitoring in Cloud Console"
Write-Host "4. Configure a custom domain (optional)"
Write-Host "5. Enable IAP for production (recommended)"
Write-Host ""
Write-Host "For more details, see GOOGLE_CLOUD_DEPLOYMENT_GUIDE.md"
Write-Host ""
Write-Success "Deployment script completed!"

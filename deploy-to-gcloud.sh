#!/bin/bash

# Google Cloud Deployment Script for Microlearning Content Generator
# This script automates the deployment process to Google Cloud Run

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# ASCII Art Header
echo "================================================"
echo "   Microlearning Generator - GCloud Deployer   "
echo "================================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first:"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Docker is installed (optional but recommended)
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. It's optional but recommended for local testing."
fi

# Step 1: Get project configuration
echo "Step 1: Project Configuration"
echo "-----------------------------"

# Get current project or ask for one
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$CURRENT_PROJECT" ]; then
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
else
    read -p "Use current project '$CURRENT_PROJECT'? (y/n): " USE_CURRENT
    if [ "$USE_CURRENT" = "y" ] || [ "$USE_CURRENT" = "Y" ]; then
        PROJECT_ID=$CURRENT_PROJECT
    else
        read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    fi
fi

# Set the project
gcloud config set project $PROJECT_ID
print_status "Project set to: $PROJECT_ID"

# Set default region
read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}
gcloud config set run/region $REGION
print_status "Region set to: $REGION"

# Step 2: Enable required APIs
echo ""
echo "Step 2: Enabling Required APIs"
echo "-------------------------------"

print_status "Enabling Cloud APIs (this may take a few minutes)..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  --quiet

print_status "APIs enabled successfully"

# Step 3: Check for .env file
echo ""
echo "Step 3: Environment Configuration"
echo "---------------------------------"

if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f backend/env.example ]; then
        cp backend/env.example .env
        print_status "Created .env file from template"
        echo ""
        print_warning "IMPORTANT: Edit the .env file with your actual API keys before continuing!"
        read -p "Press Enter after you've updated the .env file..."
    else
        print_error "No env.example file found. Please create a .env file manually."
        exit 1
    fi
else
    print_status ".env file found"
fi

# Step 4: Create secrets
echo ""
echo "Step 4: Setting up Google Secret Manager"
echo "----------------------------------------"

# Function to create or update a secret
create_or_update_secret() {
    SECRET_NAME=$1
    SECRET_VALUE=$2
    
    # Check if secret exists
    if gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID &>/dev/null; then
        echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_NAME --data-file=- --quiet
        print_status "Updated secret: $SECRET_NAME"
    else
        echo -n "$SECRET_VALUE" | gcloud secrets create $SECRET_NAME --data-file=- --quiet
        print_status "Created secret: $SECRET_NAME"
    fi
}

# Read values from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check for required secrets
if [ -z "$GOOGLE_API_KEY" ]; then
    read -p "Enter your Google API Key: " GOOGLE_API_KEY
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    read -p "Enter your Anthropic API Key: " ANTHROPIC_API_KEY
fi

if [ -z "$EDITOR_PASSWORD" ]; then
    read -sp "Enter Editor Password: " EDITOR_PASSWORD
    echo ""
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    read -sp "Enter Admin Password: " ADMIN_PASSWORD
    echo ""
fi

# Generate APP_SECRET if not provided
if [ -z "$APP_SECRET" ]; then
    APP_SECRET=$(openssl rand -hex 32)
    print_status "Generated random APP_SECRET"
fi

# Create secrets in Google Secret Manager
create_or_update_secret "google-api-key" "$GOOGLE_API_KEY"
create_or_update_secret "anthropic-api-key" "$ANTHROPIC_API_KEY"
create_or_update_secret "editor-password" "$EDITOR_PASSWORD"
create_or_update_secret "admin-password" "$ADMIN_PASSWORD"
create_or_update_secret "app-secret" "$APP_SECRET"

# Step 5: Create service account
echo ""
echo "Step 5: Setting up Service Account"
echo "-----------------------------------"

SERVICE_ACCOUNT_NAME="microlearning-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account exists
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID &>/dev/null; then
    print_status "Service account already exists: $SERVICE_ACCOUNT_EMAIL"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Microlearning Generator Service Account" \
        --quiet
    print_status "Created service account: $SERVICE_ACCOUNT_EMAIL"
fi

# Grant necessary permissions
print_status "Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" \
  --quiet

# Step 6: Deploy to Cloud Run
echo ""
echo "Step 6: Deploying to Cloud Run"
echo "-------------------------------"

# Ask for deployment method
echo ""
echo "Choose deployment method:"
echo "1) Use Cloud Build (recommended)"
echo "2) Build locally with Docker"
echo "3) Skip deployment (configuration only)"
read -p "Enter your choice (1-3): " DEPLOY_METHOD

case $DEPLOY_METHOD in
    1)
        print_status "Deploying with Cloud Build..."
        
        # Check if cloudbuild.yaml exists
        if [ ! -f cloudbuild.yaml ]; then
            print_error "cloudbuild.yaml not found in current directory"
            exit 1
        fi
        
        # Submit build
        gcloud builds submit \
          --config=cloudbuild.yaml \
          --substitutions=_REGION=$REGION,_SERVICE_ACCOUNT=$SERVICE_ACCOUNT_EMAIL,_APP_SECRET=$APP_SECRET \
          --quiet
        
        print_status "Deployment submitted to Cloud Build"
        ;;
        
    2)
        print_status "Building Docker image locally..."
        
        # Check if Docker is running
        if ! docker info &>/dev/null; then
            print_error "Docker is not running. Please start Docker and try again."
            exit 1
        fi
        
        # Build Docker image
        IMAGE_NAME="gcr.io/${PROJECT_ID}/microlearning-generator:latest"
        docker build -t $IMAGE_NAME .
        print_status "Docker image built: $IMAGE_NAME"
        
        # Configure Docker authentication
        gcloud auth configure-docker --quiet
        
        # Push image
        print_status "Pushing image to Container Registry..."
        docker push $IMAGE_NAME
        
        # Deploy to Cloud Run
        print_status "Deploying to Cloud Run..."
        gcloud run deploy microlearning-generator \
          --image $IMAGE_NAME \
          --region $REGION \
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
          --service-account=$SERVICE_ACCOUNT_EMAIL \
          --quiet
        ;;
        
    3)
        print_status "Skipping deployment. Configuration complete."
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Step 7: Get service URL
if [ "$DEPLOY_METHOD" != "3" ]; then
    echo ""
    echo "Step 7: Deployment Complete!"
    echo "----------------------------"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe microlearning-generator \
      --region $REGION \
      --format 'value(status.url)' 2>/dev/null)
    
    if [ -n "$SERVICE_URL" ]; then
        echo ""
        print_status "Your application is deployed at:"
        echo -e "${GREEN}$SERVICE_URL${NC}"
        echo ""
        echo "Test endpoints:"
        echo "  - Frontend: $SERVICE_URL"
        echo "  - API Health: $SERVICE_URL/api/healthz"
        echo "  - API Docs: $SERVICE_URL/api/docs"
        echo ""
        echo "Credentials:"
        echo "  - Editor login: Use the EDITOR_PASSWORD you set"
        echo "  - Admin login: Use the ADMIN_PASSWORD you set"
    else
        print_warning "Could not retrieve service URL. Check Cloud Console for details."
    fi
fi

# Final instructions
echo ""
echo "================================================"
echo "            Deployment Summary                  "
echo "================================================"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "Next steps:"
echo "1. Visit your application URL"
echo "2. Test the API endpoints"
echo "3. Set up monitoring in Cloud Console"
echo "4. Configure a custom domain (optional)"
echo "5. Enable IAP for production (recommended)"
echo ""
echo "For more details, see GOOGLE_CLOUD_DEPLOYMENT_GUIDE.md"
echo ""
print_status "Deployment script completed!"

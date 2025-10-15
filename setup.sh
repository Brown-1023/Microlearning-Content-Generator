#!/bin/bash

echo "========================================="
echo "Microlearning Content Generator Setup"
echo "For Google Cloud Run Deployment"
echo "========================================="
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
else
    echo "❌ Docker is not installed. Please install Docker."
    exit 1
fi

# Check gcloud
if command -v gcloud &> /dev/null; then
    echo "✅ Google Cloud SDK is installed"
else
    echo "⚠️  Google Cloud SDK not found (needed for deployment)"
fi

# Create environment file
if [ ! -f .env ]; then
    cp env.example .env
    echo ""
    echo "📝 Created .env file - Please edit with your API keys:"
    echo "   - GOOGLE_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - EDITOR_PASSWORD"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "1. Edit .env with your API keys"
echo ""
echo "2. Test locally:"
echo "   docker-compose up"
echo ""
echo "3. Deploy to Cloud Run:"
echo "   gcloud builds submit --config=cloudbuild.yaml"
echo ""
echo "4. Access:"
echo "   Local: http://localhost:8080"
echo "   Cloud: https://[service-name].run.app"
echo ""
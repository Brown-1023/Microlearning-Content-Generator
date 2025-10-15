# Microlearning Content Generator

Secure internal tool that converts curated notes into finalized microlearning content using a two-step LangGraph pipeline with Claude and Gemini models.

## Architecture

Single container deployment serving both UI and API as required in specifications:
- **Backend**: FastAPI with LangGraph orchestration
- **Frontend**: Next.js/React single-page application
- **Deployment**: Google Cloud Run (single container)

## Features

- **Content Types**: MCQ and Non-MCQ generation
- **AI Models**: 
  - Generator: Claude Sonnet 4.5 or Gemini 2.5 Pro (toggle)
  - Formatter: Gemini 2.5 Flash (always)
- **Validation**: Deterministic code-based validators
- **Security**: Password authentication with path to Google IAP
- **Plain Text**: All prompts and outputs are plain text (no JSON)

## Quick Start

### Prerequisites
- Docker installed
- Google Cloud SDK (for deployment)
- API Keys:
  - Google AI Studio API key
  - Anthropic API key

### Local Development

1. **Setup environment:**
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
```

2. **Run with Docker:**
```bash
# Build and run single container
docker-compose up
```

3. **Access application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:4000
- API Docs: http://localhost:4000/docs

### For Development (Separate Services)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Cloud Run Deployment

### Deploy with Cloud Build (Recommended)

```bash
# Set project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Create secrets
echo -n "your-api-key" | gcloud secrets create google-api-key --data-file=-
echo -n "your-api-key" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "password" | gcloud secrets create editor-password --data-file=-

# Deploy
gcloud builds submit --config=cloudbuild.yaml
```

### Manual Docker Deployment

```bash
# Build
docker build -t gcr.io/$PROJECT_ID/microlearning-generator .

# Push
docker push gcr.io/$PROJECT_ID/microlearning-generator

# Deploy
gcloud run deploy microlearning-generator \
  --image gcr.io/$PROJECT_ID/microlearning-generator \
  --region us-central1 \
  --port 8080 \
  --set-secrets="GOOGLE_API_KEY=google-api-key:latest" \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-secrets="EDITOR_PASSWORD=editor-password:latest"
```

## Project Structure

```
.
├── backend/              # Python FastAPI backend
│   ├── app.py           # Main API application  
│   ├── pipeline.py      # LangGraph orchestration
│   ├── validators.py    # Content validators
│   ├── prompts/         # Plain text prompt templates
│   └── tests/           # Unit tests
├── frontend/            # Next.js React frontend
│   ├── pages/          # Application pages
│   ├── components/     # React components
│   └── services/       # API services
├── Dockerfile          # Single container for Cloud Run
├── docker-compose.yml  # Local development
└── cloudbuild.yaml     # Cloud Build configuration
```

## API Endpoints

- `POST /run` - Generate content
- `GET /healthz` - Health check
- `GET /version` - Version info with prompt hashes
- `POST /api/auth/login` - Authentication
- `GET /docs` - API documentation

## Environment Variables

Required:
- `GOOGLE_API_KEY` - Google AI Studio API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `EDITOR_PASSWORD` - Editor password
- `APP_SECRET` - Session secret

Optional:
- `MAX_FORMATTER_RETRIES` - Max formatter retries (default: 1)
- `MODEL_TEMPERATURE` - Model temperature (default: 0.51)
- `MODEL_TOP_P` - Model top_p (default: 0.95)

## Testing

```bash
# Backend tests
cd backend
pytest tests/

# Test CLI
python test_cli.py generate
```

## Security

- Password authentication (basic)
- Path to Google IAP for production
- HttpOnly session cookies
- Rate limiting (10 requests/minute)
- CORS handled automatically (single container)
- Secrets in Google Secret Manager

## Monitoring

View Cloud Run logs:
```bash
gcloud logging read "resource.type=cloud_run_revision"
```

## License

Internal use only - proprietary software
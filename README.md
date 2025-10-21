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
- **Model Restrictions**: Admins can lock/restrict which models are visible to users
- **Validation**: Deterministic code-based validators
- **Security**: Role-based access control (Admin/Editor roles)
- **Plain Text**: All prompts and outputs are plain text (no JSON)

### Role-Based Access Control

Two user roles with different permissions:

| Feature | Admin | Editor |
|---------|-------|--------|
| Generate Content | ✅ | ✅ |
| Select Model | ✅ | ✅* |
| Set Number of Questions | ✅ | ✅ |
| Set Focus Areas | ✅ | ✅ |
| View/Edit Prompt Templates | ✅ | ❌ |
| Adjust Temperature/Top-P | ✅ | ❌ |
| View Advanced Settings | ✅ | ❌ |
| Configure Model Restrictions | ✅ | ❌ |
| View All Available Models | ✅ | ❌ |

*Editors can only select from models allowed by admin restrictions

Users are identified by their login password:
- **Admin**: Uses `ADMIN_PASSWORD` environment variable
- **Editor**: Uses `EDITOR_PASSWORD` environment variable

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
│   ├── config.py        # Configuration settings
│   ├── prompts/         # Plain text prompt templates
│   └── tests/           # Unit tests
├── frontend/            # Next.js React frontend
│   ├── pages/          # Application pages
│   ├── components/     # React components
│   └── services/       # API services
├── docs/                # Documentation
├── Dockerfile          # Single container for Cloud Run
├── docker-compose.yml  # Local development
├── cloudbuild.yaml     # Cloud Build configuration
├── README.md           # Main documentation
├── MODEL_CONFIGURATION_GUIDE.md  # Detailed model config guide
└── QUICK_CONFIG_REFERENCE.md     # Quick reference card
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
- `ADMIN_PASSWORD` - Admin user password (full access)
- `EDITOR_PASSWORD` - Editor user password (limited access)
- `APP_SECRET` - Session secret

Optional:
- `MAX_FORMATTER_RETRIES` - Max formatter retries (default: 1)
- `MAX_INPUT_CHARS` - Maximum input character limit (default: 500000)
- `MODEL_TEMPERATURE` - Model temperature (default: 0.51)
- `MODEL_TOP_P` - Model top_p (default: 0.95)
- `MODEL_MAX_TOKENS` - Maximum tokens for generation (default: 8000)
- `MODEL_TIMEOUT` - API timeout in seconds (default: 60)

## Model Configuration Guide

> 📚 **Additional Resources:**
> - [Detailed Model Configuration Guide](MODEL_CONFIGURATION_GUIDE.md) - Complete configuration documentation
> - [Quick Config Reference](QUICK_CONFIG_REFERENCE.md) - One-page reference card for common tasks

### Current Model Setup

The pipeline uses the following models:
- **Generator Models** (user-selectable):
  - Claude Sonnet 4.5: `claude-sonnet-4-5-20250929`
  - Gemini 2.5 Pro: `gemini-2.5-pro`
- **Formatter Model** (fixed):
  - Gemini 2.5 Flash: `gemini-2.5-flash`

### How to Update Models

#### 1. Via Environment Variables

The easiest way to update model versions is through environment variables in your `.env` file or deployment configuration:

```bash
# Update model versions
CLAUDE_MODEL=claude-sonnet-4-5-20250929  # Update when new Claude version available
GEMINI_PRO=gemini-2.5-pro                # Update for new Gemini Pro version
GEMINI_FLASH=gemini-2.5-flash            # Update for new Gemini Flash version
```

#### 2. Via Configuration File

For permanent changes, update `backend/config.py`:

```python
# Model Configuration section (lines 27-38)
claude_model: str = Field(
    default="claude-sonnet-4-5-20250929",  # Change default model here
    env="CLAUDE_MODEL"
)
gemini_pro: str = Field(
    default="gemini-2.5-pro",               # Change default model here
    env="GEMINI_PRO"
)
gemini_flash: str = Field(
    default="gemini-2.5-flash",             # Change default model here
    env="GEMINI_FLASH"
)
```

### Adjusting Model Parameters

#### Temperature and Top-P

Temperature controls randomness (0.0 = deterministic, 1.0 = very random)
Top-P controls nucleus sampling (0.1 = narrow, 1.0 = consider all tokens)

**Via Environment Variables:**
```bash
MODEL_TEMPERATURE=0.7    # Increase for more creativity
MODEL_TOP_P=0.9          # Adjust sampling breadth
```

**Via Configuration File** (`backend/config.py` lines 44-48):
```python
model_temperature: float = Field(default=0.51, env="MODEL_TEMPERATURE")
model_top_p: float = Field(default=0.95, env="MODEL_TOP_P")
```

#### Token Limits and Timeouts

Control generation length and API timeouts:

```bash
MODEL_MAX_TOKENS=10000   # Increase for longer outputs
MODEL_TIMEOUT=120         # Increase timeout for slow responses
```

### Pipeline-Specific Settings

#### Input Size Limit

Control maximum input text size:
```bash
MAX_INPUT_CHARS=500000   # Currently set to 500k characters
```

#### Formatter Retries

Control how many times the formatter retries on validation failure:
```bash
MAX_FORMATTER_RETRIES=1  # Set to 0 to disable retries, max recommended: 2
```

### Advanced Configuration

#### Model Initialization in Pipeline

To add support for new model providers or change model initialization logic, update `backend/pipeline.py`:

1. **Model Caller Class** (lines 52-203): Handles model API calls
2. **Generator Node** (lines 323-398): Implements generation logic
3. **Formatter Node** (lines 399-476): Implements formatting logic

Example of adding a new model provider:
```python
# In ModelCaller.call_model() method
elif model_type == "new_provider":
    return self._call_new_provider(
        prompt=prompt,
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
```

### Testing Model Changes

After updating models or parameters:

1. **Test with CLI:**
```bash
cd backend
python test_cli.py generate --type MCQ --model claude
python test_cli.py generate --type NMCQ --model gemini
```

2. **Run validation tests:**
```bash
python test_all_features.py
```

3. **Check model configuration:**
```bash
python -c "from config import settings; print(f'Claude: {settings.claude_model}'); print(f'Temperature: {settings.model_temperature}')"
```

### Deployment Configuration

When deploying to Cloud Run with updated models:

```bash
# Update secrets if API keys changed
gcloud secrets update google-api-key --data-file=-
gcloud secrets update anthropic-api-key --data-file=-

# Deploy with environment overrides
gcloud run deploy microlearning-generator \
  --update-env-vars="MODEL_TEMPERATURE=0.7,MODEL_TOP_P=0.9,CLAUDE_MODEL=claude-3-opus-20240229"
```

### Model Migration Checklist

When updating to new model versions:

1. ✅ Update model name in `.env` or `config.py`
2. ✅ Verify API compatibility (check provider docs)
3. ✅ Test with sample inputs using CLI
4. ✅ Run validation test suite
5. ✅ Update prompt templates if needed (`backend/prompts/`)
6. ✅ Deploy to staging first
7. ✅ Monitor logs for API errors
8. ✅ Update documentation

### Troubleshooting

**Model not found error:**
- Check model name matches provider's exact naming
- Verify API key has access to the model
- Check provider's model availability in your region

**Rate limiting:**
- Adjust `MODEL_TIMEOUT` for longer waits
- Implement exponential backoff in `pipeline.py`
- Consider using different API keys for load distribution

**Output quality issues:**
- Adjust `MODEL_TEMPERATURE` (lower for consistency)
- Modify `MODEL_TOP_P` (lower for focused outputs)
- Review and update prompt templates
- Increase `MODEL_MAX_TOKENS` if outputs are truncated

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
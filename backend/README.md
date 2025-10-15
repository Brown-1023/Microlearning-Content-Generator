# Backend - Microlearning Content Generator

FastAPI backend with LangGraph orchestration for microlearning content generation.

## Structure

- `app.py` - FastAPI application with endpoints
- `pipeline.py` - LangGraph orchestration flow
- `validators.py` - Deterministic content validators
- `prompts/` - Plain text prompt templates
- `tests/` - Unit tests

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python run.py

# Run tests
pytest tests/

# Test CLI
python test_cli.py generate
```

## API Endpoints

- `POST /run` - Generate content
- `GET /healthz` - Health check  
- `GET /version` - Version info
- `GET /docs` - Swagger documentation

## Deployment

This backend is designed to be deployed as part of a single container with the frontend for Google Cloud Run. See the main [README.md](../README.md) for deployment instructions.
# Backend Docker Guide

This guide explains how to build and run the Microlearning Content Generator backend using Docker.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# 1. Create .env file from template
cp env.example .env
# Edit .env with your API keys

# 2. Build and run
docker-compose up -d

# 3. Check health
curl http://localhost:4000/healthz
```

### Using Makefile Commands

```bash
# View all available commands
make help

# Build the image
make build

# Run the container
make run

# View logs
make logs

# Stop container
make stop
```

### Using Docker Directly

```bash
# Build image
docker build -t microlearning-backend .

# Run container
docker run -d \
  --name microlearning-backend \
  -p 4000:4000 \
  --env-file .env \
  microlearning-backend
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Required API Keys
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Authentication
EDITOR_PASSWORD=your_editor_password
ADMIN_PASSWORD=your_admin_password
APP_SECRET=your_32_char_secret_key

# Optional Configuration
MODEL_TEMPERATURE=0.51
MODEL_TOP_P=0.95
MODEL_MAX_TOKENS=8000
MODEL_TIMEOUT=60
MAX_FORMATTER_RETRIES=1
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=minute
```

## Development Setup

### Run with Live Code Reload

For development with automatic code reload:

```bash
# Using docker-compose (mounts ./prompts and ./config as read-only)
docker-compose up

# Or using Makefile
make dev

# Or manually with volume mount
docker run -d \
  --name microlearning-backend-dev \
  -p 4000:4000 \
  --env-file .env \
  -v $(pwd):/app \
  microlearning-backend
```

### Accessing the Container

```bash
# Open shell in running container
make shell
# or
docker exec -it microlearning-backend /bin/bash

# View real-time logs
make logs
# or
docker logs -f microlearning-backend
```

## API Endpoints

Once running, the backend provides:

| Endpoint | Description |
|----------|------------|
| http://localhost:4000/healthz | Health check endpoint |
| http://localhost:4000/docs | Interactive API documentation (Swagger UI) |
| http://localhost:4000/redoc | Alternative API documentation (ReDoc) |
| http://localhost:4000/version | Version information |
| http://localhost:4000/api/generate | Main generation endpoint |

## Testing

### Test API with curl

```bash
# Health check
curl http://localhost:4000/healthz

# Version info
curl http://localhost:4000/version

# Generate content (requires authentication)
curl -X POST http://localhost:4000/api/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content_type": "MCQ",
    "generator_model": "gemini-2.0-flash-exp",
    "input_text": "Sample medical text about hypertension...",
    "num_questions": 2
  }'
```

### Run Tests in Container

```bash
# Using Makefile
make test

# Or directly
docker run --rm \
  --env-file .env \
  microlearning-backend \
  python -m pytest tests/
```

## Production Deployment

### Build for Production

```bash
# Build with specific tag
docker build -t microlearning-backend:v1.0.0 .

# Tag for registry
docker tag microlearning-backend:v1.0.0 gcr.io/PROJECT_ID/microlearning-backend:v1.0.0

# Push to Google Container Registry
docker push gcr.io/PROJECT_ID/microlearning-backend:v1.0.0
```

### Optimize Image Size

The Dockerfile is already optimized with:
- Python slim base image
- Multi-stage build capabilities
- Minimal system dependencies
- No-cache pip installations

Current image size: ~250MB

### Security Considerations

1. **Never commit .env files** - Use `.dockerignore` to exclude them
2. **Use secrets management** in production (Google Secret Manager, etc.)
3. **Run as non-root user** in production:
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```
4. **Scan for vulnerabilities**:
   ```bash
   docker scan microlearning-backend
   ```

## Docker Compose Configuration

### Default Configuration

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "4000:4000"
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:4000/healthz')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Production Configuration

For production, add:
- Resource limits
- Restart policies
- Logging configuration

```yaml
services:
  backend:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs microlearning-backend

# Common issues:
# - Missing .env file
# - Invalid API keys
# - Port 4000 already in use
```

### Memory Issues

```bash
# Increase memory limit
docker run -d \
  --name microlearning-backend \
  --memory="2g" \
  --memory-swap="4g" \
  -p 4000:4000 \
  microlearning-backend
```

### Network Issues

```bash
# Check if port is accessible
netstat -an | grep 4000

# Test from inside container
docker exec microlearning-backend curl http://localhost:4000/healthz
```

### Clean Up

```bash
# Stop and remove everything
make clean

# Or manually
docker stop microlearning-backend
docker rm microlearning-backend
docker rmi microlearning-backend

# Remove unused Docker resources
docker system prune -a
```

## Integration with Frontend

If running frontend separately:

```javascript
// frontend/.env
NEXT_PUBLIC_API_URL=http://localhost:4000
```

Or use Docker network for container-to-container communication:

```bash
# Create network
docker network create microlearning-net

# Run backend on network
docker run -d \
  --name backend \
  --network microlearning-net \
  -p 4000:4000 \
  microlearning-backend

# Frontend can access backend at http://backend:4000
```

## Monitoring

### Health Monitoring

```bash
# Simple health check loop
while true; do
  curl -s http://localhost:4000/healthz || echo "Service down"
  sleep 30
done
```

### Resource Usage

```bash
# Check container stats
docker stats microlearning-backend

# Check logs size
docker logs microlearning-backend 2>&1 | wc -l
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Backend
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push
        run: |
          cd backend
          docker build -t microlearning-backend .
          # Add push commands
```

## Support

For issues or questions:
1. Check container logs: `docker logs microlearning-backend`
2. Verify environment variables in `.env`
3. Ensure API keys are valid
4. Check API documentation at http://localhost:4000/docs

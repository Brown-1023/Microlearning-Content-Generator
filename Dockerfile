# Multi-stage build for both frontend and backend to serve from single container

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source code  
COPY frontend/ .

# Build Next.js app for production
RUN npm run build

# Stage 2: Build backend dependencies
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Also install httpx for the proxy
RUN pip install --no-cache-dir --user httpx

# Stage 3: Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Install Node.js for running Next.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /root/.local /root/.local

# Copy built frontend from builder
COPY --from=frontend-builder /frontend/.next /app/frontend/.next
COPY --from=frontend-builder /frontend/public /app/frontend/public  
COPY --from=frontend-builder /frontend/node_modules /app/frontend/node_modules
COPY --from=frontend-builder /frontend/package.json /app/frontend/package.json
COPY --from=frontend-builder /frontend/next.config.js /app/frontend/next.config.js

# Copy backend application code and configs
COPY *.py /app/
COPY *.txt /app/
COPY *.md /app/
COPY *.yaml /app/
COPY prompts/ /app/prompts/
COPY samples/ /app/samples/
COPY validators.py /app/validators.py
COPY pipeline.py /app/pipeline.py
COPY config.py /app/config.py
COPY app.py /app/app.py
COPY run.py /app/run.py
COPY start_services.py /app/start_services.py

# Make scripts executable
RUN chmod +x /app/start_services.py

# Make sure Python packages are in PATH
ENV PATH=/root/.local/bin:$PATH

# Set environment variables for production
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000 (Cloud Run requirement)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/healthz')" || exit 1

# Start both services via the proxy script
CMD ["python", "/app/start_services.py"]
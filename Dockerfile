# Single container for Cloud Run - serves both UI and API as required
# Milestone 2: "Serve UI and API from the same Cloud Run service (one container)"

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# Stage 2: Build backend
FROM python:3.11-slim

WORKDIR /app

# Install Node.js for serving frontend
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend from builder
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json
COPY --from=frontend-builder /app/frontend/next.config.js ./frontend/next.config.js

# Create startup script for single container
RUN echo '#!/bin/bash\n\
cd /app/frontend && npm start &\n\
cd /app && python run.py &\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Environment variables
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Cloud Run expects port 8080 by default
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/healthz')" || exit 1

# Start both services
CMD ["/app/start.sh"]

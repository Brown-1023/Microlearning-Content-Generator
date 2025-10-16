"""
FastAPI application for microlearning content generation.
"""

import os
import hashlib
from datetime import datetime
from typing import Optional, Literal
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException, status, Depends, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets
import time
from pathlib import Path
import jwt
from datetime import timedelta

from pipeline import ContentPipeline
from config import settings

# Configure structured logging
logger = structlog.get_logger()


# Settings are imported from config.py

# Initialize pipeline
pipeline = ContentPipeline()

# JWT configuration
JWT_SECRET_KEY = settings.app_secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=1)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(
        "app_started",
        timestamp=datetime.utcnow().isoformat(),
        max_retries=settings.max_formatter_retries
    )
    yield
    logger.info("app_shutdown", timestamp=datetime.utcnow().isoformat())


# Middleware for request size limit
from starlette.middleware.base import BaseHTTPMiddleware

class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request, call_next):
        if request.method == 'POST':
            content_length = request.headers.get('content-length')
            if content_length:
                content_length = int(content_length)
                if content_length > self.max_upload_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": f"Request size exceeds {self.max_upload_size / (1024*1024):.1f}MB limit"
                        }
                    )
        return await call_next(request)

# Create FastAPI app
app = FastAPI(
    title="Microlearning Content Generator",
    description="Internal tool for generating MCQ and Non-MCQ educational content",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Length"],
)

# Add request size limit middleware (configurable via env)
max_request_size = settings.max_request_size_mb * 1024 * 1024  # Convert MB to bytes
app.add_middleware(LimitUploadSize, max_upload_size=max_request_size)

# Static files served by Next.js frontend


class RunRequest(BaseModel):
    """Request model for the /run endpoint."""
    content_type: Literal["MCQ", "NMCQ"] = Field(
        ...,
        description="Type of content to generate"
    )
    generator_model: str = Field(
        ...,
        description="AI model to use for generation (e.g., claude-sonnet-3.5, gemini-2.5-pro)"
    )
    input_text: str = Field(
        ...,
        description="Text to analyze and generate questions from",
        min_length=1,
        max_length=150000
    )
    num_questions: int = Field(
        ...,
        description="Number of questions to generate",
        ge=1,
        le=20
    )
    focus_areas: Optional[str] = Field(
        None,
        description="Optional areas to focus on when generating questions"
    )
    temperature: Optional[float] = Field(
        None,
        description="Temperature for model generation (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    top_p: Optional[float] = Field(
        None,
        description="Top-p sampling parameter (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    custom_mcq_generator: Optional[str] = Field(
        None,
        description="Custom MCQ generator prompt"
    )
    custom_mcq_formatter: Optional[str] = Field(
        None,
        description="Custom MCQ formatter prompt"
    )
    custom_nmcq_generator: Optional[str] = Field(
        None,
        description="Custom Non-MCQ generator prompt"
    )
    custom_nmcq_formatter: Optional[str] = Field(
        None,
        description="Custom Non-MCQ formatter prompt"
    )
    
    @validator("input_text")
    def validate_input_text(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Input text must be at least 10 characters")
        return v
    
    @validator("content_type")
    def validate_content_type(cls, v):
        return v.upper()


class RunResponse(BaseModel):
    """Response model for the /run endpoint."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    validation_errors: list = []
    partial_output: Optional[str] = None
    metadata: dict = {}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    checks: dict


class VersionResponse(BaseModel):
    """Version information response."""
    version: str
    prompt_hashes: dict
    max_formatter_retries: int
    models: dict


class LoginRequest(BaseModel):
    """Login request model."""
    password: str


def create_jwt_token() -> str:
    """Create a JWT token."""
    expiration = datetime.utcnow() + JWT_EXPIRATION_DELTA
    payload = {
        "exp": expiration,
        "iat": datetime.utcnow(),
        "authorized": True
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> bool:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("authorized", False)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
        return False


def verify_auth(request: Request, authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify authentication via JWT Bearer token.
    """
    # No password required - allow access
    if not settings.editor_password:
        return True
    
    # Check Bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if verify_jwt_token(token):
            return True
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns system health status and checks.
    """
    checks = {}
    
    # Check API keys are configured
    checks["google_api_key"] = bool(settings.google_api_key)
    checks["anthropic_api_key"] = bool(settings.anthropic_api_key)
    
    # Check prompt files exist
    prompt_files = [
        "prompts/mcq.generator.txt",
        "prompts/mcq.formatter.txt",
        "prompts/nonmcq.generator.txt",
        "prompts/nonmcq.formatter.txt"
    ]
    
    checks["prompts_loaded"] = all(
        os.path.exists(f) for f in prompt_files
    )
    
    overall_status = "healthy" if all(checks.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        checks=checks
    )


@app.get("/version", response_model=VersionResponse)
async def version_info():
    """
    Version information endpoint.
    
    Returns version details including prompt hashes and configuration.
    """
    return VersionResponse(
        version="1.0.0",
        prompt_hashes=pipeline.get_prompt_hashes(),
        max_formatter_retries=settings.max_formatter_retries,
        models={
            "claude": settings.claude_model,
            "gemini_pro": settings.gemini_pro,
            "gemini_flash": settings.gemini_flash
        }
    )


@app.post("/run", response_model=RunResponse)
@limiter.limit("10 per minute")
async def run_pipeline(
    request: Request,
    run_request: RunRequest,
    authorized: bool = Depends(verify_auth)
):
    """
    Main endpoint to run the content generation pipeline.
    
    Args:
        request: The run request with input parameters
        authorized: Authorization check dependency
        
    Returns:
        RunResponse with generated content or error details
    """
    logger.info(
        "run_request_received",
        content_type=run_request.content_type,
        generator_model=run_request.generator_model,
        num_questions=run_request.num_questions,
        input_length=len(run_request.input_text)
    )
    
    try:
        # Run the pipeline
        result = pipeline.run(
            content_type=run_request.content_type,
            generator_model=run_request.generator_model,
            input_text=run_request.input_text,
            num_questions=run_request.num_questions,
            focus_areas=run_request.focus_areas,
            temperature=run_request.temperature,
            top_p=run_request.top_p,
            custom_mcq_generator=run_request.custom_mcq_generator,
            custom_mcq_formatter=run_request.custom_mcq_formatter,
            custom_nmcq_generator=run_request.custom_nmcq_generator,
            custom_nmcq_formatter=run_request.custom_nmcq_formatter
        )
        
        # Log result
        logger.info(
            "run_request_completed",
            success=result["success"],
            validation_errors=len(result.get("validation_errors", [])),
            retries=result["metadata"].get("formatter_retries", 0)
        )
        
        # Handle failure with validation errors
        if not result["success"] and result.get("validation_errors"):
            # Return 422 with validation errors and partial output
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "success": False,
                    "output": None,
                    "error": "Validation failed after retries",
                    "validation_errors": result["validation_errors"],
                    "partial_output": result.get("partial_output"),
                    "metadata": result["metadata"]
                }
            )
        
        # Return success or other failure
        return RunResponse(**result)
        
    except Exception as e:
        logger.error("run_request_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}"
        )


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Microlearning Content Generator API",
        "version": "1.0.0",
        "frontend": "http://localhost:3000",
        "documentation": "/docs"
    }


@app.post("/api/auth/login")
async def login(login_request: LoginRequest):
    """Handle login and return JWT token."""
    if not settings.editor_password:
        # No password set, return token anyway (dev mode)
        token = create_jwt_token()
        return {
            "success": True,
            "message": "Logged in (dev mode)",
            "token": token
        }
    
    if login_request.password != settings.editor_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    token = create_jwt_token()
    return {
        "success": True,
        "message": "Logged in successfully",
        "token": token
    }


@app.get("/api/auth/check")
async def check_auth(authorization: Optional[str] = Header(None)):
    """Check if user is authenticated."""
    # No password required - always authenticated
    if not settings.editor_password:
        return {"authenticated": True}
    
    # Check Bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if verify_jwt_token(token):
            return {"authenticated": True}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.post("/api/auth/logout")
async def logout():
    """Handle logout (JWT tokens are stateless, so just return success)."""
    # With JWT, logout is handled client-side by removing the token
    return {"success": True, "message": "Logged out"}


@app.get("/api/prompts")
async def get_prompts():
    """Get all default prompt templates."""
    prompts = {}
    prompt_files = {
        "mcq_generator": "prompts/mcq.generator.txt",
        "mcq_formatter": "prompts/mcq.formatter.txt", 
        "nmcq_generator": "prompts/nonmcq.generator.txt",
        "nmcq_formatter": "prompts/nonmcq.formatter.txt"
    }
    
    for key, filepath in prompt_files.items():
        try:
            file_path = Path(filepath)
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompts[key] = f.read()
            else:
                prompts[key] = f"Error: {filepath} not found"
        except Exception as e:
            prompts[key] = f"Error loading prompt: {str(e)}"
    
    return prompts


@app.get("/api/info")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Microlearning Content Generator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/healthz",
            "version": "/version",
            "generate": "/run (POST)",
            "auth": "/api/auth/*",
            "prompts": "/api/prompts"
        }
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error("unhandled_exception", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"]
            }
        }
    )

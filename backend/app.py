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

from pipeline import ContentPipeline
from config import settings

# Configure structured logging
logger = structlog.get_logger()


# Settings are imported from config.py

# Initialize pipeline
pipeline = ContentPipeline()

# Session storage (in production, use Redis or similar)
sessions = {}

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
    generator_model: Literal["claude", "gemini"] = Field(
        ...,
        description="AI model to use for generation"
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


def create_session(response: Response) -> str:
    """Create a new session and set cookie."""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "created_at": time.time(),
        "last_accessed": time.time()
    }
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=86400  # 24 hours
    )
    
    return session_id


def verify_session(request: Request) -> bool:
    """Verify session from cookie."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        return False
    
    # Check session expiry (24 hours)
    session = sessions[session_id]
    if time.time() - session["created_at"] > 86400:
        del sessions[session_id]
        return False
    
    # Update last accessed time
    session["last_accessed"] = time.time()
    return True


def verify_auth(request: Request, authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify authentication via session or Bearer token.
    """
    # First check session cookie
    if verify_session(request):
        return True
    
    # Fall back to Bearer token for API access
    if not settings.editor_password:
        return True
    
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if token == settings.editor_password:
            return True
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
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
        "prompts/mcq.generator.template.txt",
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
            focus_areas=run_request.focus_areas
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
async def login(login_request: LoginRequest, response: Response):
    """Handle login and create session."""
    if not settings.editor_password:
        # No password set, create session anyway (dev mode)
        create_session(response)
        return {"success": True, "message": "Logged in (dev mode)"}
    
    if login_request.password != settings.editor_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    create_session(response)
    return {"success": True, "message": "Logged in successfully"}


@app.get("/api/auth/check")
async def check_auth(request: Request):
    """Check if user is authenticated."""
    if verify_session(request):
        return {"authenticated": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )


@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """Handle logout and clear session."""
    session_id = request.cookies.get("session_id")
    
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    response.delete_cookie(key="session_id")
    return {"success": True, "message": "Logged out"}


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
            "auth": "/api/auth/*"
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

"""
FastAPI application for microlearning content generation.
"""

import os
import hashlib
import shutil
from datetime import datetime
from typing import Optional, Literal, AsyncGenerator
from contextlib import asynccontextmanager
import asyncio
import json

import structlog
from fastapi import FastAPI, HTTPException, status, Depends, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sse_starlette.sse import EventSourceResponse
import secrets
import time
from pathlib import Path
import jwt
from datetime import timedelta

from pipeline import ContentPipeline
from config import settings
from model_manager import ModelManager, ALL_MODELS

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
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "ngrok-skip-browser-warning"],
    expose_headers=["Content-Length"],
)

# Add request size limit middleware (configurable via env)
max_request_size = settings.max_request_size_mb * 1024 * 1024  # Convert MB to bytes
app.add_middleware(LimitUploadSize, max_upload_size=max_request_size)

# Static files served by Next.js frontend

# Create backup of original prompts on first run
def create_prompt_backups():
    """Create backup copies of original prompts if they don't exist."""
    prompt_files = {
        "mcq_generator": "prompts/mcq.generator.txt",
        "mcq_formatter": "prompts/mcq.formatter.txt", 
        "nmcq_generator": "prompts/nonmcq.generator.txt",
        "nmcq_formatter": "prompts/nonmcq.formatter.txt",
        "summary_generator": "prompts/summarybytes.generator.txt",
        "summary_formatter": "prompts/summarybytes.formatter.txt"
    }
    
    for key, filepath in prompt_files.items():
        original_path = Path(filepath)
        backup_path = Path(filepath.replace('.txt', '.default.txt'))
        
        # Create backup if it doesn't exist
        if original_path.exists() and not backup_path.exists():
            try:
                import shutil
                shutil.copy2(original_path, backup_path)
                logger.info(f"Created backup for {key} at {backup_path}")
            except Exception as e:
                logger.error(f"Failed to create backup for {key}: {e}")

# Create backups on startup
create_prompt_backups()


class RunRequest(BaseModel):
    """Request model for the /run endpoint."""
    content_type: Literal["MCQ", "NMCQ", "SUMMARY"] = Field(
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
        max_length=500000
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
    # Separate temperature and top-p for generator and formatter
    generator_temperature: Optional[float] = Field(
        None,
        description="Temperature for generator model (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    generator_top_p: Optional[float] = Field(
        None,
        description="Top-p sampling for generator model (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    formatter_temperature: Optional[float] = Field(
        None,
        description="Temperature for formatter model (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    formatter_top_p: Optional[float] = Field(
        None,
        description="Top-p sampling for formatter model (0.0 to 1.0)",
        ge=0.0,
        le=1.0
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


class UserRole(str):
    """User role enumeration."""
    ADMIN = "admin"
    EDITOR = "editor"


def create_jwt_token(role: str = "editor") -> str:
    """Create a JWT token with role."""
    expiration = datetime.utcnow() + JWT_EXPIRATION_DELTA
    payload = {
        "exp": expiration,
        "iat": datetime.utcnow(),
        "authorized": True,
        "role": role
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("authorized", False):
            return {"authorized": True, "role": payload.get("role", "editor")}
        return {"authorized": False, "role": None}
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
        return {"authorized": False, "role": None}


def verify_auth(request: Request, authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify authentication via JWT Bearer token and return user info.
    """
    # No password required - allow access as admin in dev mode
    if not settings.editor_password and not settings.admin_password:
        return {"authorized": True, "role": "admin"}
    
    # Check Bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        auth_info = verify_jwt_token(token)
        if auth_info["authorized"]:
            return auth_info
    
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


@app.post("/run/stream")
@limiter.limit("10 per minute")
async def run_pipeline_stream(
    request: Request,
    run_request: RunRequest,
    auth_info: dict = Depends(verify_auth)
):
    """
    Streaming endpoint for content generation pipeline.
    Returns Server-Sent Events with progress updates.
    """
    logger.info(
        "stream_request_received",
        content_type=run_request.content_type,
        generator_model=run_request.generator_model,
        num_questions=run_request.num_questions,
        input_length=len(run_request.input_text)
    )
    
    # Validate that the selected model is allowed for this user
    user_role = auth_info.get("role", "editor")
    if not ModelManager.is_model_allowed(run_request.generator_model, user_role):
        logger.warning(
            "model_access_denied",
            model=run_request.generator_model,
            user_role=user_role
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Model '{run_request.generator_model}' is not available for your role"
        )
    
    async def generate_events() -> AsyncGenerator:
        try:
            # Yield initial event
            yield {
                "event": "start",
                "data": json.dumps({
                    "message": "Starting content generation...",
                    "stage": "init"
                })
            }
            
            # Run the pipeline with streaming
            async for event in pipeline.run_stream(
                content_type=run_request.content_type,
                generator_model=run_request.generator_model,
                input_text=run_request.input_text,
                num_questions=run_request.num_questions,
                focus_areas=run_request.focus_areas,
                generator_temperature=run_request.generator_temperature,
                generator_top_p=run_request.generator_top_p,
                formatter_temperature=run_request.formatter_temperature,
                formatter_top_p=run_request.formatter_top_p
            ):
                yield event
                
        except Exception as e:
            logger.error("stream_request_failed", error=str(e))
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": f"Pipeline execution failed: {str(e)}"
                })
            }
    
    return EventSourceResponse(generate_events())


@app.post("/run", response_model=RunResponse)
@limiter.limit("10 per minute")
async def run_pipeline(
    request: Request,
    run_request: RunRequest,
    auth_info: dict = Depends(verify_auth)
):
    """
    Main endpoint to run the content generation pipeline.
    
    Args:
        request: The run request with input parameters
        auth_info: Authorization info with user role
        
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
    
    # Validate that the selected model is allowed for this user
    user_role = auth_info.get("role", "editor")
    if not ModelManager.is_model_allowed(run_request.generator_model, user_role):
        logger.warning(
            "model_access_denied",
            model=run_request.generator_model,
            user_role=user_role
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Model '{run_request.generator_model}' is not available for your role"
        )
    
    try:
        # Run the pipeline with current saved prompts and separate temperature/top-p settings
        result = pipeline.run(
            content_type=run_request.content_type,
            generator_model=run_request.generator_model,
            input_text=run_request.input_text,
            num_questions=run_request.num_questions,
            focus_areas=run_request.focus_areas,
            generator_temperature=run_request.generator_temperature,
            generator_top_p=run_request.generator_top_p,
            formatter_temperature=run_request.formatter_temperature,
            formatter_top_p=run_request.formatter_top_p
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
    """Handle login and return JWT token with role."""
    # Development mode - no passwords set
    if not settings.editor_password and not settings.admin_password:
        token = create_jwt_token("admin")
        return {
            "success": True,
            "message": "Logged in (dev mode)",
            "token": token,
            "role": "admin"
        }
    
    # Check if admin password
    if settings.admin_password and login_request.password == settings.admin_password:
        token = create_jwt_token("admin")
        return {
            "success": True,
            "message": "Logged in successfully",
            "token": token,
            "role": "admin"
        }
    
    # Check if editor password
    if settings.editor_password and login_request.password == settings.editor_password:
        token = create_jwt_token("editor")
        return {
            "success": True,
            "message": "Logged in successfully",
            "token": token,
            "role": "editor"
        }
    
    # Invalid password
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )


@app.get("/api/auth/check")
async def check_auth(authorization: Optional[str] = Header(None)):
    """Check if user is authenticated and return role."""
    # No password required - authenticated as admin in dev mode
    if not settings.editor_password and not settings.admin_password:
        return {"authenticated": True, "role": "admin"}
    
    # Check Bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        auth_info = verify_jwt_token(token)
        if auth_info["authorized"]:
            return {"authenticated": True, "role": auth_info["role"]}
    
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
async def get_prompts(auth_info: dict = Depends(verify_auth)):
    """Get all current prompt templates (admin only)."""
    # Only admins can view prompts
    if auth_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view prompt templates"
        )
    
    prompts = {}
    prompt_files = {
        "mcq_generator": "prompts/mcq.generator.txt",
        "mcq_formatter": "prompts/mcq.formatter.txt", 
        "nmcq_generator": "prompts/nonmcq.generator.txt",
        "nmcq_formatter": "prompts/nonmcq.formatter.txt",
        "summary_generator": "prompts/summarybytes.generator.txt",
        "summary_formatter": "prompts/summarybytes.formatter.txt"
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


@app.get("/api/prompts/defaults")
async def get_default_prompts(auth_info: dict = Depends(verify_auth)):
    """Get original default prompt templates (admin only)."""
    # Only admins can view prompts
    if auth_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view prompt templates"
        )
    
    prompts = {}
    # Try to load from backup files first, fallback to current if backup doesn't exist
    prompt_files = {
        "mcq_generator": ("prompts/mcq.generator.default.txt", "prompts/mcq.generator.txt"),
        "mcq_formatter": ("prompts/mcq.formatter.default.txt", "prompts/mcq.formatter.txt"), 
        "nmcq_generator": ("prompts/nonmcq.generator.default.txt", "prompts/nonmcq.generator.txt"),
        "nmcq_formatter": ("prompts/nonmcq.formatter.default.txt", "prompts/nonmcq.formatter.txt"),
        "summary_generator": ("prompts/summarybytes.generator.default.txt", "prompts/summarybytes.generator.txt"),
        "summary_formatter": ("prompts/summarybytes.formatter.default.txt", "prompts/summarybytes.formatter.txt")
    }
    
    for key, (default_path, fallback_path) in prompt_files.items():
        try:
            # Try default backup first
            file_path = Path(default_path)
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompts[key] = f.read()
            else:
                # Fallback to current file if backup doesn't exist
                file_path = Path(fallback_path)
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        prompts[key] = f.read()
                else:
                    prompts[key] = f"Error: No prompt file found"
        except Exception as e:
            prompts[key] = f"Error loading prompt: {str(e)}"
    
    return prompts


@app.post("/api/prompts/reset")
async def reset_prompts_to_defaults(auth_info: dict = Depends(verify_auth)):
    """Reset all prompts to their original defaults (admin only)."""
    # Only admins can reset prompts
    if auth_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reset prompt templates"
        )
    
    prompt_files = {
        "mcq_generator": ("prompts/mcq.generator.default.txt", "prompts/mcq.generator.txt"),
        "mcq_formatter": ("prompts/mcq.formatter.default.txt", "prompts/mcq.formatter.txt"), 
        "nmcq_generator": ("prompts/nonmcq.generator.default.txt", "prompts/nonmcq.generator.txt"),
        "nmcq_formatter": ("prompts/nonmcq.formatter.default.txt", "prompts/nonmcq.formatter.txt"),
        "summary_generator": ("prompts/summarybytes.generator.default.txt", "prompts/summarybytes.generator.txt"),
        "summary_formatter": ("prompts/summarybytes.formatter.default.txt", "prompts/summarybytes.formatter.txt")
    }
    
    reset_count = 0
    errors = []
    
    for key, (default_path, current_path) in prompt_files.items():
        try:
            default_file = Path(default_path)
            current_file = Path(current_path)
            
            if default_file.exists():
                # Copy default back to current
                import shutil
                shutil.copy2(default_file, current_file)
                reset_count += 1
                logger.info(f"Reset {key} to default")
            else:
                errors.append({"key": key, "error": "Default file not found"})
        except Exception as e:
            errors.append({"key": key, "error": str(e)})
            logger.error(f"Failed to reset {key}: {e}")
    
    return {
        "success": len(errors) == 0,
        "reset_count": reset_count,
        "errors": errors,
        "message": f"Successfully reset {reset_count} prompts to defaults" if reset_count > 0 else "No prompts were reset"
    }


@app.post("/api/prompts")
async def update_prompts(
    prompts: dict,
    auth_info: dict = Depends(verify_auth)
):
    """Update prompt templates (admin only)."""
    # Only admins can update prompts
    if auth_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update prompt templates"
        )
    
    prompt_files = {
        "mcq_generator": "prompts/mcq.generator.txt",
        "mcq_formatter": "prompts/mcq.formatter.txt", 
        "nmcq_generator": "prompts/nonmcq.generator.txt",
        "nmcq_formatter": "prompts/nonmcq.formatter.txt",
        "summary_generator": "prompts/summarybytes.generator.txt",
        "summary_formatter": "prompts/summarybytes.formatter.txt"
    }
    
    updated = []
    errors = []
    
    for key, content in prompts.items():
        if key in prompt_files:
            try:
                file_path = Path(prompt_files[key])
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated.append(key)
            except Exception as e:
                errors.append({"key": key, "error": str(e)})
    
    return {
        "success": len(errors) == 0,
        "updated": updated,
        "errors": errors
    }


@app.get("/api/settings")
async def get_settings(auth_info: dict = Depends(verify_auth)):
    """Get advanced settings (admin only)."""
    # Only admins can view settings
    if auth_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view advanced settings"
        )
    
    return {
        "temperature": settings.model_temperature,
        "top_p": settings.model_top_p,
        "max_tokens": settings.model_max_tokens,
        "max_formatter_retries": settings.max_formatter_retries,
        "models": {
            "claude": settings.claude_model,
            "gemini_pro": settings.gemini_pro,
            "gemini_flash": settings.gemini_flash
        }
    }


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
            "prompts": "/api/prompts",
            "models": "/api/models"
        }
    }


@app.get("/api/models")
async def get_models(auth_info: dict = Depends(verify_auth)):
    """
    Get available models based on user role and restrictions.
    """
    # Get available API keys
    api_keys = {
        "GOOGLE_API_KEY": settings.google_api_key,
        "ANTHROPIC_API_KEY": settings.anthropic_api_key
    }
    
    # Get models available to this user
    available_models = ModelManager.get_available_models(
        user_role=auth_info.get("role", "editor"),
        api_keys=api_keys
    )
    
    # Get current restrictions (for admin view)
    restrictions = ModelManager.load_restrictions() if auth_info.get("role") == "admin" else None
    
    return {
        "models": available_models,
        "all_models": ALL_MODELS if auth_info.get("role") == "admin" else None,
        "restrictions": restrictions
    }


class ModelRestrictionsRequest(BaseModel):
    """Request body for updating model restrictions."""
    enabled: bool = Field(..., description="Whether model restrictions are enabled")
    allowed_models: list[str] = Field(default=[], description="List of allowed model IDs for non-admin users")


@app.post("/api/models/restrictions")
async def update_model_restrictions(
    request: ModelRestrictionsRequest,
    auth_info: dict = Depends(verify_auth)
):
    """
    Update model restrictions (admin only).
    """
    # Check if user is admin
    if auth_info.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update model restrictions"
        )
    
    # Update restrictions
    success = ModelManager.update_restrictions(
        enabled=request.enabled,
        allowed_models=request.allowed_models
    )
    
    if success:
        return {
            "success": True,
            "message": "Model restrictions updated successfully",
            "restrictions": ModelManager.load_restrictions()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update model restrictions"
        )


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

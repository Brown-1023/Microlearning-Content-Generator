"""
Application configuration and settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    # Authentication
    app_secret: str = Field(default="development-secret", env="APP_SECRET")
    editor_password: str = Field(default="", env="EDITOR_PASSWORD")
    admin_password: str = Field(default="", env="ADMIN_PASSWORD")
    
    # Model Configuration
    # Using the correct model names as specified in requirements:
    # - Claude Sonnet 4.5 -> claude-sonnet-4-5-20250929
    # - Gemini 2.5 Pro -> gemini-2.5-pro
    # - Gemini 2.5 Flash -> gemini-2.5-flash
    claude_model: str = Field(
        default="claude-sonnet-4-5-20250929", 
        env="CLAUDE_MODEL"
    )
    gemini_pro: str = Field(
        default="gemini-2.5-pro", 
        env="GEMINI_PRO"
    )
    gemini_flash: str = Field(
        default="gemini-2.5-flash", 
        env="GEMINI_FLASH"
    )
    
    # Pipeline Configuration
    max_formatter_retries: int = Field(default=1, env="MAX_FORMATTER_RETRIES")
    max_input_chars: int = Field(default=500000, env="MAX_INPUT_CHARS")
    
    # Model parameters (configurable as per requirements)
    model_temperature: float = Field(default=0.51, env="MODEL_TEMPERATURE")
    model_top_p: float = Field(default=0.95, env="MODEL_TOP_P")
    model_max_tokens: int = Field(default=8000, env="MODEL_MAX_TOKENS")
    model_timeout: int = Field(default=60, env="MODEL_TIMEOUT")
    
    # Request size limit (in MB)
    max_request_size_mb: int = Field(default=10, env="MAX_REQUEST_SIZE_MB")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    # Use PORT env var (Cloud Run sets this) or default to 4000
    port: int = Field(default=4000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://localhost:4000",
        "https://microlearning-content-generator-frontend-4ui6bm2vf.vercel.app",
        "https://microlearning-content-generator-f-git-7602dd-content-generation.vercel.app"
        
    ]
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=10, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: str = Field(default="minute", env="RATE_LIMIT_PERIOD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Project paths
PROJECT_ROOT = Path(__file__).parent
STATIC_DIR = PROJECT_ROOT / "static"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
SAMPLES_DIR = PROJECT_ROOT / "samples"

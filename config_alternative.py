"""
Alternative configuration with currently available model names.
Use this if the models in config.py are not available.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class AlternativeSettings(BaseSettings):
    """Alternative settings with currently available model names."""
    
    # API Keys
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    # Authentication
    app_secret: str = Field(default="development-secret", env="APP_SECRET")
    editor_password: str = Field(default="", env="EDITOR_PASSWORD")
    
    # Model Configuration - Using currently available models
    # Note: These are the actual available models as of 2024
    # If the requirements specify different models, they might be future versions
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",  # Latest Claude 3.5 Sonnet
        env="CLAUDE_MODEL"
    )
    gemini_pro: str = Field(
        default="gemini-1.5-pro-latest",  # Currently available Gemini Pro
        env="GEMINI_PRO"
    )
    gemini_flash: str = Field(
        default="gemini-1.5-flash-latest",  # Currently available Gemini Flash
        env="GEMINI_FLASH"
    )
    
    # Alternative model names (if -latest versions don't work)
    # gemini_pro: str = Field(default="gemini-1.5-pro", env="GEMINI_PRO")
    # gemini_flash: str = Field(default="gemini-1.5-flash", env="GEMINI_FLASH")
    
    # Pipeline Configuration
    max_formatter_retries: int = Field(default=1, env="MAX_FORMATTER_RETRIES")
    max_input_chars: int = Field(default=150000, env="MAX_INPUT_CHARS")
    
    # Model parameters (configurable as per requirements)
    model_temperature: float = Field(default=0.51, env="MODEL_TEMPERATURE")
    model_top_p: float = Field(default=0.95, env="MODEL_TOP_P")
    model_max_tokens: int = Field(default=8000, env="MODEL_MAX_TOKENS")
    model_timeout: int = Field(default=60, env="MODEL_TIMEOUT")
    
    # Request size limit (in MB)
    max_request_size_mb: int = Field(default=10, env="MAX_REQUEST_SIZE_MB")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=4000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://localhost:4000"
    ]
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=10, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: str = Field(default="minute", env="RATE_LIMIT_PERIOD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
alternative_settings = AlternativeSettings()

# Project paths
PROJECT_ROOT = Path(__file__).parent
STATIC_DIR = PROJECT_ROOT / "static"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
SAMPLES_DIR = PROJECT_ROOT / "samples"

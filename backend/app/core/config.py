# backend/app/core/config.py

import secrets
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator
from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Code Review"
    DEBUG: bool = False
    
    # Authentication
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Cookie Settings
    COOKIE_SECURE: bool = True  # Set to False in development
    COOKIE_DOMAIN: Optional[str] = None
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_CALLBACK_URL: str = "http://localhost:3000/auth/callback"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # LLM Service
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # Analysis Settings
    MAX_FILE_SIZE: int = 500_000  # 500KB
    SUPPORTED_LANGUAGES: list = [
        "python", "javascript", "typescript", "java", "go",
        "rust", "cpp", "c", "csharp", "php", "ruby"
    ]
    IGNORE_FILES: list = [
        ".min.js", ".min.css", "package-lock.json",
        "yarn.lock", ".map", ".pyc", "__pycache__"
    ]
    
    # Cache Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Webhook Settings
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "app.log"
    
    # Performance
    WORKERS_PER_CORE: int = 1
    MAX_WORKERS: int = 4
    KEEPALIVE: int = 120
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Environment-specific configurations
def get_environment_config():
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return {
            "DEBUG": False,
            "COOKIE_SECURE": True,
            "LOG_LEVEL": "WARNING",
            "BACKEND_CORS_ORIGINS": [
                "https://your-production-domain.com"
            ]
        }
    
    elif env == "staging":
        return {
            "DEBUG": True,
            "COOKIE_SECURE": True,
            "LOG_LEVEL": "INFO",
            "BACKEND_CORS_ORIGINS": [
                "https://staging.your-domain.com"
            ]
        }
    
    else:  # development
        return {
            "DEBUG": True,
            "COOKIE_SECURE": False,
            "LOG_LEVEL": "DEBUG",
            "BACKEND_CORS_ORIGINS": [
                "http://localhost:3000",
                "http://localhost:8000"
            ]
        }

# Update settings with environment-specific configurations
env_config = get_environment_config()
for key, value in env_config.items():
    setattr(settings, key, value)
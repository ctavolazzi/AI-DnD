"""Application configuration using pydantic-settings."""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Sprite Enhancer"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database
    database_url: str = "postgresql://sprite_user:sprite_pass@localhost:5432/sprite_db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    # API Keys
    pixellab_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Storage
    storage_backend: str = "local"  # "local" or "s3"
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Local storage path
    upload_dir: str = "uploads"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()


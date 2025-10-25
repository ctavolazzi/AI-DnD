"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings
from typing import Tuple


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "sqlite:///./dnd_game.db"

    # Storage
    IMAGE_STORAGE_DIR: str = "images"
    MAX_IMAGE_SIZE_MB: int = 5
    MAX_IMAGES_PER_ITEM: int = 20

    # Caching
    CACHE_EXPIRY_DAYS: int = 7

    # API
    GEMINI_API_KEY: str
    MAX_REQUESTS_PER_MINUTE: int = 10

    # Image processing
    THUMBNAIL_SIZE: Tuple[int, int] = (200, 200)
    WEBP_QUALITY: int = 85

    # Backup
    BACKUP_RETENTION_DAYS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


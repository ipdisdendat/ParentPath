"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database (SQLite default for zero setup, PostgreSQL for production)
    database_url: str = "sqlite:///parentpath.db"

    # Gemini Mode (CLI for free tier, API for production)
    use_gemini_cli: bool = True

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    # Gemini AI
    gemini_api_key: Optional[str] = None

    # WhatsApp
    whatsapp_phone_id: Optional[str] = None
    whatsapp_token: Optional[str] = None

    # Twilio
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None

    # MinIO
    minio_url: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "parentpath"

    # Security
    jwt_secret: str = "change_me_in_production"
    admin_username: str = "admin"
    admin_password: str = "change_me"

    # Application
    app_env: str = "development"
    log_level: str = "INFO"

    # Feature Flags
    enable_multilingual: bool = True
    enable_gamification: bool = True
    enable_voice_messages: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

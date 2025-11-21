"""
Application configuration and environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, AnyUrl
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    # Application
    APP_NAME: str = "2FA Application"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    
    # Email configuration (FastAPI-Mail-compatible)
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[EmailStr] = None
    MAIL_FROM_NAME: str = "2FA-App"
    MAIL_SERVER: Optional[str] = "2fa_mailhog"
    MAIL_PORT: Optional[int] = 1025
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: Optional[bool] = None  # if not provided, we'll compute
    
    # 2FA configuration
    TWO_FA_CODE_TTL_SECONDS: int = 180  # in seconds (2-5 minutes -> set 120-300)
    TWO_FA_RESEND_SECONDS: int = 60     # minimal seconds between sends
    TWO_FA_MAX_ATTEMPTS: int = 5
    TWO_FA_BLOCK_INITIAL_MINUTES: int = 30
    
    # TMP TOKEN
    TMP_TOKEN_EXPIRE_MINUTES: int = 5
    
    # Redis (optional)
    REDIS_URL: Optional[AnyUrl] = None  # e.g. redis://redis:6379/0
    
    @property
    def cors_origins(self) -> List[str]:
        """Returns list of allowed origins for CORS."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Singleton settings instance
settings = Settings()

"""
Application configuration and environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, AnyUrl
from typing import List, Optional
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="allow", case_sensitive=True)
    
    APP_NAME: str = "2FA Application"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    
    DATABASE_URL: str
    PUBLIC_BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:8501"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[EmailStr] = None
    MAIL_FROM_NAME: str = "2FA-App"
    
    MAIL_SERVER: Optional[str] = "smtp.gmail.com"
    MAIL_PORT: Optional[int] = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    USE_CREDENTIALS: Optional[bool] = None
    
    TWO_FA_CODE_TTL_SECONDS: int = 180
    TWO_FA_RESEND_SECONDS: int = 60
    TWO_FA_MAX_ATTEMPTS: int = 5
    TWO_FA_BLOCK_INITIAL_MINUTES: int = 30
    
    TMP_TOKEN_EXPIRE_MINUTES: int = 5

    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"
    GOOGLE_SCOPE: str = "openid email profile"
    GOOGLE_CLIENT_ID: str = "test_client_id"
    GOOGLE_CLIENT_SECRET: str = "test_client_secret"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    FRONTEND_BASE_URL: str = "http://localhost:8501"

    REDIS_URL: Optional[AnyUrl] = None
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()

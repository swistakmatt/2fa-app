"""
Application configuration and environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    # Application
    APP_NAME: str = "2FA Application"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    
    # Email (for future 2FA implementation)
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = ""
    MAIL_FROM_NAME: str = "2FA Application"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    # TOTP (for future 2FA implementation)
    TOTP_ISSUER: str = "2FA-App"
    TOTP_PERIOD: int = 30
    
    @property
    def cors_origins(self) -> List[str]:
        """Returns list of allowed origins for CORS."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Singleton settings instance
settings = Settings()

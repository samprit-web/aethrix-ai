from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "AETHRIX AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DOMAIN: str = "aethrix.ai"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://aethrix.ai", "https://www.aethrix.ai"]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "aethrix"
    POSTGRES_PASSWORD: str = "aethrix"
    POSTGRES_DB: str = "aethrix"
    DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # AI Models - Open Source, self-hostable
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_CHAT_MODEL: str = "llama-3.1-8b"
    DEFAULT_IMAGE_MODEL: str = "stable-diffusion-xl"
    
    # Storage
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Features
    ENABLE_REGISTRATION: bool = True
    ENABLE_PREMIUM: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

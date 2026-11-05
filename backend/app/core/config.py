from pydantic import BaseSettings
from typing import List, Optional
import secrets
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AETHRIX AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DOMAIN: str = "aethrix.ai"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "aethrix"
    POSTGRES_PASSWORD: str = "aethrix"
    POSTGRES_DB: str = "aethrix"
    DATABASE_URL: Optional[str] = None

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_CHAT_MODEL: str = "llama3.1"
    DEFAULT_IMAGE_MODEL: str = "stable-diffusion-xl"

    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024

    RATE_LIMIT_PER_MINUTE: int = 60

    ENABLE_REGISTRATION: bool = True
    ENABLE_PREMIUM: bool = True

    @property
    def sql_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # SQLite fallback for easy local/dev use when Postgres is unavailable.
        return os.getenv("AETHRIX_SQLITE_URL", "sqlite:///./aethrix.db")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

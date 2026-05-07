from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os

# En Docker, on ne charge pas le .env (les vars viennent du docker-compose)
# En local, on charge le .env à la racine du projet
ENV_FILE = Path(__file__).parent.parent.parent / ".env"
USE_ENV_FILE = str(ENV_FILE) if not os.getenv("DOCKER_ENV") and ENV_FILE.exists() else None

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_PASSWORD: str = ""

    # API
    PROJECT_NAME: str = "ObRail Europe API"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    API_KEY: str = "obrail-api-key-2026"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = USE_ENV_FILE
        case_sensitive = True
        extra = "ignore"

settings = Settings()
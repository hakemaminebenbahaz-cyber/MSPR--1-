from pydantic_settings import BaseSettings

from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
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
        env_file = ".env"
        case_sensitive = True

settings = Settings()
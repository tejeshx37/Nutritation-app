from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Personal AI Nutritionist"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/nutrition_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # FatSecret API
    FATSECRET_CLIENT_ID: Optional[str] = None
    FATSECRET_CLIENT_SECRET: Optional[str] = None
    FATSECRET_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # NLP Models
    SPACY_MODEL: str = "en_core_web_sm"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure required environment variables are set
def validate_settings():
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "FATSECRET_CLIENT_ID",
        "FATSECRET_CLIENT_SECRET",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing required environment variables: {missing_vars}")
        print("Please set these in your .env file")
    
    return len(missing_vars) == 0

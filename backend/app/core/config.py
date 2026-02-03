import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PulseLink API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "firebase-service-account.json"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "https://pulse-link.vercel.app"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
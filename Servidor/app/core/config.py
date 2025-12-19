"""
Smart Classroom AI - Core Configuration
Load and validate environment variables
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Smart Classroom AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    API_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    CORS_METHODS: str = "GET,POST,PUT,DELETE"
    CORS_HEADERS: str = "*"
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str | None = None
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # DeepFace
    FACE_DETECTOR_BACKEND: str = "retinaface"
    FACE_RECOGNITION_MODEL: str = "Facenet"
    EMOTION_MODEL: str = "default"
    DISTANCE_METRIC: str = "euclidean"
    
    # Thresholds
    FACE_MATCH_THRESHOLD: float = 0.6
    EMOTION_CONFIDENCE_THRESHOLD: float = 0.7
    MIN_FACE_SIZE: int = 80
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    WEIGHTS_DIR: str = "./weights"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Feature Flags
    ENABLE_EMOTION_ANALYSIS: bool = True
    ENABLE_MULTI_FACE_DETECTION: bool = True
    ENABLE_AUTO_REPORTS: bool = True
    
    # Performance
    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT: int = 30
    BATCH_SIZE: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance (singleton pattern)"""
    return Settings()


# Global settings instance
settings = get_settings()

"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Horoscope & Saju Fortune Service"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./fortune.db"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 500
    
    # Models
    horoscope_model_path: str = "./models/horoscope"
    saju_model_path: str = "./models/saju"
    enable_model_cache: bool = True
    
    # Fusion Engine
    horoscope_weight: float = 0.5
    saju_weight: float = 0.5
    
    # Caching
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 86400
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    api_rate_limit: int = 10
    
    # Retraining
    min_feedback_count: int = 1000
    min_average_rating: float = 3.0
    auto_retrain_enabled: bool = False
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": ('settings_',)
    }


# Global settings instance
settings = Settings()

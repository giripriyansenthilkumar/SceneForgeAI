"""
SceneForge AI - Application Configuration
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SceneForge AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://sceneforge_admin:sceneforge_secure_dev_password@localhost:5432/sceneforge"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev_secret_jwt_sceneforge_key_replace_in_prod")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

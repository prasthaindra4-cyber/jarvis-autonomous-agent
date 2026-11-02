import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "JARVIS Autonomous AI Agent Core"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # LLM Configuration
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    PRIMARY_LLM_PROVIDER: str = "gemini"  # "gemini" | "openai" | "mock"
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_FLASH_MODEL: str = "gemini-3.8-flash"
    
    # Execution & Workflow
    MAX_SELF_CORRECTION_RETRIES: int = 2
    ASYNC_CONCURRENCY_LIMIT: int = 5
    
    # Memory Storage
    SQLITE_DB_PATH: str = "jarvis_memory.db"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

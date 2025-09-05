"""
Configuration settings for the Aura Desktop Assistant API
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    ENABLE_DOCS: bool = Field(default=True, env="ENABLE_DOCS")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],  # Allow all origins for development
        env="ALLOWED_ORIGINS"
    )
    
    # File System Configuration
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=[".txt", ".md", ".json", ".csv", ".xlsx", ".xls", ".pdf"],
        env="ALLOWED_FILE_EXTENSIONS"
    )
    SAFE_DIRECTORIES: List[str] = Field(
        default=["./documents", "./data", "./temp"],
        env="SAFE_DIRECTORIES"
    )
    
    # Hugging Face Configuration
    HF_API_TOKEN: str = Field(default="", env="HF_API_TOKEN")
    HF_API_URL: str = Field(
        default="https://api-inference.huggingface.co/models",
        env="HF_API_URL"
    )
    HF_SUMMARIZATION_MODEL: str = Field(
        default="facebook/bart-large-cnn",
        env="HF_SUMMARIZATION_MODEL"
    )
    HF_QA_MODEL: str = Field(
        default="deepset/roberta-base-squad2",
        env="HF_QA_MODEL"
    )
    
    # Request Configuration
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    RETRY_DELAY: float = Field(default=1.0, env="RETRY_DELAY")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")  # json or console
    
    # Security Configuration
    ENABLE_RATE_LIMITING: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
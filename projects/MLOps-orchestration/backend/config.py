"""
Core configuration and utilities for the Conversational MLOps Agent.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google APIs
    google_application_credentials: Optional[str] = None
    google_cloud_project: Optional[str] = None
    
    # LangChain
    langchain_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    langchain_tracing_v2: bool = False
    
    # Prefect
    prefect_api_url: str = "http://localhost:4200/api"
    prefect_api_key: Optional[str] = None
    
    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "conversational-mlops"
    
    # Backend
    backend_host: str = "localhost"
    backend_port: int = 8000
    
    # Frontend
    react_app_api_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

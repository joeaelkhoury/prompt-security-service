# src/core/config.py
"""Configuration management."""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

from src.core.exceptions import ConfigurationException


@dataclass
class Settings:
    """Application settings."""
    # Azure OpenAI - Required
    azure_api_key: str
    azure_endpoint: str
    azure_api_version: str
    azure_chat_deployment: str
    azure_embedding_deployment: str
    
    azure_chat_cheaper_deployment: Optional[str] = None
    log_level: str = "INFO"
    max_prompt_length: int = 2000
    similarity_threshold: float = 0.7
    secret_key: str = "default-secret-key"
    allowed_hosts: str = "localhost,127.0.0.1"
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    database_url: str = "postgresql://user:password@localhost/prompt_security"
    redis_host: str = "localhost"
    redis_port: int = 6379
    jwt_secret_key: str = "your-secret-key-change-this"
    api_key_salt: str = "your-salt-change-this"
    connection_pool_size: int = 20
    connection_pool_max_overflow: int = 40
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        # Load .env file
        load_dotenv()
        
        # Required Azure settings
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        azure_chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        azure_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
        
        # Check required variables
        missing_vars = []
        if not azure_api_key:
            missing_vars.append("AZURE_OPENAI_API_KEY")
        if not azure_endpoint:
            missing_vars.append("AZURE_OPENAI_ENDPOINT")
        if not azure_api_version:
            missing_vars.append("AZURE_OPENAI_API_VERSION")
        if not azure_chat_deployment:
            missing_vars.append("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        if not azure_embedding_deployment:
            missing_vars.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
        
        if missing_vars:
            raise ConfigurationException(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please create a .env file with these variables."
            )
        
        return cls(
            azure_api_key=azure_api_key,
            azure_endpoint=azure_endpoint,
            azure_api_version=azure_api_version,
            azure_chat_deployment=azure_chat_deployment,
            azure_embedding_deployment=azure_embedding_deployment,
            azure_chat_cheaper_deployment=os.getenv("AZURE_OPENAI_CHAT_CHEAPER_DEPLOYMENT_NAME"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_prompt_length=int(os.getenv("MAX_PROMPT_LENGTH", "2000")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7")),
            secret_key=os.getenv("SECRET_KEY", "default-secret-key"),
            allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1"),
            rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "3600")),
            database_url=os.getenv("DATABASE_URL", "postgresql://user:password@localhost/prompt_security"),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this"),
            api_key_salt=os.getenv("API_KEY_SALT", "your-salt-change-this"),
            connection_pool_size=int(os.getenv("CONNECTION_POOL_SIZE", "20")),
            connection_pool_max_overflow=int(os.getenv("CONNECTION_POOL_MAX_OVERFLOW", "40"))
        )
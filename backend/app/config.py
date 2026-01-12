"""Configuration settings loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI API (Standard OpenAI, not Azure)
    openai_api_key: str
    openai_model: str = "gpt-4"  # or "gpt-4-turbo", "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-ada-002"
    
    # Azure AI Search
    azure_search_endpoint: str
    azure_search_api_key: str
    azure_search_index_name: str
    
    # Azure Storage
    azure_storage_connection_string: str
    azure_storage_container_name: str = "documents"
    
    # Azure AD (optional)
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    
    # Application
    api_v1_prefix: str = "/api"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    debug: bool = False
    
    # Caching
    cache_backend: str = "memory"  # "memory" or "redis"
    cache_max_size: int = 1000  # For in-memory cache
    redis_url: Optional[str] = None  # Redis connection URL (e.g., "redis://localhost:6379/0")
    cache_query_ttl: int = 3600  # Query response cache TTL in seconds (1 hour)
    cache_embedding_ttl: int = 86400  # Embedding cache TTL in seconds (24 hours)
    enable_query_cache: bool = True  # Enable query response caching
    enable_embedding_cache: bool = True  # Enable embedding caching
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

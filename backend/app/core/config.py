from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Enterprise AI PDF Chat / RAG Assistant"
    app_env: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    backend_cors_origins: list[AnyHttpUrl] | list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/rag_assistant"
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_request_timeout_seconds: float = 10.0
    ollama_num_ctx: int = 4096
    ollama_keep_alive: str = "10m"

    chroma_collection_name: str = "enterprise_pdf_chunks_ollama"
    chroma_persist_dir: Path = Path("storage/chroma")
    upload_dir: Path = Path("storage/uploads")
    max_upload_size_mb: int = 50
    chunk_strategy: str = "recursive"
    chunk_size: int = 900
    chunk_overlap: int = 120
    retrieval_top_k: int = 5
    conversation_window_messages: int = 10

    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    cache_ttl_seconds: int = 300

    sentry_dsn: str | None = None

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Any) -> Any:
        """Support comma-separated CORS origins from .env files."""
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Normalize hosted Postgres URLs to SQLAlchemy's asyncpg dialect."""
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://") and "+asyncpg" not in value:
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Cache settings for dependency injection."""
    return Settings()

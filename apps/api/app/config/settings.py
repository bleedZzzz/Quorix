"""Quorix API — Application configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_env: str = "development"
    app_name: str = "Quorix"
    log_level: str = "INFO"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://quorix:quorix_dev@localhost:5432/quorix"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Qdrant ───────────────────────────────────────────────────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "quorix_chunks"

    # ── Object Storage ───────────────────────────────────────────────────────
    storage_endpoint: str = "http://localhost:9000"
    storage_access_key: str = "quorix_minio"
    storage_secret_key: str = "quorix_minio_secret"
    storage_bucket: str = "quorix"
    storage_region: str = "us-east-1"

    # ── Authentication ───────────────────────────────────────────────────────
    jwt_secret: str = "change-this-to-a-random-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── AI Providers ─────────────────────────────────────────────────────────
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # ── External Search ──────────────────────────────────────────────────────
    tavily_api_key: str | None = None

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Create and return application settings (cached via lru_cache)."""
    return Settings()


settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]

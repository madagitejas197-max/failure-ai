"""
Application configuration — reads from environment / .env file.
All settings are validated by Pydantic on startup.
"""
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    environment: Literal["development", "staging", "production"] = "development"
    secret_key: str = "change-me-in-production"
    debug: bool = True
    app_name: str = "FailureAI"
    app_version: str = "0.1.0"

    # ── Database ─────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://failureai:failureai@localhost:5432/failureai"
    )

    # ── ChromaDB ─────────────────────────────────────────────
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── LLM Provider ─────────────────────────────────────────
    llm_provider: Literal["ollama", "gemini", "openai"] = "ollama"
    llm_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ── Auth ─────────────────────────────────────────────────
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def chroma_url(self) -> str:
        return f"http://{self.chroma_host}:{self.chroma_port}"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton)."""
    return Settings()

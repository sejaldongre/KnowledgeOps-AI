from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "KnowledgeOps AI"
    environment: str = "development"
    debug: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # -------------------------
    # LLM configuration
    # -------------------------

    llm_default_mode: str = "offline"

    # Online LLM - Groq
    groq_api_key: str | None = None
    online_llm_model: str = (
        "llama-3.3-70b-versatile"
    )

    # Offline LLM - Ollama
    ollama_base_url: str = (
        "http://localhost:11434"
    )
    offline_llm_model: str = "llama3.2:3b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""

    return Settings()

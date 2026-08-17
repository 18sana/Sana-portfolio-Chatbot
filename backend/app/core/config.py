from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # App
    app_env: str = Field(default="development", alias="APP_ENV")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
        description="Comma-separated list of allowed CORS origins",
    )

    # Infra
    database_url: str = Field(
        default="postgresql+asyncpg://portfolio:portfolio@localhost:5432/ai_portfolio",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        """Accept postgres:// or postgresql:// from Supabase/Render and force asyncpg."""
        if not isinstance(value, str) or not value:
            return value
        url = value.strip()
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = "postgresql+asyncpg://" + url[len("postgresql://") :]
        # Supabase usually needs TLS from hosted runtimes
        if "supabase.co" in url and "ssl=" not in url:
            url += ("&" if "?" in url else "?") + "ssl=require"
        return url

    # Auth
    admin_api_key: str = Field(default="", alias="ADMIN_API_KEY")

    # Uploads / rate limits
    max_upload_bytes: int = Field(default=5_000_000, alias="MAX_UPLOAD_BYTES")
    rate_limit_ip_per_minute: int = Field(default=60, alias="RATE_LIMIT_IP_PER_MINUTE")
    rate_limit_session_per_minute: int = Field(default=30, alias="RATE_LIMIT_SESSION_PER_MINUTE")
    rate_limit_jd_per_minute: int = Field(default=10, alias="RATE_LIMIT_JD_PER_MINUTE")
    retrieval_top_k: int = Field(default=4, alias="RETRIEVAL_TOP_K")
    # Extra LLM verify after each answer (slower). Heuristic still runs when False.
    verify_groundedness_llm: bool = Field(default=False, alias="VERIFY_GROUNDEDNESS_LLM")
    chat_max_tokens: int = Field(default=500, alias="CHAT_MAX_TOKENS")

    # LLM
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_api_base: str = Field(default="", alias="LLM_API_BASE")
    llm_fallback_provider: str = Field(default="", alias="LLM_FALLBACK_PROVIDER")
    llm_fallback_model: str = Field(default="", alias="LLM_FALLBACK_MODEL")
    llm_fallback_api_base: str = Field(default="", alias="LLM_FALLBACK_API_BASE")

    # Embeddings
    embedding_provider: str = Field(default="openai", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="EMBEDDING_MODEL",
    )
    embedding_api_base: str = Field(default="", alias="EMBEDDING_API_BASE")
    embedding_dimensions: int | None = Field(default=None, alias="EMBEDDING_DIMENSIONS")
    embedding_fallback_provider: str = Field(default="", alias="EMBEDDING_FALLBACK_PROVIDER")
    embedding_fallback_model: str = Field(default="", alias="EMBEDDING_FALLBACK_MODEL")
    embedding_fallback_api_base: str = Field(default="", alias="EMBEDDING_FALLBACK_API_BASE")

    @field_validator("embedding_dimensions", mode="before")
    @classmethod
    def empty_str_to_none(cls, value: object) -> object:
        if value == "" or value is None:
            return None
        return value

    # Keys
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")

    # Observability
    langfuse_public_key: str = Field(default="", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", alias="LANGFUSE_HOST")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "dev", "local"}


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Factory: build providers from Settings. Owns fallback wrapping."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.providers.base import EmbeddingProvider, LLMProvider
from app.providers.fallback import FallbackEmbeddingProvider, FallbackLLMProvider
from app.providers.litellm_embedding import LiteLLMEmbeddingProvider
from app.providers.litellm_llm import LiteLLMLLMProvider
from app.providers.model_ids import litellm_model_id


def resolve_api_key(settings: Settings, provider: str) -> str | None:
    """Map provider name to the configured API key (env-only)."""
    key = provider.strip().lower()
    mapping = {
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
        "google": settings.google_api_key,
        "gemini": settings.google_api_key,
        "openrouter": settings.openrouter_api_key,
    }
    value = mapping.get(key, "")
    return value or None


def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    """Construct an LLM provider from settings. No module-level singleton."""
    cfg = settings or get_settings()
    primary = _build_llm(
        provider=cfg.llm_provider,
        model=cfg.llm_model,
        api_base=cfg.llm_api_base or None,
        settings=cfg,
    )
    if cfg.llm_fallback_provider.strip() and cfg.llm_fallback_model.strip():
        fallback = _build_llm(
            provider=cfg.llm_fallback_provider,
            model=cfg.llm_fallback_model,
            api_base=cfg.llm_fallback_api_base or cfg.llm_api_base or None,
            settings=cfg,
        )
        return FallbackLLMProvider(primary, fallback)
    return primary


def get_embedding_provider(settings: Settings | None = None) -> EmbeddingProvider:
    """Construct an embedding provider from settings. No module-level singleton."""
    cfg = settings or get_settings()
    primary = _build_embedding(
        provider=cfg.embedding_provider,
        model=cfg.embedding_model,
        api_base=cfg.embedding_api_base or cfg.llm_api_base or None,
        dimensions=cfg.embedding_dimensions,
        settings=cfg,
    )
    if cfg.embedding_fallback_provider.strip() and cfg.embedding_fallback_model.strip():
        fallback = _build_embedding(
            provider=cfg.embedding_fallback_provider,
            model=cfg.embedding_fallback_model,
            api_base=cfg.embedding_fallback_api_base
            or cfg.embedding_api_base
            or cfg.llm_api_base
            or None,
            dimensions=cfg.embedding_dimensions,
            settings=cfg,
        )
        return FallbackEmbeddingProvider(primary, fallback)
    return primary


def _build_llm(
    *,
    provider: str,
    model: str,
    api_base: str | None,
    settings: Settings,
) -> LiteLLMLLMProvider:
    model_id = litellm_model_id(provider, model)
    return LiteLLMLLMProvider(
        model=model_id,
        api_key=resolve_api_key(settings, provider),
        api_base=api_base,
        provider_name=provider.strip().lower(),
    )


def _build_embedding(
    *,
    provider: str,
    model: str,
    api_base: str | None,
    dimensions: int | None,
    settings: Settings,
) -> LiteLLMEmbeddingProvider:
    model_id = litellm_model_id(provider, model)
    return LiteLLMEmbeddingProvider(
        model=model_id,
        api_key=resolve_api_key(settings, provider),
        api_base=api_base,
        provider_name=provider.strip().lower(),
        default_dimensions=dimensions,
    )

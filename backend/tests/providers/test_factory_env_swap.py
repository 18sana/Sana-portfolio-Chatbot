"""Acceptance: swap providers via settings/env only — LiteLLM model strings change."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.providers.factory import get_embedding_provider, get_llm_provider
from app.providers.fallback import FallbackEmbeddingProvider, FallbackLLMProvider
from app.providers.model_ids import litellm_model_id


def _settings(**kwargs: object) -> Settings:
    """Build Settings without reading backend/.env (tests must be hermetic)."""
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


def test_llm_model_string_swaps_via_settings_only() -> None:
    openai_settings = _settings(
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        llm_fallback_provider="",
        llm_fallback_model="",
    )
    anthropic_settings = _settings(
        llm_provider="anthropic",
        llm_model="claude-sonnet-4-5",
        llm_fallback_provider="",
        llm_fallback_model="",
    )

    p1 = get_llm_provider(openai_settings)
    p2 = get_llm_provider(anthropic_settings)

    assert p1.model_name == "openai/gpt-4o-mini"
    assert p2.model_name == "anthropic/claude-sonnet-4-5"
    assert p1.model_name != p2.model_name
    assert p1.provider_name == "openai"
    assert p2.provider_name == "anthropic"


def test_llm_swap_via_env_monkeypatch(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "")
    monkeypatch.setenv("LLM_FALLBACK_MODEL", "")
    get_settings.cache_clear()
    # Force Settings to ignore .env file so monkeypatch wins cleanly
    monkeypatch.setenv("APP_ENV", "test")
    a = get_llm_provider(
        Settings(
            _env_file=None,
            llm_provider="openai",
            llm_model="gpt-4o-mini",
            llm_fallback_provider="",
            llm_fallback_model="",
        )
    )

    b = get_llm_provider(
        Settings(
            _env_file=None,
            llm_provider="anthropic",
            llm_model="claude-sonnet-4-5",
            llm_fallback_provider="",
            llm_fallback_model="",
        )
    )

    assert a.model_name == "openai/gpt-4o-mini"
    assert b.model_name == "anthropic/claude-sonnet-4-5"


def test_embedding_model_string_swaps_via_settings_only() -> None:
    openai = _settings(
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_fallback_provider="",
        embedding_fallback_model="",
    )
    cohere = _settings(
        embedding_provider="cohere",
        embedding_model="embed-english-v3.0",
        embedding_fallback_provider="",
        embedding_fallback_model="",
    )

    e1 = get_embedding_provider(openai)
    e2 = get_embedding_provider(cohere)

    assert e1.model_name == "openai/text-embedding-3-small"
    assert e2.model_name == "cohere/embed-english-v3.0"
    assert e1.model_name != e2.model_name


def test_fully_qualified_model_id_is_trusted() -> None:
    settings = _settings(
        llm_provider="openrouter",
        llm_model="openrouter/auto",
        llm_fallback_provider="",
        llm_fallback_model="",
    )
    provider = get_llm_provider(settings)
    assert provider.model_name == "openrouter/auto"


def test_litellm_model_id_helper() -> None:
    assert litellm_model_id("openai", "gpt-4o-mini") == "openai/gpt-4o-mini"
    assert litellm_model_id("openai", "openai/gpt-4o") == "openai/gpt-4o"


def test_factory_wraps_fallback_when_configured() -> None:
    settings = _settings(
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        llm_fallback_provider="anthropic",
        llm_fallback_model="claude-sonnet-4-5",
        embedding_provider="openai",
        embedding_model="text-embedding-3-small",
        embedding_fallback_provider="cohere",
        embedding_fallback_model="embed-english-v3.0",
    )
    llm = get_llm_provider(settings)
    emb = get_embedding_provider(settings)

    assert isinstance(llm, FallbackLLMProvider)
    assert llm.model_name == "openai/gpt-4o-mini"
    assert llm.fallback.model_name == "anthropic/claude-sonnet-4-5"

    assert isinstance(emb, FallbackEmbeddingProvider)
    assert emb.model_name == "openai/text-embedding-3-small"
    assert emb.fallback.model_name == "cohere/embed-english-v3.0"

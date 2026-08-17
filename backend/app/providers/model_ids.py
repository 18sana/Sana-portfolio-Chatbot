"""Helpers for building LiteLLM model identifiers from env config."""

from __future__ import annotations


def litellm_model_id(provider: str, model: str) -> str:
    """Return a LiteLLM-qualified model id.

    If ``model`` already contains ``/`` (e.g. ``openrouter/auto``), it is trusted
    as a fully-qualified id. Otherwise returns ``{provider}/{model}``.
    """
    provider = provider.strip()
    model = model.strip()
    if not provider:
        raise ValueError("provider must be a non-empty string")
    if not model:
        raise ValueError("model must be a non-empty string")
    if "/" in model:
        return model
    return f"{provider}/{model}"


def provider_from_model_id(model_id: str) -> str:
    """Best-effort provider prefix from a LiteLLM model id."""
    if "/" in model_id:
        return model_id.split("/", 1)[0]
    return model_id

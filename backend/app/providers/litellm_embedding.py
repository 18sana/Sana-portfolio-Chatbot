"""LiteLLM-backed embedding provider."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import litellm

from app.providers.model_ids import provider_from_model_id
from app.providers.types import EmbeddingResult


class LiteLLMEmbeddingProvider:
    """Thin adapter: maps EmbeddingProvider.embed onto litellm.aembedding."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        provider_name: str | None = None,
        default_dimensions: int | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key or None
        self._api_base = api_base or None
        self._provider_name = provider_name or provider_from_model_id(model)
        self._default_dimensions = default_dimensions

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model

    async def embed(
        self,
        texts: Sequence[str],
        *,
        dimensions: int | None = None,
    ) -> EmbeddingResult:
        if not texts:
            return EmbeddingResult(
                vectors=[],
                model=self._model,
                provider=self._provider_name,
                usage=None,
            )

        kwargs: dict[str, Any] = {
            "model": self._model,
            "input": list(texts),
        }
        dims = dimensions if dimensions is not None else self._default_dimensions
        if dims is not None:
            kwargs["dimensions"] = dims
        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._api_base:
            kwargs["api_base"] = self._api_base

        response = await litellm.aembedding(**kwargs)
        vectors = _extract_vectors(response)
        usage = _extract_embedding_usage(response)
        return EmbeddingResult(
            vectors=vectors,
            model=self._model,
            provider=self._provider_name,
            usage=usage,
            raw=response,
        )


def _extract_vectors(response: Any) -> list[list[float]]:
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if not data:
        raise RuntimeError("Unexpected LiteLLM embedding response shape: empty data")

    vectors: list[list[float]] = []
    for item in data:
        embedding = getattr(item, "embedding", None)
        if embedding is None and isinstance(item, dict):
            embedding = item.get("embedding")
        if embedding is None:
            raise RuntimeError("Unexpected LiteLLM embedding item without embedding")
        vectors.append([float(x) for x in embedding])
    return vectors


def _extract_embedding_usage(response: Any) -> dict[str, int] | None:
    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, dict):
        usage = response.get("usage")
    if usage is None:
        return None
    prompt = getattr(usage, "prompt_tokens", None)
    if prompt is None and isinstance(usage, dict):
        prompt = usage.get("prompt_tokens")
    total = getattr(usage, "total_tokens", None)
    if total is None and isinstance(usage, dict):
        total = usage.get("total_tokens")
    result: dict[str, int] = {}
    if isinstance(prompt, int):
        result["prompt_tokens"] = prompt
    if isinstance(total, int):
        result["total_tokens"] = total
    return result or None

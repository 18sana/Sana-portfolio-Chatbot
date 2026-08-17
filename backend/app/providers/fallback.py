"""Fallback wrappers — the ONLY place primary→secondary retry lives."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence

from app.core.logging import get_logger
from app.providers.base import EmbeddingProvider, LLMProvider
from app.providers.errors import is_retryable_provider_error
from app.providers.types import (
    ChatMessage,
    CompletionChunk,
    CompletionResult,
    EmbeddingResult,
)

logger = get_logger(__name__)


class FallbackLLMProvider:
    """Try primary; on retryable failure before success, use fallback once.

    Stream policy: if the primary fails before the first chunk is yielded,
    switch to the fallback stream. Mid-stream failure does not switch providers
    (that would corrupt SSE clients).
    """

    def __init__(self, primary: LLMProvider, fallback: LLMProvider) -> None:
        self._primary = primary
        self._fallback = fallback

    @property
    def provider_name(self) -> str:
        return self._primary.provider_name

    @property
    def model_name(self) -> str:
        return self._primary.model_name

    @property
    def primary(self) -> LLMProvider:
        return self._primary

    @property
    def fallback(self) -> LLMProvider:
        return self._fallback

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> CompletionResult:
        try:
            return await self._primary.complete(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
        except Exception as exc:
            if not is_retryable_provider_error(exc):
                raise
            logger.warning(
                "llm.fallback_triggered",
                primary_model=self._primary.model_name,
                fallback_model=self._fallback.model_name,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            return await self._fallback.complete(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )

    async def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> AsyncIterator[CompletionChunk]:
        primary_iter = self._primary.stream(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        try:
            first = await primary_iter.__anext__()
        except StopAsyncIteration:
            return
        except Exception as exc:
            if not is_retryable_provider_error(exc):
                raise
            logger.warning(
                "llm.fallback_stream_triggered",
                primary_model=self._primary.model_name,
                fallback_model=self._fallback.model_name,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            async for chunk in self._fallback.stream(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            ):
                yield chunk
            return

        yield first
        async for chunk in primary_iter:
            yield chunk


class FallbackEmbeddingProvider:
    """Try primary embeddings; on retryable failure, use fallback once."""

    def __init__(self, primary: EmbeddingProvider, fallback: EmbeddingProvider) -> None:
        self._primary = primary
        self._fallback = fallback

    @property
    def provider_name(self) -> str:
        return self._primary.provider_name

    @property
    def model_name(self) -> str:
        return self._primary.model_name

    @property
    def primary(self) -> EmbeddingProvider:
        return self._primary

    @property
    def fallback(self) -> EmbeddingProvider:
        return self._fallback

    async def embed(
        self,
        texts: Sequence[str],
        *,
        dimensions: int | None = None,
    ) -> EmbeddingResult:
        try:
            return await self._primary.embed(texts, dimensions=dimensions)
        except Exception as exc:
            if not is_retryable_provider_error(exc):
                raise
            logger.warning(
                "embedding.fallback_triggered",
                primary_model=self._primary.model_name,
                fallback_model=self._fallback.model_name,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            return await self._fallback.embed(texts, dimensions=dimensions)

"""Provider protocols — business logic depends only on these contracts."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Protocol

from app.providers.types import (
    ChatMessage,
    CompletionChunk,
    CompletionResult,
    EmbeddingResult,
)


class LLMProvider(Protocol):
    """Provider-agnostic chat completion interface."""

    @property
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str:
        """Canonical LiteLLM model id, e.g. ``openai/gpt-4o-mini``."""
        ...

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> CompletionResult: ...

    def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> AsyncIterator[CompletionChunk]: ...


class EmbeddingProvider(Protocol):
    """Provider-agnostic embedding interface."""

    @property
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str: ...

    async def embed(
        self,
        texts: Sequence[str],
        *,
        dimensions: int | None = None,
    ) -> EmbeddingResult: ...

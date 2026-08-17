"""Fallback chain behavior — retries live only in Fallback*Provider."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.providers.errors import is_retryable_provider_error
from app.providers.fallback import FallbackEmbeddingProvider, FallbackLLMProvider
from app.providers.types import (
    ChatMessage,
    CompletionChunk,
    CompletionResult,
    EmbeddingResult,
)


class _FakeStatusError(Exception):
    def __init__(self, status_code: int, message: str = "error") -> None:
        super().__init__(message)
        self.status_code = status_code


class _ScriptedLLM:
    def __init__(
        self,
        *,
        model_name: str,
        provider_name: str = "fake",
        complete_side_effect: Any = None,
        complete_result: CompletionResult | None = None,
        stream_side_effect: Any = None,
        stream_chunks: list[CompletionChunk] | None = None,
    ) -> None:
        self._model_name = model_name
        self._provider_name = provider_name
        self.complete_calls = 0
        self.stream_calls = 0
        self._complete_side_effect = complete_side_effect
        self._complete_result = complete_result or CompletionResult(
            content=f"ok:{model_name}",
            model=model_name,
            provider=provider_name,
        )
        self._stream_side_effect = stream_side_effect
        self._stream_chunks = stream_chunks or [
            CompletionChunk(content="hello", finish_reason=None),
            CompletionChunk(content="", finish_reason="stop"),
        ]

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model_name

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> CompletionResult:
        self.complete_calls += 1
        if self._complete_side_effect is not None:
            if callable(self._complete_side_effect):
                raise self._complete_side_effect()
            raise self._complete_side_effect
        return self._complete_result

    async def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> AsyncIterator[CompletionChunk]:
        self.stream_calls += 1
        if self._stream_side_effect is not None:
            raise self._stream_side_effect
        for chunk in self._stream_chunks:
            yield chunk


class _ScriptedEmbedding:
    def __init__(
        self,
        *,
        model_name: str,
        provider_name: str = "fake",
        side_effect: Any = None,
        vectors: list[list[float]] | None = None,
    ) -> None:
        self._model_name = model_name
        self._provider_name = provider_name
        self.embed_calls = 0
        self._side_effect = side_effect
        self._vectors = vectors or [[0.1, 0.2]]

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model_name

    async def embed(
        self,
        texts: Sequence[str],
        *,
        dimensions: int | None = None,
    ) -> EmbeddingResult:
        self.embed_calls += 1
        if self._side_effect is not None:
            raise self._side_effect
        return EmbeddingResult(
            vectors=self._vectors,
            model=self._model_name,
            provider=self._provider_name,
        )


def test_retryable_classification() -> None:
    assert is_retryable_provider_error(_FakeStatusError(429))
    assert is_retryable_provider_error(_FakeStatusError(503))
    assert is_retryable_provider_error(TimeoutError("timed out"))
    assert not is_retryable_provider_error(_FakeStatusError(401))
    assert not is_retryable_provider_error(_FakeStatusError(400))


@pytest.mark.asyncio
async def test_fallback_uses_secondary_on_retryable_primary_failure() -> None:
    primary = _ScriptedLLM(
        model_name="openai/gpt-4o-mini",
        complete_side_effect=_FakeStatusError(503, "unavailable"),
    )
    fallback = _ScriptedLLM(model_name="anthropic/claude-sonnet-4-5")
    provider = FallbackLLMProvider(primary, fallback)

    result = await provider.complete([{"role": "user", "content": "hi"}])

    assert primary.complete_calls == 1
    assert fallback.complete_calls == 1
    assert result.model == "anthropic/claude-sonnet-4-5"
    assert result.content == "ok:anthropic/claude-sonnet-4-5"


@pytest.mark.asyncio
async def test_non_retryable_does_not_fallback() -> None:
    primary = _ScriptedLLM(
        model_name="openai/gpt-4o-mini",
        complete_side_effect=_FakeStatusError(401, "bad key"),
    )
    fallback = _ScriptedLLM(model_name="anthropic/claude-sonnet-4-5")
    provider = FallbackLLMProvider(primary, fallback)

    with pytest.raises(_FakeStatusError):
        await provider.complete([{"role": "user", "content": "hi"}])

    assert primary.complete_calls == 1
    assert fallback.complete_calls == 0


@pytest.mark.asyncio
async def test_stream_fallback_before_first_chunk() -> None:
    primary = _ScriptedLLM(
        model_name="openai/gpt-4o-mini",
        stream_side_effect=_FakeStatusError(529, "overloaded"),
    )
    fallback = _ScriptedLLM(
        model_name="anthropic/claude-sonnet-4-5",
        stream_chunks=[CompletionChunk(content="from-fallback", finish_reason="stop")],
    )
    provider = FallbackLLMProvider(primary, fallback)

    chunks = [chunk async for chunk in provider.stream([{"role": "user", "content": "hi"}])]

    assert primary.stream_calls == 1
    assert fallback.stream_calls == 1
    assert chunks[0].content == "from-fallback"


@pytest.mark.asyncio
async def test_embedding_fallback_on_retryable_failure() -> None:
    primary = _ScriptedEmbedding(
        model_name="openai/text-embedding-3-small",
        side_effect=_FakeStatusError(429, "rate limited"),
    )
    fallback = _ScriptedEmbedding(
        model_name="cohere/embed-english-v3.0",
        vectors=[[0.9, 0.8]],
    )
    provider = FallbackEmbeddingProvider(primary, fallback)

    result = await provider.embed(["hello"])

    assert primary.embed_calls == 1
    assert fallback.embed_calls == 1
    assert result.model == "cohere/embed-english-v3.0"
    assert result.vectors == [[0.9, 0.8]]


@pytest.mark.asyncio
async def test_litellm_complete_passes_model_string(monkeypatch) -> None:
    from app.providers.litellm_llm import LiteLLMLLMProvider

    mock_completion = AsyncMock(
        return_value=type(
            "Resp",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {"message": type("Msg", (), {"content": "pong"})()},
                    )()
                ],
                "usage": type(
                    "Usage",
                    (),
                    {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                )(),
            },
        )()
    )
    monkeypatch.setattr("app.providers.litellm_llm.litellm.acompletion", mock_completion)

    provider = LiteLLMLLMProvider(model="anthropic/claude-sonnet-4-5", provider_name="anthropic")
    result = await provider.complete([{"role": "user", "content": "ping"}])

    assert result.content == "pong"
    assert result.model == "anthropic/claude-sonnet-4-5"
    assert mock_completion.await_args.kwargs["model"] == "anthropic/claude-sonnet-4-5"

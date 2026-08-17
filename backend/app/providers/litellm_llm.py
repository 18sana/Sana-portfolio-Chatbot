"""LiteLLM-backed LLM provider."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Any

import litellm

from app.core.logging import get_logger
from app.providers.model_ids import provider_from_model_id
from app.providers.types import ChatMessage, CompletionChunk, CompletionResult

logger = get_logger(__name__)


class LiteLLMLLMProvider:
    """Thin adapter: maps LLMProvider calls onto litellm.acompletion."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        provider_name: str | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key or None
        self._api_base = api_base or None
        self._provider_name = provider_name or provider_from_model_id(model)

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model

    def _completion_kwargs(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float,
        max_tokens: int | None,
        stop: Sequence[str] | None,
        stream: bool,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": list(messages),
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if stop:
            kwargs["stop"] = list(stop)
        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._api_base:
            kwargs["api_base"] = self._api_base
        return kwargs

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> CompletionResult:
        response = await litellm.acompletion(
            **self._completion_kwargs(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=False,
            )
        )
        content = _extract_message_content(response)
        usage = _extract_usage(response)
        return CompletionResult(
            content=content,
            model=self._model,
            provider=self._provider_name,
            usage=usage,
            raw=response,
        )

    async def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> AsyncIterator[CompletionChunk]:
        response = await litellm.acompletion(
            **self._completion_kwargs(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=True,
            )
        )
        async for chunk in response:
            text, finish_reason = _extract_stream_delta(chunk)
            if text or finish_reason:
                yield CompletionChunk(content=text, finish_reason=finish_reason)


def _extract_message_content(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, KeyError, TypeError) as exc:
        raise RuntimeError("Unexpected LiteLLM completion response shape") from exc
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    # Some providers return list-of-parts; flatten text parts.
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and part.get("type") == "text":
                parts.append(str(part.get("text", "")))
            else:
                text = getattr(part, "text", None)
                if text:
                    parts.append(str(text))
        return "".join(parts)
    return str(content)


def _extract_usage(response: Any) -> dict[str, int] | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    prompt = getattr(usage, "prompt_tokens", None)
    completion = getattr(usage, "completion_tokens", None)
    total = getattr(usage, "total_tokens", None)
    result: dict[str, int] = {}
    if isinstance(prompt, int):
        result["prompt_tokens"] = prompt
    if isinstance(completion, int):
        result["completion_tokens"] = completion
    if isinstance(total, int):
        result["total_tokens"] = total
    return result or None


def _extract_stream_delta(chunk: Any) -> tuple[str, str | None]:
    try:
        choice = chunk.choices[0]
        delta = choice.delta
        content = getattr(delta, "content", None) or ""
        finish_reason = getattr(choice, "finish_reason", None)
        return str(content), finish_reason
    except (AttributeError, IndexError, KeyError, TypeError):
        return "", None

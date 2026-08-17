"""Shared provider types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypedDict


class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


@dataclass(frozen=True, slots=True)
class CompletionChunk:
    content: str
    finish_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CompletionResult:
    content: str
    model: str
    provider: str
    usage: dict[str, int] | None = None
    raw: Any | None = None


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    vectors: list[list[float]]
    model: str
    provider: str
    usage: dict[str, int] | None = None
    raw: Any | None = None

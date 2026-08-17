"""Provider abstractions — public exports for the rest of the app."""

from app.providers.base import EmbeddingProvider, LLMProvider
from app.providers.factory import get_embedding_provider, get_llm_provider
from app.providers.types import (
    ChatMessage,
    CompletionChunk,
    CompletionResult,
    EmbeddingResult,
)

__all__ = [
    "ChatMessage",
    "CompletionChunk",
    "CompletionResult",
    "EmbeddingProvider",
    "EmbeddingResult",
    "LLMProvider",
    "get_embedding_provider",
    "get_llm_provider",
]

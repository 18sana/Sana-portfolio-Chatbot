"""Tracing hooks (Langfuse-ready). Full wiring when keys are present."""

from __future__ import annotations

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)
_tracing_enabled = False


def init_tracing(settings: Settings) -> None:
    global _tracing_enabled
    if settings.langfuse_public_key and settings.langfuse_secret_key:
        _tracing_enabled = True
        logger.info("tracing.enabled", host=settings.langfuse_host)
    else:
        _tracing_enabled = False
        logger.info("tracing.disabled", reason="missing_langfuse_keys")


def is_tracing_enabled() -> bool:
    return _tracing_enabled


def trace_event(name: str, **payload: object) -> None:
    """Lightweight hook — replace with Langfuse client spans in production wiring."""
    if not _tracing_enabled:
        return
    logger.info("trace.event", name=name, **payload)

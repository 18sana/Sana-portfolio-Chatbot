"""Retryability helpers for provider fallback decisions."""

from __future__ import annotations

from typing import Any


def is_retryable_provider_error(exc: BaseException) -> bool:
    """Return True when falling back to a secondary provider may help.

    Retryable: timeouts, connection failures, rate limits (429), 5xx.
    Not retryable: auth/validation client errors (400/401/403) — those usually
    indicate misconfiguration that a different provider won't fix cleanly, or
    would hide bugs.
    """
    status = _extract_status_code(exc)
    if status is not None:
        if status in {401, 403, 400, 404, 422}:
            return False
        if status == 429 or status >= 500:
            return True

    name = type(exc).__name__.lower()
    message = str(exc).lower()
    retryable_tokens = (
        "timeout",
        "timed out",
        "connection",
        "rate limit",
        "ratelimit",
        "overloaded",
        "service unavailable",
        "internal server error",
        "temporarily unavailable",
    )
    if any(token in name for token in ("timeout", "connection", "ratelimit", "apiconnection")):
        return True
    if any(token in message for token in retryable_tokens):
        return True
    return False


def _extract_status_code(exc: BaseException) -> int | None:
    for attr in ("status_code", "status", "http_status"):
        value: Any = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    response = getattr(exc, "response", None)
    if response is not None:
        code = getattr(response, "status_code", None)
        if isinstance(code, int):
            return code
    return None

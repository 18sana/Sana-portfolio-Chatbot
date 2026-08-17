"""Redis-backed rate limiting (Upstash-compatible)."""

from __future__ import annotations

import time
from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis = None
_memory_buckets: dict[str, list[float]] = {}


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_at: float


def get_redis(settings: Settings | None = None):
    global _redis
    if _redis is not None:
        return _redis
    cfg = settings or get_settings()
    try:
        from redis.asyncio import Redis

        _redis = Redis.from_url(cfg.redis_url, decode_responses=True)
        return _redis
    except Exception as exc:
        logger.warning("redis.unavailable", error=str(exc))
        return None


async def check_rate_limit(
    key: str,
    *,
    limit: int,
    window_seconds: int,
    settings: Settings | None = None,
) -> RateLimitResult:
    """Fixed-window counter. Falls back to in-memory if Redis is down."""
    cfg = settings or get_settings()
    client = get_redis(cfg)
    now = time.time()
    window_id = int(now // window_seconds)
    redis_key = f"rl:{key}:{window_id}"
    reset_at = (window_id + 1) * window_seconds

    if client is not None:
        try:
            count = await client.incr(redis_key)
            if count == 1:
                await client.expire(redis_key, window_seconds)
            remaining = max(0, limit - int(count))
            return RateLimitResult(
                allowed=int(count) <= limit,
                remaining=remaining,
                reset_at=reset_at,
            )
        except Exception as exc:
            logger.warning("redis.rate_limit_failed", error=str(exc))

    # In-memory fallback (single-process)
    bucket = _memory_buckets.setdefault(redis_key, [])
    bucket[:] = [ts for ts in bucket if now - ts < window_seconds]
    if len(bucket) >= limit:
        return RateLimitResult(allowed=False, remaining=0, reset_at=reset_at)
    bucket.append(now)
    return RateLimitResult(
        allowed=True,
        remaining=max(0, limit - len(bucket)),
        reset_at=reset_at,
    )

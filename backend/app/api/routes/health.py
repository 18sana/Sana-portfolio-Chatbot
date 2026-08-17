from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    checks = {"api": "ok", "postgres": "unknown", "redis": "unknown"}

    # Best-effort deep checks (never fail liveness hard on dependency blips)
    try:
        from sqlalchemy import text

        from app.db.session import get_engine

        engine = get_engine(settings)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception:
        checks["postgres"] = "unavailable"

    try:
        from app.core.rate_limit import get_redis

        client = get_redis(settings)
        if client is None:
            checks["redis"] = "unavailable"
        else:
            pong = await client.ping()
            checks["redis"] = "ok" if pong else "unavailable"
    except Exception:
        checks["redis"] = "unavailable"

    status = "ok" if checks["api"] == "ok" else "degraded"
    return {
        "status": status,
        "version": settings.app_version or __version__,
        "environment": settings.app_env,
        "checks": checks,
    }

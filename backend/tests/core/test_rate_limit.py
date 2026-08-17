import pytest

from app.core.rate_limit import check_rate_limit


@pytest.mark.asyncio
async def test_in_memory_rate_limit_enforced(monkeypatch) -> None:
    # Force redis path to fail closed into memory buckets
    monkeypatch.setattr("app.core.rate_limit.get_redis", lambda settings=None: None)
    key = "test:rate:unique"
    for _ in range(3):
        result = await check_rate_limit(key, limit=3, window_seconds=60)
        assert result.allowed
    blocked = await check_rate_limit(key, limit=3, window_seconds=60)
    assert blocked.allowed is False
    assert blocked.remaining == 0

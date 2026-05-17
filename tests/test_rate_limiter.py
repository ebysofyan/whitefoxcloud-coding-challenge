import asyncio
import time

from src.rate_limiter import RateLimiter


def test_is_allowed_under_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60.0)
    assert asyncio.run(limiter.is_allowed("user1")) is True
    assert asyncio.run(limiter.is_allowed("user1")) is True
    assert asyncio.run(limiter.is_allowed("user1")) is True


def test_is_allowed_over_limit():
    limiter = RateLimiter(max_requests=2, window_seconds=60.0)
    assert asyncio.run(limiter.is_allowed("user1")) is True
    assert asyncio.run(limiter.is_allowed("user1")) is True
    assert asyncio.run(limiter.is_allowed("user1")) is False


def test_is_allowed_different_keys_independent():
    limiter = RateLimiter(max_requests=1, window_seconds=60.0)
    assert asyncio.run(limiter.is_allowed("user1")) is True
    assert asyncio.run(limiter.is_allowed("user1")) is False
    assert asyncio.run(limiter.is_allowed("user2")) is True


def test_is_allowed_window_expiry():
    limiter = RateLimiter(max_requests=1, window_seconds=0.1)
    assert asyncio.run(limiter.is_allowed("user1")) is True
    assert asyncio.run(limiter.is_allowed("user1")) is False
    time.sleep(0.15)
    assert asyncio.run(limiter.is_allowed("user1")) is True


def test_get_retry_after_no_requests():
    limiter = RateLimiter(max_requests=5, window_seconds=60.0)
    result = asyncio.run(limiter.get_retry_after("user1"))
    assert result == 0.0


def test_get_retry_after_under_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60.0)
    asyncio.run(limiter.is_allowed("user1"))
    result = asyncio.run(limiter.get_retry_after("user1"))
    assert result == 0.0


def test_get_retry_after_over_limit():
    limiter = RateLimiter(max_requests=1, window_seconds=60.0)
    asyncio.run(limiter.is_allowed("user1"))
    asyncio.run(limiter.is_allowed("user1"))
    result = asyncio.run(limiter.get_retry_after("user1"))
    assert result > 55.0


def test_get_retry_after_unknown_key():
    limiter = RateLimiter(max_requests=5, window_seconds=60.0)
    result = asyncio.run(limiter.get_retry_after("nobody"))
    assert result == 0.0


def test_get_retry_after_window_expired():
    limiter = RateLimiter(max_requests=1, window_seconds=0.1)
    asyncio.run(limiter.is_allowed("user1"))
    asyncio.run(limiter.is_allowed("user1"))
    time.sleep(0.15)
    result = asyncio.run(limiter.get_retry_after("user1"))
    assert result == 0.0


def test_max_keys_eviction():
    limiter = RateLimiter(max_requests=5, window_seconds=60.0, max_keys=3)
    asyncio.run(limiter.is_allowed("a"))
    asyncio.run(limiter.is_allowed("b"))
    asyncio.run(limiter.is_allowed("c"))
    assert len(limiter._requests) == 3
    asyncio.run(limiter.is_allowed("d"))
    assert len(limiter._requests) <= 3


def test_prune_expired_clears_empty_keys():
    limiter = RateLimiter(max_requests=5, window_seconds=0.1)
    asyncio.run(limiter.is_allowed("user1"))
    time.sleep(0.15)
    asyncio.run(limiter.is_allowed("user2"))
    assert "user1" not in limiter._requests

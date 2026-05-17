import asyncio

import pytest

from src.config import settings
from src.core.exceptions import RateLimitExceededError
from src.middleware import rate_limit as rl_module
from src.middleware.rate_limit import (
    _extract_client_ip,
    _get_limiter_for_path,
    rate_limit_middleware,
)
from src.middleware.rate_limiter import RateLimiter


@pytest.fixture(autouse=True)
def _reset_limiters():
    fresh_login = RateLimiter(max_requests=5, window_seconds=60.0)
    fresh_general = RateLimiter(max_requests=60, window_seconds=60.0)
    rl_module._LOGIN_LIMIT = fresh_login
    rl_module._GENERAL_LIMIT = fresh_general
    yield


def test_extract_client_ip_x_forwarded_for(monkeypatch):
    from unittest.mock import MagicMock

    monkeypatch.setattr(settings, "trust_proxy_headers", True)
    request = MagicMock()
    request.headers = {"x-forwarded-for": "203.0.113.1, 70.41.3.18"}
    request.client = None
    assert _extract_client_ip(request) == "203.0.113.1"


def test_extract_client_ip_x_real_ip(monkeypatch):
    from unittest.mock import MagicMock

    monkeypatch.setattr(settings, "trust_proxy_headers", True)
    request = MagicMock()
    request.headers = {"x-real-ip": "10.0.0.1"}
    request.client = None
    assert _extract_client_ip(request) == "10.0.0.1"


def test_extract_client_ip_ignores_proxy_when_not_trusted():
    from unittest.mock import MagicMock

    request = MagicMock()
    request.headers = {"x-forwarded-for": "1.2.3.4"}
    client = MagicMock()
    client.host = "127.0.0.1"
    request.client = client
    assert _extract_client_ip(request) == "127.0.0.1"


def test_extract_client_ip_fallback():
    from unittest.mock import MagicMock

    request = MagicMock()
    request.headers = {}
    client = MagicMock()
    client.host = "127.0.0.1"
    request.client = client
    assert _extract_client_ip(request) == "127.0.0.1"


def test_extract_client_ip_no_client():
    from unittest.mock import MagicMock

    request = MagicMock()
    request.headers = {}
    request.client = None
    assert _extract_client_ip(request) == "unknown"


def test_get_limiter_for_path_login():
    limiter = _get_limiter_for_path("/api/auth/login")
    assert limiter is not None
    assert limiter is rl_module._LOGIN_LIMIT


def test_get_limiter_for_path_api():
    limiter = _get_limiter_for_path("/api/books")
    assert limiter is not None
    assert limiter is rl_module._GENERAL_LIMIT


def test_get_limiter_for_path_non_api():
    assert _get_limiter_for_path("/") is None
    assert _get_limiter_for_path("/health") is None
    assert _get_limiter_for_path("/static/index.html") is None


def test_middleware_passes_non_api():
    from unittest.mock import AsyncMock, MagicMock

    request = MagicMock()
    request.url.path = "/health"
    call_next = AsyncMock(return_value=MagicMock(status_code=200))

    result = asyncio.run(rate_limit_middleware(request, call_next))
    assert result.status_code == 200
    call_next.assert_called_once()


def test_middleware_allows_under_limit():
    from unittest.mock import AsyncMock, MagicMock

    request = MagicMock()
    request.url.path = "/api/auth/login"
    request.headers = {}
    client = MagicMock()
    client.host = "127.0.0.1"
    request.client = client
    call_next = AsyncMock(return_value=MagicMock(status_code=200))

    for _ in range(5):
        result = asyncio.run(rate_limit_middleware(request, call_next))
        assert result.status_code == 200


def test_middleware_blocks_over_limit():
    from unittest.mock import AsyncMock, MagicMock

    request = MagicMock()
    request.url.path = "/api/auth/login"
    request.headers = {}
    client = MagicMock()
    client.host = "127.0.0.1"
    request.client = client
    call_next = AsyncMock(return_value=MagicMock(status_code=200))

    for _ in range(5):
        asyncio.run(rate_limit_middleware(request, call_next))

    with pytest.raises(RateLimitExceededError) as exc:
        asyncio.run(rate_limit_middleware(request, call_next))
    assert "Rate limit exceeded" in exc.value.message
    assert exc.value.retry_after > 0


def test_middleware_general_api_limit():
    from unittest.mock import AsyncMock, MagicMock

    request = MagicMock()
    request.url.path = "/api/books"
    request.headers = {}
    client = MagicMock()
    client.host = "127.0.0.1"
    request.client = client
    call_next = AsyncMock(return_value=MagicMock(status_code=200))

    for _ in range(60):
        asyncio.run(rate_limit_middleware(request, call_next))

    with pytest.raises(RateLimitExceededError):
        asyncio.run(rate_limit_middleware(request, call_next))

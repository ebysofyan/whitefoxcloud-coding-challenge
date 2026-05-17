from starlette.requests import Request

from src.config import settings
from src.exceptions import RateLimitExceededError
from src.rate_limiter import RateLimiter

# Rate limit configs
_LOGIN_LIMIT = RateLimiter(max_requests=5, window_seconds=60.0)
_GENERAL_LIMIT = RateLimiter(max_requests=60, window_seconds=60.0)

_LOGIN_PATH = "/api/auth/login"
_API_PREFIX = "/api/"


def _extract_client_ip(request: Request) -> str:
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

    return request.client.host if request.client else "unknown"


def _get_limiter_for_path(path: str) -> RateLimiter | None:
    if path == _LOGIN_PATH:
        return _LOGIN_LIMIT
    if path.startswith(_API_PREFIX):
        return _GENERAL_LIMIT
    return None


async def rate_limit_middleware(request: Request, call_next):
    limiter = _get_limiter_for_path(request.url.path)
    if limiter is None:
        return await call_next(request)

    ip = _extract_client_ip(request)
    allowed = await limiter.is_allowed(ip)

    if not allowed:
        retry_after = await limiter.get_retry_after(ip)
        raise RateLimitExceededError(
            message="Rate limit exceeded. Please try again later.",
            retry_after=retry_after,
        )

    return await call_next(request)

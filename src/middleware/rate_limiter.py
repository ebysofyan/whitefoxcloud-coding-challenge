import asyncio
import time


class RateLimiter:
    """Sliding window rate limiter.
    Tracks request timestamps per key and prunes expired entries.
    Async-safe via a single asyncio.Lock.
    Evicts oldest key when max_keys cap is reached.
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        max_keys: int = 10_000,
    ) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._max_keys = max_keys
        self._requests: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> bool:
        """Return True if the request is allowed, False if rate limited."""
        async with self._lock:
            now = time.time()
            window_start = now - self._window_seconds
            self._prune_expired(now, window_start)
            timestamps = self._requests.get(key, [])
            timestamps = [ts for ts in timestamps if ts > window_start]
            if len(timestamps) >= self._max_requests:
                self._requests[key] = timestamps
                return False
            if key not in self._requests and len(self._requests) >= self._max_keys:
                oldest_key = min(self._requests, key=lambda k: min(self._requests[k]))
                del self._requests[oldest_key]
            timestamps.append(now)
            self._requests[key] = timestamps
            return True

    async def get_retry_after(self, key: str) -> float:
        """Return seconds until the key can make another request."""
        async with self._lock:
            now = time.time()
            window_start = now - self._window_seconds
            timestamps = self._requests.get(key, [])
            timestamps = [ts for ts in timestamps if ts > window_start]
            if len(timestamps) < self._max_requests:
                return 0.0
            oldest = timestamps[0]
            retry_after = oldest + self._window_seconds - now
            return max(0.0, retry_after)

    def _prune_expired(self, now: float, window_start: float) -> None:
        """Remove expired keys to prevent memory growth."""
        empty_keys = []
        for key, timestamps in self._requests.items():
            self._requests[key] = [ts for ts in timestamps if ts > window_start]
            if not self._requests[key]:
                empty_keys.append(key)
        for key in empty_keys:
            del self._requests[key]

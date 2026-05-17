import secrets
import time

from fastapi import Header

from src.exceptions import NotAuthenticatedError

DEFAULT_TOKEN_TTL = 86_400


class TokenStore:
    """In-memory token store with TTL-based expiry."""

    def __init__(self, ttl: int = DEFAULT_TOKEN_TTL):
        self._ttl = ttl
        self._tokens: dict[str, tuple[str, float]] = {}

    def create_token(self, username: str) -> str:
        """Generate a new token for the given username."""
        token = secrets.token_hex(32)
        self._tokens[token] = (username, time.time() + self._ttl)
        return token

    def validate_token(self, token: str) -> str | None:
        """Validate a token and return the username, or None if invalid or expired."""
        entry = self._tokens.get(token)
        if entry is None:
            return None
        username, expires_at = entry
        if time.time() > expires_at:
            del self._tokens[token]
            return None
        return username

    def cleanup_expired(self) -> int:
        """Remove all expired tokens. Returns count of removed entries."""
        now = time.time()
        expired = [t for t, (_, exp) in self._tokens.items() if now > exp]
        for token in expired:
            del self._tokens[token]
        return len(expired)


token_store = TokenStore()

VALID_USERS = {"admin": "admin123"}


def authenticate(username: str, password: str) -> str | None:
    """Authenticate a user and return a token, or None if credentials are invalid."""
    if VALID_USERS.get(username) == password:
        return token_store.create_token(username)
    return None


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> str:
    """FastAPI dependency to validate current user from Authorization header."""
    if authorization is None:
        raise NotAuthenticatedError("Missing authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise NotAuthenticatedError("Invalid authorization format. Use: Bearer <token>")

    token = parts[1]
    username = token_store.validate_token(token)
    if username is None:
        raise NotAuthenticatedError("Invalid or expired token")

    return username

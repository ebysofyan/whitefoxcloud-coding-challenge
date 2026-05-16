import secrets

from fastapi import Header

from src.exceptions import NotAuthenticatedError


class TokenStore:
    """In-memory token store for authentication."""

    def __init__(self):
        self._tokens: dict[str, str] = {}

    def create_token(self, username: str) -> str:
        """Generate a new token for the given username."""
        token = secrets.token_hex(32)
        self._tokens[token] = username
        return token

    def validate_token(self, token: str) -> str | None:
        """Validate a token and return the username, or None if invalid."""
        return self._tokens.get(token)


# Global token store instance
token_store = TokenStore()

# Hardcoded users for coding challenge
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

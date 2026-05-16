import pytest

from src.auth import TokenStore, authenticate, get_current_user
from src.exceptions import NotAuthenticatedError


def test_token_store_create_token():
    store = TokenStore()
    token = store.create_token("admin")
    assert store.validate_token(token) == "admin"


def test_token_store_validate_valid():
    store = TokenStore()
    token = store.create_token("admin")
    assert store.validate_token(token) == "admin"


def test_token_store_validate_invalid():
    store = TokenStore()
    assert store.validate_token("invalid-token") is None


def test_authenticate_success():
    token = authenticate("admin", "admin123")
    assert token is not None
    assert len(token) == 64  # secrets.token_hex(32) = 64 chars


def test_authenticate_invalid_credentials():
    token = authenticate("admin", "wrong")
    assert token is None


def test_authenticate_unknown_user():
    token = authenticate("unknown", "anything")
    assert token is None


def test_get_current_user_missing_header():
    import asyncio

    with pytest.raises(NotAuthenticatedError) as exc:
        asyncio.run(get_current_user(authorization=None))
    assert "Missing" in exc.value.message


def test_get_current_user_malformed_header():
    import asyncio

    with pytest.raises(NotAuthenticatedError) as exc:
        asyncio.run(get_current_user(authorization="Token abc"))
    assert "Invalid authorization format" in exc.value.message


def test_get_current_user_invalid_token():
    import asyncio

    with pytest.raises(NotAuthenticatedError) as exc:
        asyncio.run(get_current_user(authorization="Bearer not-a-real-token"))
    assert "Invalid or expired token" in exc.value.message

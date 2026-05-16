import pytest
from fastapi import HTTPException

from src.auth import TokenStore, authenticate, get_current_user


def test_token_store_create_token():
    store = TokenStore()
    token = store.create_token("admin")
    assert token in store._tokens
    assert store._tokens[token] == "admin"


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

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user(authorization=None))
    assert exc.value.status_code == 401
    assert "Missing" in exc.value.detail


def test_get_current_user_malformed_header():
    import asyncio

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user(authorization="Token abc"))
    assert exc.value.status_code == 401
    assert "Invalid authorization format" in exc.value.detail


def test_get_current_user_invalid_token():
    import asyncio

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user(authorization="Bearer not-a-real-token"))
    assert exc.value.status_code == 401
    assert "Invalid or expired token" in exc.value.detail

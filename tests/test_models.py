import pytest
from pydantic import ValidationError

from src.schemas import BookCreate, LoginRequest, LoginResponse


def test_book_create_valid():
    book = BookCreate(
        id="/books/id1",
        author="/authors/id1",
        name="Test",
        note="Note",
        serial="S001",
    )
    assert book.id == "/books/id1"


def test_book_create_missing_field():
    with pytest.raises(ValidationError):
        BookCreate(id="/books/id1", name="Test")


def test_login_request_valid():
    req = LoginRequest(username="admin", password="admin123")
    assert req.username == "admin"


def test_login_response():
    resp = LoginResponse(token="abc123")
    assert resp.token == "abc123"
    data = resp.model_dump()
    assert data["token"] == "abc123"

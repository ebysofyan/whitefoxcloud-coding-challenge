import boto3
import pytest
from moto import mock_aws

from src.config import settings
from src.core.aws import get_dynamodb_resource
from src.core.exceptions import BookNotFoundError, InvalidCursorError
from src.schemas import BookCreate
from src.services.book_service import (
    BookService,
    _decode_cursor,
    _encode_cursor,
)


@pytest.fixture
def service():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        dynamodb.create_table(
            TableName=settings.books_table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield BookService()


def test_create_book(service):
    book = BookCreate(
        id="/books/id1",
        author="/authors/id1",
        name="Test Book",
        note="A test",
        serial="T001",
    )
    result = service.create_book(book)
    assert result.id == "/books/id1"


def test_create_book_auto_id(service):
    book = BookCreate(
        author="/authors/id1",
        name="Auto ID Book",
        note="A test",
        serial="T001",
    )
    result = service.create_book(book)
    assert result.id is not None
    assert len(result.id) > 0


def test_get_book_exists(service):
    book = BookCreate(
        id="/books/id1",
        author="/authors/id1",
        name="Test Book",
        note="A test",
        serial="T001",
    )
    service.create_book(book)
    result = service.get_book("/books/id1")
    assert result.id == "/books/id1"


def test_get_book_not_found(service):
    with pytest.raises(BookNotFoundError):
        service.get_book("/books/nonexistent")


def test_service_uses_dynamodb_endpoint(monkeypatch):
    """When `dynamodb_endpoint` is set, BookService passes it to boto3."""
    monkeypatch.setattr(settings, "dynamodb_endpoint", "http://localhost:9999")
    captured: dict[str, object] = {}

    def fake_resource(name, **kwargs):
        captured["name"] = name
        captured.update(kwargs)

        class _Resource:
            def Table(self, _):
                return None

        return _Resource()

    monkeypatch.setattr("src.core.aws.boto3.resource", fake_resource)
    BookService()
    assert captured["endpoint_url"] == "http://localhost:9999"
    assert captured["region_name"] == settings.aws_region


def test_get_dynamodb_resource_uses_endpoint_when_set(monkeypatch):
    """Factory passes endpoint_url when dynamodb_endpoint is configured."""
    monkeypatch.setattr(settings, "dynamodb_endpoint", "http://localhost:9999")
    captured: dict[str, object] = {}

    def fake_resource(name, **kwargs):
        captured["name"] = name
        captured.update(kwargs)
        return object()

    monkeypatch.setattr("src.core.aws.boto3.resource", fake_resource)
    get_dynamodb_resource()
    assert captured["endpoint_url"] == "http://localhost:9999"
    assert captured["region_name"] == settings.aws_region


def test_get_dynamodb_resource_omits_endpoint_when_not_set(monkeypatch):
    """Factory omits endpoint_url when dynamodb_endpoint is not configured."""
    monkeypatch.setattr(settings, "dynamodb_endpoint", None)
    captured: dict[str, object] = {}

    def fake_resource(name, **kwargs):
        captured["name"] = name
        captured.update(kwargs)
        return object()

    monkeypatch.setattr("src.core.aws.boto3.resource", fake_resource)
    get_dynamodb_resource()
    assert "endpoint_url" not in captured
    assert captured["region_name"] == settings.aws_region


def test_encode_cursor_none_returns_none():
    assert _encode_cursor(None) is None
    assert _encode_cursor({}) is None


def test_encode_decode_cursor_round_trip():
    key = {"id": "book-1"}
    cursor = _encode_cursor(key)
    assert cursor is not None
    assert _decode_cursor(cursor) == key


def test_decode_cursor_none_returns_none():
    assert _decode_cursor(None) is None
    assert _decode_cursor("") is None


def test_decode_cursor_invalid_base64_raises():
    with pytest.raises(InvalidCursorError):
        _decode_cursor("not-base64!!!")


def test_decode_cursor_non_dict_payload_raises():
    import base64

    payload = base64.urlsafe_b64encode(b'"just-a-string"').decode("ascii")
    with pytest.raises(InvalidCursorError):
        _decode_cursor(payload)


def test_list_books_paginates(service):
    for i in range(3):
        service.create_book(
            BookCreate(
                id=f"b-{i}",
                author="/a/1",
                name=f"n{i}",
                note="x",
                serial=f"S{i}",
            )
        )
    page1 = service.list_books(limit=2)
    assert len(page1.items) == 2
    assert page1.next_cursor is not None
    assert page1.has_prev is False

    page2 = service.list_books(limit=2, cursor=page1.next_cursor)
    assert len(page2.items) == 1
    assert page2.prev_cursor == page1.next_cursor
    assert page2.has_next is False

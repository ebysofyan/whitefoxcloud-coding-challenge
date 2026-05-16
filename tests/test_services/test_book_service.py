import boto3
import pytest
from moto import mock_aws

from src.config import settings
from src.exceptions import BookNotFoundError
from src.services.book_service import BookService


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
    book_data = {
        "id": "/books/id1",
        "author": "/authors/id1",
        "name": "Test Book",
        "note": "A test",
        "serial": "T001",
    }
    result = service.create_book(book_data)
    assert result["id"] == "/books/id1"


def test_get_book_exists(service):
    book_data = {
        "id": "/books/id1",
        "author": "/authors/id1",
        "name": "Test Book",
        "note": "A test",
        "serial": "T001",
    }
    service.create_book(book_data)
    result = service.get_book("/books/id1")
    assert result["id"] == "/books/id1"


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

    monkeypatch.setattr("src.services.book_service.boto3.resource", fake_resource)
    BookService()
    assert captured["endpoint_url"] == "http://localhost:9999"
    assert captured["region_name"] == settings.aws_region

import base64
import json
from typing import Any

import boto3

from src.config import settings
from src.exceptions import BookNotFoundError, InvalidCursorError


def _encode_cursor(key: dict[str, Any] | None) -> str | None:
    """Encode a DynamoDB LastEvaluatedKey as an opaque base64 string."""
    if not key:
        return None
    raw = json.dumps(key, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def _decode_cursor(cursor: str | None) -> dict[str, Any] | None:
    """Decode a client-supplied cursor back into a DynamoDB ExclusiveStartKey."""
    if not cursor:
        return None
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("ascii"))
        decoded = json.loads(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        raise InvalidCursorError() from exc
    if not isinstance(decoded, dict):
        raise InvalidCursorError()
    return decoded


class BookService:
    def __init__(self):
        kwargs: dict[str, Any] = {"region_name": settings.aws_region}
        if settings.dynamodb_endpoint:
            kwargs["endpoint_url"] = settings.dynamodb_endpoint
        self.dynamodb = boto3.resource("dynamodb", **kwargs)
        self.table = self.dynamodb.Table(settings.books_table_name)

    def create_book(self, book_data: dict[str, Any]) -> dict[str, Any]:
        self.table.put_item(Item=book_data)
        return book_data

    def get_book(self, book_id: str) -> dict[str, Any]:
        response = self.table.get_item(Key={"id": book_id})
        item = response.get("Item")

        if item is None:
            raise BookNotFoundError(book_id)

        return item

    def list_books(
        self,
        limit: int = 10,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Paginate books via DynamoDB LastEvaluatedKey.

        Returns a dict matching BookListResponse:
          - items: page of books
          - next_cursor: LEK of this page (None at end of data)
          - prev_cursor: echo of incoming cursor (one-step back)
          - has_next / has_prev: convenience flags
          - total: table item count (eventually consistent; from table metadata)
        """
        scan_kwargs: dict[str, Any] = {"Limit": limit}
        start_key = _decode_cursor(cursor)
        if start_key is not None:
            scan_kwargs["ExclusiveStartKey"] = start_key

        response = self.table.scan(**scan_kwargs)
        next_cursor = _encode_cursor(response.get("LastEvaluatedKey"))

        return {
            "items": response.get("Items", []),
            "next_cursor": next_cursor,
            "prev_cursor": cursor,
            "has_next": next_cursor is not None,
            "has_prev": cursor is not None,
            "total": self.table.item_count,
        }

    def delete_book(self, book_id: str) -> None:
        self.table.delete_item(Key={"id": book_id})

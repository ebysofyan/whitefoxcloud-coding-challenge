from typing import Any

import boto3

from src.config import settings
from src.exceptions import BookNotFoundError


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

    def list_books(self) -> list[dict[str, Any]]:
        response = self.table.scan()
        return response.get("Items", [])

    def delete_book(self, book_id: str) -> None:
        self.table.delete_item(Key={"id": book_id})

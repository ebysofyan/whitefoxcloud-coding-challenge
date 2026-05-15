from typing import Any

import boto3

from src.config import settings
from src.exceptions import BookNotFoundError


class BookService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
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

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, Path

from src.auth import get_current_user
from src.models import BookCreate, BookResponse

router = APIRouter(prefix="/api/books", tags=["books"])


def get_service():
    from src.services.book_service import BookService

    return BookService()


@router.post("", status_code=201, response_model=BookResponse)
def create_book(
    book: Annotated[BookCreate, Body()],
    current_user: Annotated[str, Depends(get_current_user)],
) -> BookResponse:
    book_data = book.model_dump()
    if book_data.get("id") is None:
        book_data["id"] = str(uuid4())
    result = get_service().create_book(book_data)
    return BookResponse(**result)


@router.get("", response_model=list[BookResponse])
def list_books(
    current_user: Annotated[str, Depends(get_current_user)],
) -> list[BookResponse]:
    results = get_service().list_books()
    return [BookResponse(**item) for item in results]


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: Annotated[str, Path()],
    current_user: Annotated[str, Depends(get_current_user)],
) -> BookResponse:
    result = get_service().get_book(book_id)
    return BookResponse(**result)


@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: Annotated[str, Path()],
    current_user: Annotated[str, Depends(get_current_user)],
) -> None:
    get_service().delete_book(book_id)

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, Path, Query

from src.auth import get_current_user
from src.models import BookCreate, BookListResponse, BookResponse

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


@router.get("", response_model=BookListResponse)
def list_books(
    current_user: Annotated[str, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    cursor: Annotated[str | None, Query()] = None,
) -> BookListResponse:
    result = get_service().list_books(limit=limit, cursor=cursor)
    return BookListResponse(
        items=[BookResponse(**item) for item in result["items"]],
        next_cursor=result["next_cursor"],
        prev_cursor=result["prev_cursor"],
        has_next=result["has_next"],
        has_prev=result["has_prev"],
        total=result["total"],
    )


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

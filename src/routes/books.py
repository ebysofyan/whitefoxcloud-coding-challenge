from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from src.auth.token_store import get_current_user
from src.schemas import BookCreate, BookListResponse, BookResponse
from src.services.book_service import BookService

router = APIRouter(prefix="/api/books", tags=["books"])


@lru_cache
def get_book_service() -> BookService:
    """Singleton BookService — avoids re-creating boto3 per request."""
    return BookService()


@router.post(
    "",
    status_code=201,
    response_model=BookResponse,
    summary="Create a book",
)
def create_book(
    book: Annotated[BookCreate, Body()],
    current_user: Annotated[str, Depends(get_current_user)],
    service: Annotated[BookService, Depends(get_book_service)],
) -> BookResponse:
    return service.create_book(book)


@router.get(
    "",
    response_model=BookListResponse,
    summary="List books with cursor pagination",
)
def list_books(
    current_user: Annotated[str, Depends(get_current_user)],
    service: Annotated[BookService, Depends(get_book_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    cursor: Annotated[str | None, Query()] = None,
) -> BookListResponse:
    return service.list_books(limit=limit, cursor=cursor)


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get a book by ID",
)
def get_book(
    book_id: Annotated[str, Path()],
    current_user: Annotated[str, Depends(get_current_user)],
    service: Annotated[BookService, Depends(get_book_service)],
) -> BookResponse:
    return service.get_book(book_id)


@router.delete(
    "/{book_id}",
    status_code=204,
    summary="Delete a book by ID",
)
def delete_book(
    book_id: Annotated[str, Path()],
    current_user: Annotated[str, Depends(get_current_user)],
    service: Annotated[BookService, Depends(get_book_service)],
) -> None:
    service.delete_book(book_id)

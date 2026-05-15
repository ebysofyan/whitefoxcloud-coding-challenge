from src.exceptions import BookNotFoundError, NotAuthenticatedError


def test_book_not_found_error():
    error = BookNotFoundError("/books/missing")
    assert error.book_id == "/books/missing"
    assert "Book not found: /books/missing" in str(error)


def test_not_authenticated_error():
    error = NotAuthenticatedError("Invalid token")
    assert error.message == "Invalid token"
    assert "Invalid token" in str(error)

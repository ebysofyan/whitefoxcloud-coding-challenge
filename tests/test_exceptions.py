from src.exceptions import BookNotFoundError, InvalidCursorError, NotAuthenticatedError


def test_book_not_found_error():
    error = BookNotFoundError("/books/missing")
    assert error.book_id == "/books/missing"
    assert error.message == "Book not found: /books/missing"
    assert "Book not found: /books/missing" in str(error)


def test_not_authenticated_error():
    error = NotAuthenticatedError("Invalid token")
    assert error.message == "Invalid token"
    assert "Invalid token" in str(error)


def test_not_authenticated_error_default_message():
    error = NotAuthenticatedError()
    assert error.message == "Not authenticated"


def test_invalid_cursor_error():
    error = InvalidCursorError()
    assert error.message == "Invalid pagination cursor"


def test_invalid_cursor_error_custom_message():
    error = InvalidCursorError("Bad cursor value")
    assert error.message == "Bad cursor value"

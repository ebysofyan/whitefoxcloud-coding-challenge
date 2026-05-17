class BookAPIError(Exception):
    """Base exception for all Books API errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BookNotFoundError(BookAPIError):
    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Book not found: {book_id}")


class NotAuthenticatedError(BookAPIError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message)


class InvalidCursorError(BookAPIError):
    """Raised when a pagination cursor cannot be decoded."""

    def __init__(self, message: str = "Invalid pagination cursor"):
        super().__init__(message)


class RateLimitExceededError(BookAPIError):
    """Raised when a client exceeds the allowed request rate."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: float = 0.0,
    ):
        self.retry_after = retry_after
        super().__init__(message)

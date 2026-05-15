class BookNotFoundError(Exception):
    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Book not found: {book_id}")


class NotAuthenticatedError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

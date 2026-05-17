from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    id: str | None = None
    author: str = Field(min_length=1)
    name: str = Field(min_length=1)
    note: str = Field(min_length=1)
    serial: str = Field(min_length=1)


class BookResponse(BaseModel):
    id: str
    author: str
    name: str
    note: str
    serial: str


class BookListResponse(BaseModel):
    """Paginated list response.
    Cursors are opaque, base64-encoded JSON of DynamoDB's LastEvaluatedKey.
    `prev_cursor` is an echo of the request's incoming cursor (one-step back).
    """

    items: list[BookResponse]
    next_cursor: str | None = None
    prev_cursor: str | None = None
    has_next: bool = False
    has_prev: bool = False
    total: int = 0

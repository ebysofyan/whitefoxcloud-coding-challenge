import logging
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from mangum import Mangum
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.exceptions import (
    BookNotFoundError,
    InvalidCursorError,
    NotAuthenticatedError,
    RateLimitExceededError,
)
from src.middleware.rate_limit import rate_limit_middleware
from src.routes.auth import router as auth_router
from src.routes.books import router as books_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Books API", version="0.1.0")

# CORS middleware (Spec §10)
# NOTE: allow_origins=["*"] is intentional for this coding challenge.
# In production, restrict to specific origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

# Include routers
app.include_router(auth_router)
app.include_router(books_router)

STATIC_DIR = Path(__file__).parent.parent / "static"


@app.get("/health", summary="Health check")
async def health() -> dict[str, str]:
    """Health check endpoint for readiness probes."""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the single-page HTML client."""
    content = (STATIC_DIR / "index.html").read_text()
    return HTMLResponse(content=content)


@app.get("/static/index.html", response_class=HTMLResponse)
async def serve_static_index() -> HTMLResponse:
    """Serve the single-page HTML client at /static/index.html."""
    content = (STATIC_DIR / "index.html").read_text()
    return HTMLResponse(content=content)


@app.exception_handler(BookNotFoundError)
async def book_not_found_handler(
    request: Request,
    exc: BookNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidCursorError)
async def invalid_cursor_handler(
    request: Request,
    exc: InvalidCursorError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(NotAuthenticatedError)
async def not_authenticated_handler(
    request: Request,
    exc: NotAuthenticatedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
    )


@app.exception_handler(RateLimitExceededError)
async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceededError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": exc.message},
        headers={"Retry-After": str(int(exc.retry_after) + 1)},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all for unexpected server errors."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


handler = Mangum(app)

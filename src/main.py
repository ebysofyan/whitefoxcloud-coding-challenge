import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from mangum import Mangum
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

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

# Disable Swagger/OpenAPI in production environments
_env = os.getenv("ENVIRONMENT", "dev")
_is_prod = _env in ("prod", "staging")

app = FastAPI(
    title="Books API",
    version="0.1.0",
    # Custom /docs handler below handles stage-prefix for API Gateway.
    # Built-in docs_url is always disabled to avoid route conflict.
    docs_url=None,
    redoc_url=None if _is_prod else "/redoc",
    openapi_url=None if _is_prod else "/openapi.json",
)


class RootPathMiddleware:
    """Set root_path from API Gateway stage so Swagger resolves URLs correctly."""

    def __init__(self, inner: ASGIApp) -> None:
        self.inner = inner

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") == "http" and not scope.get("root_path"):
            path = scope.get("path", "")
            headers = dict(scope.get("headers", []))
            host = headers.get(b"host", b"").decode()
            if "execute-api" in host:
                parts = path.strip("/").split("/")
                if parts and parts[0] in ("dev", "prod", "staging"):
                    scope["root_path"] = f"/{parts[0]}"
        await self.inner(scope, receive, send)


app.add_middleware(RootPathMiddleware)

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


@app.get("/docs", response_class=HTMLResponse)
async def docs(request: Request) -> HTMLResponse:
    headers = dict(request.scope.get("headers", []))
    host = headers.get(b"host", b"").decode()
    if "execute-api" in host:
        stage = os.getenv("ENVIRONMENT", "dev")
        openapi_url = f"/{stage}/openapi.json"
    else:
        openapi_url = "/openapi.json"
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="Books API - Swagger UI",
    )


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

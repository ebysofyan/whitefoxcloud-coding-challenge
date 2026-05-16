from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from mangum import Mangum

from src.exceptions import (
    BookNotFoundError,
    NotAuthenticatedError,
)
from src.routes.auth import router as auth_router
from src.routes.books import router as books_router

app = FastAPI(title="Books API", version="0.1.0")

# CORS middleware (Spec §10)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(books_router)

STATIC_DIR = Path(__file__).parent.parent / "static"


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
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(NotAuthenticatedError)
async def not_authenticated_handler(
    request: Request,
    exc: NotAuthenticatedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all for unexpected server errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


handler = Mangum(app)

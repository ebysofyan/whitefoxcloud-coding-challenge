"""Tests for src.main app-level behavior (CORS, static serving, error handlers)."""

from fastapi.testclient import TestClient

from src.exceptions import NotAuthenticatedError
from src.main import app


def test_cors_headers(client: TestClient):
    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" in {k.lower() for k in response.headers}


def test_index_html_served(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Books API" in response.text


def test_static_index_html_served(client: TestClient):
    response = client.get("/static/index.html")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_not_authenticated_error_handler():
    """Wire a throwaway route that raises NotAuthenticatedError to cover its handler."""

    @app.get("/__test/not-authenticated")
    async def _trigger():
        raise NotAuthenticatedError("nope")

    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            response = test_client.get("/__test/not-authenticated")
        assert response.status_code == 401
        assert response.json() == {"detail": "nope"}
    finally:
        app.router.routes = [
            r
            for r in app.router.routes
            if getattr(r, "path", "") != "/__test/not-authenticated"
        ]


def test_general_exception_handler():
    """Unhandled exceptions map to 500 via the catch-all handler."""

    @app.get("/__test/boom")
    async def _trigger():
        raise RuntimeError("kaboom")

    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            response = test_client.get("/__test/boom")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}
    finally:
        app.router.routes = [
            r for r in app.router.routes if getattr(r, "path", "") != "/__test/boom"
        ]

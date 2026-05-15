import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_login_success(client):
    """POST /api/auth/login returns 200 with token on valid credentials."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert len(data["token"]) == 64


def test_login_invalid_credentials(client):
    """POST /api/auth/login returns 401 on invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "wrong",
        },
    )
    assert response.status_code == 401


def test_login_missing_fields(client):
    """POST /api/auth/login returns 422 on missing fields."""
    response = client.post("/api/auth/login", json={"username": "admin"})
    assert response.status_code == 422

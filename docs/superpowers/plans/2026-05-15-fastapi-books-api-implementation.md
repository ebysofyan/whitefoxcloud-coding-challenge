# FastAPI Books API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a RESTful Books API on FastAPI with DynamoDB backend, token-based auth, single-page HTML client, deployed via Serverless Framework on AWS Lambda, with full test coverage and pre-commit quality gates.

**Architecture:** Monolithic Lambda running FastAPI app. API Gateway proxies `/api/*` to Lambda. FastAPI handles routing internally. Auth middleware protects `/api/books/*` endpoints. Service layer abstracts DynamoDB operations. Static HTML client served via route handler.

**Tech Stack:** Python 3.14, FastAPI, Pydantic 2, boto3, pydantic-settings, mangum, moto, pytest, pytest-cov, uv, ruff, pre-commit, Serverless Framework, Make

**Development Methodology:** Test-Driven Development (TDD). Every task follows Red-Green-Refactor:
1. **Red** — Write failing test first
2. **Green** — Write minimal implementation to pass
3. **Refactor** — Clean up while tests stay green

**Coverage Target:** ≥ 90% line coverage on all `src/` files.

---

## File Structure Map

| File | Responsibility | Created/Modified |
|------|----------------|------------------|
| `pyproject.toml` | uv project config, dependencies, pytest, ruff, FastAPI entrypoint | Create |
| `.pre-commit-config.yaml` | pre-commit hooks (ruff, ruff-format) | Create |
| `.gitignore` | Standard Python/serverless ignores | Create |
| `Makefile` | Developer task runner | Create |
| `src/__init__.py` | Package marker | Create |
| `src/config.py` | Environment-based settings | Create |
| `src/models.py` | Pydantic 2 schemas (LoginRequest, LoginResponse, BookCreate, BookResponse) | Create |
| `src/exceptions.py` | Custom exceptions (BookNotFoundError, NotAuthenticatedError) | Create |
| `src/auth.py` | Token store, login logic, auth dependency | Create |
| `src/services/__init__.py` | Package marker | Create |
| `src/services/book_service.py` | DynamoDB CRUD operations | Create |
| `src/routes/__init__.py` | Package marker | Create |
| `src/routes/auth.py` | Auth endpoints (login) | Create |
| `src/routes/books.py` | Book endpoints (protected) | Create |
| `src/main.py` | FastAPI app, middleware, exception handlers, static file route, Lambda handler | Create |
| `static/index.html` | Single-page HTML client (login + book CRUD) | Create |
| `tests/__init__.py` | Package marker | Create |
| `tests/conftest.py` | Shared pytest fixtures | Create |
| `tests/test_config.py` | Config unit tests | Create |
| `tests/test_models.py` | Model unit tests | Create |
| `tests/test_exceptions.py` | Exception unit tests | Create |
| `tests/test_auth.py` | Auth logic unit tests | Create |
| `tests/test_services/__init__.py` | Package marker | Create |
| `tests/test_services/test_book_service.py` | Service unit tests | Create |
| `tests/test_routes/__init__.py` | Package marker | Create |
| `tests/test_routes/test_auth.py` | Auth route unit tests | Create |
| `tests/test_routes/test_books.py` | Book route unit tests | Create |
| `tests/integration/__init__.py` | Package marker | Create |
| `tests/integration/test_books.py` | Integration tests (auth + book lifecycle) | Create |
| `serverless.yml` | Serverless Framework config | Create |
| `README.md` | Setup, run, test, deploy documentation | Create |

---

## Task 1: Project Setup with uv

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "books-api"
version = "0.1.0"
description = "FastAPI Books API on AWS Lambda"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "boto3>=1.35.0",
    "pydantic-settings>=2.6.0",
    "mangum>=0.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.27.0",
    "moto>=5.0.0",
    "ruff>=0.8.0",
    "pre-commit>=4.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.fastapi]
entrypoint = "src.main:app"

[tool.ruff]
target-version = "py314"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

- [ ] **Step 2: Create .gitignore**

```gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.env
.venv/
.serverless/
.aws-sam/
*.egg-info/
dist/
build/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
```

- [ ] **Step 3: Install dependencies**

```bash
uv sync --all-extras
```

Expected: `.venv/` created, all packages installed.

- [ ] **Step 4: Verify**

```bash
uv run pytest --version
```

Expected: `pytest 8.x.x`

---

## Task 2: pre-commit Configuration

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Create .pre-commit-config.yaml**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 2: Install hooks**

```bash
uv run pre-commit install
```

Expected: `pre-commit installed at .git/hooks/pre-commit`

---

## Task 3: Makefile

**Files:**
- Create: `Makefile`

- [ ] **Step 1: Create Makefile**

```makefile
.PHONY: help setup dev test test-unit test-integration coverage lint format fix precommit deploy deploy-prod remove clean

help:
	@echo "Available targets:"
	@echo "  setup        Install dependencies and pre-commit hooks"
	@echo "  dev           Start FastAPI development server"
	@echo "  test          Run all tests (unit + integration)"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  coverage      Run tests with 90% coverage gate"
	@echo "  lint          Run ruff linter"
	@echo "  format        Run ruff formatter"
	@echo "  fix           Auto-fix lint issues and format"
	@echo "  precommit     Run pre-commit hooks on all files"
	@echo "  deploy        Deploy to AWS (dev stage)"
	@echo "  deploy-prod   Deploy to AWS (production stage)"
	@echo "  remove        Remove deployed AWS resources"
	@echo "  clean         Remove local artifacts and caches"

setup:
	uv sync --all-extras
	uv run pre-commit install

dev:
	uv run fastapi dev src.main:app

test:
	uv run pytest -v

test-unit:
	uv run pytest tests/ -v --ignore=tests/integration

test-integration:
	uv run pytest tests/integration/ -v

coverage:
	uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90 -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

fix:
	uv run ruff check . --fix
	uv run ruff format .

precommit:
	uv run pre-commit run --all-files

deploy:
	serverless deploy

deploy-prod:
	serverless deploy --stage production

remove:
	serverless remove

clean:
	rm -rf .venv .ruff_cache .pytest_cache __pycache__ .serverless .coverage htmlcov
```

**Important:** Must use **real tabs** for recipe indentation.

- [ ] **Step 2: Verify**

```bash
make help
make setup
```

---

## Task 4: Configuration and Models (TDD)

**Files:**
- Create: `src/__init__.py`
- Create: `tests/test_config.py`
- Create: `src/config.py`
- Create: `tests/test_models.py`
- Create: `src/models.py`
- Create: `tests/test_exceptions.py`
- Create: `src/exceptions.py`

- [ ] **Step 1: Create src/__init__.py**

```python
# Books API package
```

- [ ] **Step 2: RED — Test for Settings**

Create `tests/test_config.py`:

```python
from src.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.books_table_name == "dev-books"
    assert settings.aws_region == "us-east-1"
    assert settings.environment == "dev"
```

- [ ] **Step 3: Run — expect FAIL**

```bash
uv run pytest tests/test_config.py -v
```

- [ ] **Step 4: GREEN — Create src/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    books_table_name: str = "dev-books"
    aws_region: str = "us-east-1"
    environment: str = "dev"

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}


settings = Settings()
```

- [ ] **Step 5: Run — expect PASS**

```bash
uv run pytest tests/test_config.py -v
```

- [ ] **Step 6: RED — Tests for models**

Create `tests/test_models.py`:

```python
import pytest
from pydantic import ValidationError

from src.models import BookCreate, BookResponse, LoginRequest, LoginResponse


def test_book_create_valid():
    book = BookCreate(
        id="/books/id1", author="/authors/id1",
        name="Test", note="Note", serial="S001",
    )
    assert book.id == "/books/id1"


def test_book_create_missing_field():
    with pytest.raises(ValidationError):
        BookCreate(id="/books/id1", name="Test")


def test_login_request_valid():
    req = LoginRequest(username="admin", password="admin123")
    assert req.username == "admin"


def test_login_response():
    resp = LoginResponse(token="abc123")
    assert resp.token == "abc123"
    data = resp.model_dump()
    assert data["token"] == "abc123"
```

- [ ] **Step 7: Run — expect FAIL**

```bash
uv run pytest tests/test_models.py -v
```

- [ ] **Step 8: GREEN — Create src/models.py**

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class BookCreate(BaseModel):
    """Input model for creating a book. All fields required."""

    id: str
    author: str
    name: str
    note: str
    serial: str


class BookResponse(BaseModel):
    """Output model for book responses."""

    id: str
    author: str
    name: str
    note: str
    serial: str
```

- [ ] **Step 9: Run — expect PASS**

```bash
uv run pytest tests/test_models.py -v
```

- [ ] **Step 10: RED — Test for exceptions**

Create `tests/test_exceptions.py`:

```python
import pytest
from src.exceptions import BookNotFoundError, NotAuthenticatedError


def test_book_not_found_error():
    error = BookNotFoundError("/books/missing")
    assert error.book_id == "/books/missing"
    assert "Book not found: /books/missing" in str(error)


def test_not_authenticated_error():
    error = NotAuthenticatedError("Invalid token")
    assert error.message == "Invalid token"
    assert "Invalid token" in str(error)
```

- [ ] **Step 11: Run — expect FAIL**

```bash
uv run pytest tests/test_exceptions.py -v
```

- [ ] **Step 12: GREEN — Create src/exceptions.py**

```python
class BookNotFoundError(Exception):
    """Raised when a book ID does not exist in DynamoDB."""

    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Book not found: {book_id}")


class NotAuthenticatedError(Exception):
    """Raised when authentication is missing or invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
```

- [ ] **Step 13: Run — expect PASS**

```bash
uv run pytest tests/test_exceptions.py -v
```

- [ ] **Step 14: Run ruff**

```bash
uv run ruff check src/ tests/test_config.py tests/test_models.py tests/test_exceptions.py
uv run ruff format src/ tests/test_config.py tests/test_models.py tests/test_exceptions.py
```

---

## Task 5: Auth Module (TDD)

**Files:**
- Create: `src/auth.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: RED — Tests for auth logic**

Create `tests/test_auth.py`:

```python
import pytest
from src.auth import TokenStore, authenticate, get_current_user


def test_token_store_create_token():
    store = TokenStore()
    token = store.create_token("admin")
    assert token in store._tokens
    assert store._tokens[token] == "admin"


def test_token_store_validate_valid():
    store = TokenStore()
    token = store.create_token("admin")
    assert store.validate_token(token) == "admin"


def test_token_store_validate_invalid():
    store = TokenStore()
    assert store.validate_token("invalid-token") is None


def test_authenticate_success():
    token = authenticate("admin", "admin123")
    assert token is not None
    assert len(token) == 64  # secrets.token_hex(32) = 64 chars


def test_authenticate_invalid_credentials():
    token = authenticate("admin", "wrong")
    assert token is None


def test_authenticate_unknown_user():
    token = authenticate("unknown", "anything")
    assert token is None
```

- [ ] **Step 2: Run — expect FAIL**

```bash
uv run pytest tests/test_auth.py -v
```

- [ ] **Step 3: GREEN — Create src/auth.py**

```python
import secrets

from fastapi import Header, HTTPException, status


class TokenStore:
    """In-memory token store for authentication."""

    def __init__(self):
        self._tokens: dict[str, str] = {}

    def create_token(self, username: str) -> str:
        """Generate a new token for the given username."""
        token = secrets.token_hex(32)
        self._tokens[token] = username
        return token

    def validate_token(self, token: str) -> str | None:
        """Validate a token and return the username, or None if invalid."""
        return self._tokens.get(token)


# Global token store instance
token_store = TokenStore()

# Hardcoded users for coding challenge
VALID_USERS = {"admin": "admin123"}


def authenticate(username: str, password: str) -> str | None:
    """Authenticate a user and return a token, or None if credentials are invalid."""
    if VALID_USERS.get(username) == password:
        return token_store.create_token(username)
    return None


async def get_current_user(authorization: str | None = Header(default=None)) -> str:
    """FastAPI dependency to extract and validate the current user from the Authorization header."""
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use: Bearer <token>",
        )

    token = parts[1]
    username = token_store.validate_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return username
```

- [ ] **Step 4: Run — expect PASS**

```bash
uv run pytest tests/test_auth.py -v
```

- [ ] **Step 5: Run ruff**

```bash
uv run ruff check src/auth.py tests/test_auth.py
uv run ruff format src/auth.py tests/test_auth.py
```

---

## Task 6: DynamoDB Service Layer (TDD)

**Files:**
- Create: `src/services/__init__.py`
- Create: `tests/test_services/__init__.py`
- Create: `tests/test_services/test_book_service.py`
- Create: `src/services/book_service.py`

- [ ] **Step 1: Create package init files**

```python
# src/services/__init__.py
# Services package

# tests/test_services/__init__.py
# Test services package
```

- [ ] **Step 2: RED — Tests for BookService**

Create `tests/test_services/test_book_service.py`:

```python
import pytest
from moto import mock_aws
import boto3

from src.services.book_service import BookService
from src.exceptions import BookNotFoundError
from src.config import settings


@pytest.fixture
def service():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        dynamodb.create_table(
            TableName=settings.books_table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield BookService()


def test_create_book(service):
    book_data = {
        "id": "/books/id1", "author": "/authors/id1",
        "name": "Test Book", "note": "A test", "serial": "T001",
    }
    result = service.create_book(book_data)
    assert result["id"] == "/books/id1"


def test_get_book_exists(service):
    book_data = {
        "id": "/books/id1", "author": "/authors/id1",
        "name": "Test Book", "note": "A test", "serial": "T001",
    }
    service.create_book(book_data)
    result = service.get_book("/books/id1")
    assert result["id"] == "/books/id1"


def test_get_book_not_found(service):
    with pytest.raises(BookNotFoundError):
        service.get_book("/books/nonexistent")
```

- [ ] **Step 3: Run — expect FAIL**

```bash
uv run pytest tests/test_services/test_book_service.py -v
```

- [ ] **Step 4: GREEN — Create src/services/book_service.py**

```python
from typing import Any

import boto3

from src.config import settings
from src.exceptions import BookNotFoundError


class BookService:
    """DynamoDB operations for the Books table."""

    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        self.table = self.dynamodb.Table(settings.books_table_name)

    def create_book(self, book_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new book in DynamoDB."""
        self.table.put_item(Item=book_data)
        return book_data

    def get_book(self, book_id: str) -> dict[str, Any]:
        """Retrieve a book by ID from DynamoDB."""
        response = self.table.get_item(Key={"id": book_id})
        item = response.get("Item")

        if item is None:
            raise BookNotFoundError(book_id)

        return item
```

- [ ] **Step 5: Run — expect PASS**

```bash
uv run pytest tests/test_services/test_book_service.py -v
```

- [ ] **Step 6: Run ruff**

```bash
uv run ruff check src/services/book_service.py tests/test_services/test_book_service.py
uv run ruff format src/services/book_service.py tests/test_services/test_book_service.py
```

---

## Task 7: Auth Routes (TDD)

**Files:**
- Create: `src/routes/__init__.py`
- Create: `src/routes/auth.py`
- Create: `tests/test_routes/__init__.py`
- Create: `tests/test_routes/test_auth.py`

- [ ] **Step 1: Create src/routes/__init__.py**

```python
# Routes package
```

- [ ] **Step 2: RED — Tests for auth routes**

Create `tests/test_routes/test_auth.py`:

```python
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_login_success(client):
    """POST /api/auth/login returns 200 with token on valid credentials."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert len(data["token"]) == 64


def test_login_invalid_credentials(client):
    """POST /api/auth/login returns 401 on invalid credentials."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrong",
    })
    assert response.status_code == 401


def test_login_missing_fields(client):
    """POST /api/auth/login returns 400 on missing fields."""
    response = client.post("/api/auth/login", json={"username": "admin"})
    assert response.status_code == 400
```

- [ ] **Step 3: Run — expect FAIL**

```bash
uv run pytest tests/test_routes/test_auth.py -v
```

- [ ] **Step 4: GREEN — Create src/routes/auth.py**

```python
from typing import Annotated

from fastapi import APIRouter, Body

from src.models import LoginRequest, LoginResponse
from src.auth import authenticate

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: Annotated[LoginRequest, Body()]) -> LoginResponse:
    """Authenticate a user and return a token."""
    token = authenticate(credentials.username, credentials.password)
    if token is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return LoginResponse(token=token)
```

- [ ] **Step 5: Run — expect PASS**

```bash
uv run pytest tests/test_routes/test_auth.py -v
```

- [ ] **Step 6: Run ruff**

```bash
uv run ruff check src/routes/auth.py tests/test_routes/test_auth.py
uv run ruff format src/routes/auth.py tests/test_routes/test_auth.py
```

---

## Task 8: Book Routes with Auth (TDD)

**Files:**
- Create: `src/routes/books.py`
- Create: `tests/test_routes/test_books.py`

- [ ] **Step 1: RED — Tests for book routes (with auth)**

Create `tests/test_routes/test_books.py`:

```python
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3

from src.main import app
from src.config import settings
from src.auth import token_store


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        dynamodb.create_table(
            TableName=settings.books_table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


@pytest.fixture
def auth_token():
    """Create a valid auth token."""
    return token_store.create_token("admin")


def test_create_book_unauthorized(client, dynamodb_table):
    """POST /api/books returns 401 without auth token."""
    response = client.post("/api/books", json={
        "id": "/books/id1", "author": "/authors/id1",
        "name": "Test", "note": "Note", "serial": "S001",
    })
    assert response.status_code == 401


def test_create_book_success(client, dynamodb_table, auth_token):
    """POST /api/books returns 201 with valid auth and payload."""
    response = client.post("/api/books", json={
        "id": "/books/id1", "author": "/authors/id1",
        "name": "Fancy Tech", "note": "Awesome book", "serial": "C040102",
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "/books/id1"


def test_create_book_missing_fields(client, dynamodb_table, auth_token):
    """POST /api/books returns 400 on missing fields."""
    response = client.post("/api/books", json={"id": "/books/id2"},
                          headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 400


def test_get_book_unauthorized(client, dynamodb_table):
    """GET /api/books/{id} returns 401 without auth token."""
    response = client.get("/api/books/%2Fbooks%2Fid1")
    assert response.status_code == 401


def test_get_book_success(client, dynamodb_table, auth_token):
    """GET /api/books/{id} returns 200 with valid auth."""
    client.post("/api/books", json={
        "id": "/books/id1", "author": "/authors/id1",
        "name": "Fancy Tech", "note": "Awesome book", "serial": "C040102",
    }, headers={"Authorization": f"Bearer {auth_token}"})
    response = client.get("/api/books/%2Fbooks%2Fid1",
                         headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "/books/id1"


def test_get_book_not_found(client, dynamodb_table, auth_token):
    """GET /api/books/{id} returns 404 when book doesn't exist."""
    response = client.get("/api/books/nonexistent",
                         headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 404
```

- [ ] **Step 2: Run — expect FAIL**

```bash
uv run pytest tests/test_routes/test_books.py -v
```

- [ ] **Step 3: GREEN — Create src/routes/books.py**

```python
from typing import Annotated

from fastapi import APIRouter, Body, Path

from src.models import BookCreate, BookResponse
from src.services.book_service import BookService
from src.auth import get_current_user

router = APIRouter(prefix="/api/books", tags=["books"])
service = BookService()


@router.post("", status_code=201, response_model=BookResponse)
def create_book(
    book: Annotated[BookCreate, Body()],
    current_user: Annotated[str, get_current_user],
) -> BookResponse:
    """Create a new book. Requires authentication."""
    book_data = book.model_dump()
    result = service.create_book(book_data)
    return BookResponse(**result)


@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: Annotated[str, Path()],
    current_user: Annotated[str, get_current_user],
) -> BookResponse:
    """Retrieve a book by ID. Requires authentication."""
    result = service.get_book(book_id)
    return BookResponse(**result)
```

- [ ] **Step 4: Run — expect PASS**

```bash
uv run pytest tests/test_routes/test_books.py -v
```

- [ ] **Step 5: Run ruff**

```bash
uv run ruff check src/routes/books.py tests/test_routes/test_books.py
uv run ruff format src/routes/books.py tests/test_routes/test_books.py
```

---

## Task 9: FastAPI Application (TDD)

**Files:**
- Create: `src/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: RED — Tests for app-level behavior**

Create `tests/test_main.py`:

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_cors_headers(client):
    """CORS headers should be present on responses."""
    response = client.options("/api/auth/login")
    assert "access-control-allow-origin" in response.headers


def test_static_html_served(client):
    """GET /static/index.html should return the HTML client."""
    response = client.get("/static/index.html")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
```

- [ ] **Step 2: Run — expect FAIL**

```bash
uv run pytest tests/test_main.py -v
```

- [ ] **Step 3: GREEN — Create src/main.py**

```python
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from src.routes.auth import router as auth_router
from src.routes.books import router as books_router
from src.exceptions import BookNotFoundError, NotAuthenticatedError

app = FastAPI(title="Books API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(books_router)


@app.get("/static/index.html", response_class=HTMLResponse)
async def serve_index_html():
    """Serve the single-page HTML client."""
    html_path = Path(__file__).parent.parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert validation errors to 400 Bad Request."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(f"Missing or invalid field: {field}")

    return JSONResponse(
        status_code=400,
        content={"detail": "; ".join(errors)},
    )


@app.exception_handler(BookNotFoundError)
async def book_not_found_handler(request: Request, exc: BookNotFoundError):
    """Handle book not found errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(NotAuthenticatedError)
async def not_authenticated_handler(request: Request, exc: NotAuthenticatedError):
    """Handle authentication errors."""
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected server errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Lambda handler
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = None
```

- [ ] **Step 4: Run — expect PASS**

```bash
uv run pytest tests/test_main.py -v
```

- [ ] **Step 5: Run ruff**

```bash
uv run ruff check src/main.py tests/test_main.py
uv run ruff format src/main.py tests/test_main.py
```

---

## Task 10: Test Fixtures (Refactor)

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create tests/__init__.py**

```python
# Tests package
```

- [ ] **Step 2: Create tests/conftest.py**

```python
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3

from src.main import app
from src.config import settings
from src.auth import token_store


@pytest.fixture
def sample_book():
    return {
        "id": "/books/id1",
        "author": "/authors/id1",
        "name": "Fancy Tech",
        "note": "Awesome book for beginners in Fancy.",
        "serial": "C040102",
    }


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        table = dynamodb.create_table(
            TableName=settings.books_table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


@pytest.fixture
def auth_token():
    return token_store.create_token("admin")
```

- [ ] **Step 3: Refactor test files to use conftest fixtures**

Update `tests/test_routes/test_books.py` to use `client`, `dynamodb_table`, `auth_token` from conftest (remove local fixture definitions).

Update `tests/test_routes/test_auth.py` to use `client` from conftest.

Update `tests/test_main.py` to use `client` from conftest.

- [ ] **Step 4: Verify all tests pass**

```bash
uv run pytest -v
```

---

## Task 11: Integration Tests (TDD)

**Files:**
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_books.py`

- [ ] **Step 1: Create tests/integration/__init__.py**

```python
# Integration tests package
```

- [ ] **Step 2: Write integration test with full auth + book lifecycle**

Create `tests/integration/test_books.py`:

```python
import pytest
from fastapi.testclient import TestClient


def test_full_auth_and_book_lifecycle(client: TestClient, dynamodb_table):
    """Integration: login → create book → get book → unauthorized access."""
    # Step 1: Login
    login_resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create book
    book_data = {
        "id": "/books/int-test",
        "author": "/authors/test",
        "name": "Integration Book",
        "note": "Testing full flow.",
        "serial": "INT001",
    }
    create_resp = client.post("/api/books", json=book_data, headers=headers)
    assert create_resp.status_code == 201

    # Step 3: Get book
    get_resp = client.get(f"/api/books/{book_data['id']}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == book_data["name"]

    # Step 4: Unauthorized access
    no_auth_resp = client.get(f"/api/books/{book_data['id']}")
    assert no_auth_resp.status_code == 401

    # Step 5: Not found
    nf_resp = client.get("/api/books/nonexistent", headers=headers)
    assert nf_resp.status_code == 404
```

- [ ] **Step 3: Run — expect PASS**

```bash
uv run pytest tests/integration/test_books.py -v
```

- [ ] **Step 4: Run ruff**

```bash
uv run ruff check tests/integration/test_books.py
uv run ruff format tests/integration/test_books.py
```

---

## Task 12: Coverage Gate

**Files:** No file changes.

- [ ] **Step 1: Run coverage check**

```bash
make coverage
```

Expected: ≥ 90% coverage.

- [ ] **Step 2: If < 90%, identify gaps and write targeted tests**

Common gap areas:
- `NotAuthenticatedError` handler branch in `main.py`
- Auth middleware edge cases (malformed Authorization header)
- Error paths in routes

Write targeted tests, re-run until ≥ 90%.

---

## Task 13: Run All Tests + pre-commit Gate

**Files:** No file changes.

- [ ] **Step 1: Run full test suite**

```bash
make test
```

Expected: All tests pass (~20+ tests).

- [ ] **Step 2: Run pre-commit**

```bash
make precommit
```

Expected: All hooks pass.

- [ ] **Step 3: Run coverage**

```bash
make coverage
```

Expected: ≥ 90%.

---

## Task 14: Single-Page HTML Client

**Files:**
- Create: `static/index.html`
- Create: `static/__init__.py` (not needed — static dir is not a Python package)

- [ ] **Step 1: Create static directory**

```bash
mkdir -p static
```

- [ ] **Step 2: Create static/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Books API Client</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        h1 { text-align: center; margin-bottom: 2rem; color: #1a1a2e; }
        .card { background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-bottom: 1rem; color: #16213e; }
        label { display: block; margin-bottom: 0.25rem; font-weight: 500; font-size: 0.9rem; }
        input, textarea { width: 100%; padding: 0.5rem; margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
        button { background: #0f3460; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; font-size: 1rem; }
        button:hover { background: #16213e; }
        button.secondary { background: #e94560; }
        button.secondary:hover { background: #c73e54; }
        .error { color: #e94560; background: #ffe0e6; padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem; }
        .success { color: #0f3460; background: #e0f0ff; padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem; }
        pre { background: #f8f9fa; padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.85rem; }
        .hidden { display: none; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        @media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Books API</h1>

        <!-- Login Panel -->
        <div id="login-panel" class="card">
            <h2>Login</h2>
            <div id="login-error" class="error hidden"></div>
            <label for="username">Username</label>
            <input type="text" id="username" value="admin" placeholder="admin">
            <label for="password">Password</label>
            <input type="password" id="password" value="admin123" placeholder="admin123">
            <button onclick="login()">Login</button>
        </div>

        <!-- Books Panel -->
        <div id="books-panel" class="hidden">
            <div class="card">
                <h2>Welcome <span id="user-display"></span></h2>
                <button class="secondary" onclick="logout()">Logout</button>
            </div>

            <!-- Create Book -->
            <div class="card">
                <h2>Create Book</h2>
                <div id="create-error" class="error hidden"></div>
                <div id="create-success" class="success hidden"></div>
                <label for="book-id">ID</label>
                <input type="text" id="book-id" placeholder="/books/id1">
                <label for="book-author">Author</label>
                <input type="text" id="book-author" placeholder="/authors/id1">
                <label for="book-name">Name</label>
                <input type="text" id="book-name" placeholder="Book Title">
                <label for="book-note">Note</label>
                <textarea id="book-note" rows="2" placeholder="Book description"></textarea>
                <label for="book-serial">Serial</label>
                <input type="text" id="book-serial" placeholder="C040102">
                <button onclick="createBook()">Create Book</button>
            </div>

            <!-- Get Book -->
            <div class="card">
                <h2>Get Book by ID</h2>
                <div id="get-error" class="error hidden"></div>
                <label for="get-id">Book ID</label>
                <input type="text" id="get-id" placeholder="/books/id1">
                <button onclick="getBook()">Fetch</button>
                <div id="get-result" class="hidden" style="margin-top: 1rem;">
                    <pre id="get-result-data"></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = "http://localhost:8000";
        let token = localStorage.getItem("books_api_token");

        // Auto-login if token exists
        if (token) {
            showBooksPanel();
        }

        function showError(elementId, message) {
            const el = document.getElementById(elementId);
            el.textContent = message;
            el.classList.remove("hidden");
        }

        function hideError(elementId) {
            document.getElementById(elementId).classList.add("hidden");
        }

        function showSuccess(elementId, message) {
            const el = document.getElementById(elementId);
            el.textContent = message;
            el.classList.remove("hidden");
            setTimeout(() => el.classList.add("hidden"), 5000);
        }

        function authHeaders() {
            return {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            };
        }

        async function login() {
            hideError("login-error");
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            try {
                const resp = await fetch(`${API_BASE}/api/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password }),
                });

                if (!resp.ok) {
                    const data = await resp.json();
                    showError("login-error", data.detail || "Login failed");
                    return;
                }

                const data = await resp.json();
                token = data.token;
                localStorage.setItem("books_api_token", token);
                showBooksPanel();
            } catch (err) {
                showError("login-error", "Network error: " + err.message);
            }
        }

        function showBooksPanel() {
            document.getElementById("login-panel").classList.add("hidden");
            document.getElementById("books-panel").classList.remove("hidden");
            document.getElementById("user-display").textContent = "(authenticated)";
        }

        function logout() {
            token = null;
            localStorage.removeItem("books_api_token");
            document.getElementById("login-panel").classList.remove("hidden");
            document.getElementById("books-panel").classList.add("hidden");
        }

        async function createBook() {
            hideError("create-error");
            hideError("create-success");
            const book = {
                id: document.getElementById("book-id").value,
                author: document.getElementById("book-author").value,
                name: document.getElementById("book-name").value,
                note: document.getElementById("book-note").value,
                serial: document.getElementById("book-serial").value,
            };

            try {
                const resp = await fetch(`${API_BASE}/api/books`, {
                    method: "POST",
                    headers: authHeaders(),
                    body: JSON.stringify(book),
                });

                if (!resp.ok) {
                    const data = await resp.json();
                    showError("create-error", data.detail || "Failed to create book");
                    return;
                }

                const data = await resp.json();
                showSuccess("create-success", `Book created: ${data.name}`);
            } catch (err) {
                showError("create-error", "Network error: " + err.message);
            }
        }

        async function getBook() {
            hideError("get-error");
            const bookId = document.getElementById("get-id").value;

            try {
                const resp = await fetch(`${API_BASE}/api/books/${encodeURIComponent(bookId)}`, {
                    headers: authHeaders(),
                });

                if (!resp.ok) {
                    const data = await resp.json();
                    showError("get-error", data.detail || "Failed to fetch book");
                    document.getElementById("get-result").classList.add("hidden");
                    return;
                }

                const data = await resp.json();
                document.getElementById("get-result-data").textContent = JSON.stringify(data, null, 2);
                document.getElementById("get-result").classList.remove("hidden");
            } catch (err) {
                showError("get-error", "Network error: " + err.message);
            }
        }
    </script>
</body>
</html>
```

- [ ] **Step 3: Verify HTML client is served**

```bash
uv run python -c "
from src.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
resp = client.get('/static/index.html')
assert resp.status_code == 200
assert 'Books API' in resp.text
print('HTML client served correctly')
"
```

Expected: `HTML client served correctly`

---

## Task 15: Serverless Framework Configuration

**Files:**
- Create: `serverless.yml`

- [ ] **Step 1: Create serverless.yml**

```yaml
service: books-api
frameworkVersion: '3'

provider:
  name: aws
  runtime: python3.14
  region: us-east-1
  environment:
    BOOKS_TABLE_NAME: ${self:custom.tableName}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:PutItem
            - dynamodb:GetItem
          Resource: !GetAtt BooksTable.Arn

functions:
  api:
    handler: src.main.handler
    events:
      - http:
          path: /api/{proxy+}
          method: ANY
          cors: true
      - http:
          path: /static/{proxy+}
          method: ANY
          cors: true

resources:
  Resources:
    BooksTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.tableName}
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST

custom:
  tableName: ${opt:stage, 'dev'}-books
```

- [ ] **Step 2: Verify syntax**

```bash
serverless print
```

---

## Task 16: README Documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# Books API

FastAPI-based REST API for managing books with token-based authentication, deployed on AWS Lambda with DynamoDB.

## Tech Stack

- **Python 3.14**
- **FastAPI** — Web framework
- **Pydantic 2** — Data validation
- **AWS DynamoDB** — Database
- **AWS Lambda + API Gateway** — Deployment
- **Serverless Framework** — Infrastructure as Code
- **uv** — Package management
- **ruff** — Linting and formatting
- **pre-commit** — Git quality gate
- **Make** — Developer task runner

## Prerequisites

- Python 3.14 or higher
- [uv](https://docs.astral.sh/uv/) — Package manager
- [GNU Make](https://www.gnu.org/software/make/) — Task runner
- Serverless Framework (`npm install -g serverless`)
- AWS CLI configured with credentials

## Quick Start

```bash
# Install dependencies and hooks
make setup

# Start development server
make dev

# Run all tests
make test

# Check coverage (90% minimum)
make coverage

# Lint and format
make fix

# Deploy to AWS
make deploy
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup` | Install dependencies and pre-commit hooks |
| `make dev` | Start FastAPI development server |
| `make test` | Run all tests (unit + integration) |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make coverage` | Run tests with 90% coverage gate |
| `make lint` | Run ruff linter |
| `make format` | Run ruff formatter |
| `make fix` | Auto-fix lint issues and format |
| `make precommit` | Run pre-commit hooks on all files |
| `make deploy` | Deploy to AWS (dev stage) |
| `make deploy-prod` | Deploy to AWS (production stage) |
| `make remove` | Remove deployed AWS resources |
| `make clean` | Remove local artifacts and caches |

## Development Methodology

This project follows **Test-Driven Development (TDD)**:
1. Write a failing test first (Red)
2. Write minimal implementation to pass (Green)
3. Refactor while tests stay green

**Coverage requirement:** ≥ 90% line coverage on all source files.

## Authentication

The API uses simple token-based authentication:

| Credential | Value |
|------------|-------|
| Username | `admin` |
| Password | `admin123` |

All `/api/books/*` endpoints require a `Authorization: Bearer <token>` header. Obtain a token via `POST /api/auth/login`.

## Testing

### Run all tests

```bash
make test
```

### Run with coverage

```bash
make coverage
```

## Code Quality

```bash
make lint      # Check
make format    # Format
make fix       # Auto-fix + format
make precommit # Run pre-commit
```

## Deployment

```bash
make deploy          # Deploy to dev
make deploy-prod     # Deploy to production
make remove          # Tear down
```

## API Endpoints

### POST /api/auth/login

Authenticate and get a token.

**Request:**
```json
{ "username": "admin", "password": "admin123" }
```

**Responses:**
- `200 OK` — Returns `{"token": "..."}`
- `401 Unauthorized` — Invalid credentials
- `400 Bad Request` — Missing fields

### POST /api/books

Create a new book. **Requires auth.**

**Request:**
```json
{
  "id": "/books/id1",
  "author": "/authors/id1",
  "name": "Fancy Tech",
  "note": "Awesome book for beginners.",
  "serial": "C040102"
}
```

**Responses:**
- `201 Created` — Success
- `400 Bad Request` — Missing/invalid fields
- `401 Unauthorized` — Missing or invalid token
- `500 Internal Server Error` — Server error

### GET /api/books/{id}

Retrieve a book by ID. **Requires auth.**

**Responses:**
- `200 OK` — Book found
- `401 Unauthorized` — Missing or invalid token
- `404 Not Found` — Book doesn't exist
- `500 Internal Server Error` — Server error

## HTML Client

A single-page HTML client is available at `/static/index.html` when running locally:

```
http://localhost:8000/static/index.html
```

It provides a browser-based UI for login, creating books, and fetching books by ID.

## CORS

CORS is enabled for all origins (`*`) to support direct browser access.

## Project Structure

```
├── src/
│   ├── main.py              # FastAPI app, middleware, exception handlers
│   ├── models.py            # Pydantic 2 schemas
│   ├── config.py            # Environment settings
│   ├── exceptions.py        # Custom exceptions
│   ├── auth.py              # Token store, login, auth dependency
│   ├── routes/
│   │   ├── auth.py          # Auth endpoints
│   │   └── books.py         # Book endpoints (protected)
│   └── services/
│       └── book_service.py  # DynamoDB operations
├── static/
│   └── index.html           # Single-page HTML client
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_config.py       # Config tests
│   ├── test_models.py       # Model tests
│   ├── test_exceptions.py   # Exception tests
│   ├── test_auth.py         # Auth logic tests
│   ├── test_services/       # Service tests
│   ├── test_routes/         # Route tests
│   └── integration/         # Integration tests
├── serverless.yml           # Serverless Framework config
├── pyproject.toml           # uv project config
├── .pre-commit-config.yaml  # pre-commit hooks
├── Makefile                 # Developer task runner
└── README.md               # This file
```
```

---

## Task 17: Final Verification

**Files:** No file changes.

- [ ] **Step 1: Run full test suite**

```bash
make test
```

Expected: All tests pass.

- [ ] **Step 2: Run coverage gate**

```bash
make coverage
```

Expected: ≥ 90%.

- [ ] **Step 3: Run pre-commit**

```bash
make precommit
```

Expected: All hooks pass.

- [ ] **Step 4: Verify app + HTML client**

```bash
uv run python -c "
from src.main import app
from fastapi.testclient import TestClient
c = TestClient(app)
assert c.get('/static/index.html').status_code == 200
print('All good')
"
```

- [ ] **Step 5: Verify all files exist**

```bash
ls -la src/main.py src/models.py src/config.py src/exceptions.py src/auth.py src/routes/auth.py src/routes/books.py src/services/book_service.py tests/conftest.py tests/test_routes/test_books.py tests/test_routes/test_auth.py tests/integration/test_books.py static/index.html serverless.yml pyproject.toml .pre-commit-config.yaml Makefile README.md
```

- [ ] **Step 6: Verify Makefile targets**

```bash
make help
make lint
make format
make coverage
```

---

## Spec Coverage Checklist

| Spec Section | Task | Status |
|--------------|------|--------|
| Monolithic Lambda | Task 15 | ✅ |
| Auth: POST /api/auth/login (200/401/400) | Tasks 7, 9 | ✅ |
| Auth middleware (401 on missing/invalid token) | Tasks 5, 8 | ✅ |
| POST /api/books (201/400/401/500) | Tasks 8, 9 | ✅ |
| GET /api/books/{id} (200/401/404/500) | Tasks 8, 9 | ✅ |
| Pydantic 2 models | Task 4 | ✅ |
| Error handling | Tasks 4, 9 | ✅ |
| DynamoDB schema | Tasks 6, 15 | ✅ |
| Unit tests (all categories) | Tasks 4-11 | ✅ |
| Integration test (auth + book lifecycle) | Task 11 | ✅ |
| CORS | Task 9 | ✅ |
| Serverless config | Task 15 | ✅ |
| README | Task 16 | ✅ |
| FastAPI best practices | Tasks 4, 7, 8, 9 | ✅ |
| uv package management | All tasks | ✅ |
| ruff + pre-commit | Tasks 2, 4-11, 13, 17 | ✅ |
| Makefile | Task 3, 13, 16, 17 | ✅ |
| Python 3.14 | Task 1, Task 15 | ✅ |
| TDD methodology | All tasks | ✅ |
| 90% coverage | Task 12, 13, 17 | ✅ |
| static/index.html | Task 14 | ✅ |

**No gaps found.**

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-15-fastapi-books-api-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** — Fresh subagent per task, review between tasks

**2. Inline Execution** — Execute in this session with checkpoints

Which approach?

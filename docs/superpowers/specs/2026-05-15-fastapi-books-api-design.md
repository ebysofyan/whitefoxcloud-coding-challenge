# Design Spec: FastAPI Books API on AWS Lambda

**Date:** 2026-05-15
**Status:** Draft — Awaiting Eby Review
**Challenge:** Python Coding Challenge — Rest API on FastAPI

---

## 1. Objective

Implement a RESTful Books API using FastAPI, deployed on AWS Lambda with API Gateway and DynamoDB, managed via Serverless Framework. The API supports authentication, creating and retrieving books with proper error handling, unit/integration tests, CORS for browser access, and a single-page HTML client.

**Development methodology:** Test-Driven Development (TDD). Write failing tests first, then implement minimal code to pass. Red-Green-Refactor cycle for every feature.

**Coverage target:** Minimum 90% line coverage across all source files.

---

## 2. Architecture

### 2.1 Deployment Model

**Monolithic Lambda** — Single Lambda function running the full FastAPI application. API Gateway routes all `/api/*` requests to this function. FastAPI handles internal routing.

**Rationale:** Challenge scope (2 endpoints + auth) does not justify per-route Lambdas. Simpler deployment, shared middleware, single cold start.

### 2.2 Project Structure

```
whitefoxcloud-coding-challenge/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory, CORS, exception handlers
│   ├── models.py            # Pydantic 2 schemas
│   ├── auth.py              # Token store, login, auth middleware
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── books.py         # APIRouter(prefix="/api/books", tags=["books"])
│   │   └── auth.py          # APIRouter(prefix="/api/auth", tags=["auth"])
│   ├── services/
│   │   ├── __init__.py
│   │   └── book_service.py  # DynamoDB CRUD (boto3, sync def)
│   └── config.py            # pydantic-settings (table name, region, env)
├── static/
│   └── index.html           # Single-page HTML client (login + book CRUD)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures (TestClient, moto, auth)
│   ├── test_config.py       # Config unit tests
│   ├── test_models.py       # Model unit tests
│   ├── test_exceptions.py   # Exception unit tests
│   ├── test_auth.py         # Auth unit tests
│   ├── test_services/       # Service unit tests
│   ├── test_routes/         # Route unit tests
│   └── integration/         # Integration tests
├── serverless.yml           # Lambda + API Gateway + DynamoDB
├── pyproject.toml           # uv project config, dependencies, tool configs
├── .pre-commit-config.yaml  # pre-commit hooks (ruff, ruff-format)
├── Makefile                 # Developer-friendly task runner
└── README.md                # Setup, run, test, deploy instructions
```

### 2.3 Data Flow

```
Browser → static/index.html → API Gateway → Lambda (FastAPI) → Auth Middleware → Router → Service → DynamoDB
                                                                                      ↓
Browser ← HTML UI ← JSON Response ← API Gateway ← Lambda ← Exception Handler ← Error
```

---

## 3. Authentication

### 3.1 Token Strategy

**Basic token-based auth** (no JWT). Simple random token generated on login, stored in-memory.

| Aspect | Detail |
|--------|--------|
| Token format | `secrets.token_hex(32)` (64-char hex string) |
| Storage | In-memory dict `{token: username}` |
| Transmission | `Authorization: Bearer <token>` header |
| Expiry | No expiry (coding challenge scope) |
| Users | Hardcoded: `{"admin": "admin123"}` |

### 3.2 POST `/api/auth/login` — Authenticate

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Responses:**
| Status | Condition |
|--------|-----------|
| 200 OK | Valid credentials, returns `{"token": "<hex_token>"}` |
| 401 Unauthorized | Invalid credentials |
| 400 Bad Request | Missing username or password |

### 3.3 Auth Middleware

All `/api/books/*` endpoints require a valid `Authorization: Bearer <token>` header.

| Condition | Response |
|-----------|----------|
| Missing header | 401 `{"detail": "Missing authorization header"}` |
| Invalid token | 401 `{"detail": "Invalid or expired token"}` |
| Valid token | Request proceeds to handler |

**Exception:** `/api/auth/*` endpoints are public (no auth required).

---

## 4. API Endpoints

### 4.1 POST `/api/auth/login` — Login

See Section 3.2.

### 4.2 POST `/api/books` — Create Book

**Auth required:** Yes (Bearer token)

**Request:**
```json
{
  "id": "/books/id1",
  "author": "/authors/id1",
  "name": "Fancy Tech",
  "note": "Awesome book for beginners in Fancy.",
  "serial": "C040102"
}
```

**Responses:**
| Status | Condition |
|--------|-----------|
| 201 Created | Book successfully created |
| 400 Bad Request | Missing/invalid payload fields |
| 401 Unauthorized | Missing or invalid auth token |
| 500 Internal Server Error | Server-side exception |

### 4.3 GET `/api/books/{id}` — Get Book

**Auth required:** Yes (Bearer token)

**Request:** `GET /api/books/{id}`

**Responses:**
| Status | Condition |
|--------|-----------|
| 200 OK | Book found, returns full book JSON |
| 401 Unauthorized | Missing or invalid auth token |
| 404 Not Found | Book ID does not exist |
| 500 Internal Server Error | Server-side exception |

---

## 5. Pydantic 2 Models

### 5.1 Auth Models

```python
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
```

### 5.2 Book Models

```python
class BookCreate(BaseModel):
    id: str
    author: str
    name: str
    note: str
    serial: str

class BookResponse(BaseModel):
    id: str
    author: str
    name: str
    note: str
    serial: str
```

All fields required. No `...` ellipsis. Pydantic 2 `model_dump()` for serialization.

---

## 6. Error Handling

### 6.1 Strategy

Centralized exception handlers in `main.py`:

| Exception | HTTP Status | Response Body |
|-----------|-------------|---------------|
| `RequestValidationError` | 400 | `{"detail": "Missing required field: <field_name>"}` |
| `NotAuthenticatedError` (custom) | 401 | `{"detail": "Missing or invalid auth token"}` |
| `BookNotFoundError` (custom) | 404 | `{"detail": "Book not found"}` |
| `Exception` (catch-all) | 500 | `{"detail": "Internal server error"}` |

### 6.2 Custom Exceptions

```python
class BookNotFoundError(Exception):
    pass

class NotAuthenticatedError(Exception):
    pass
```

### 6.3 Error Response Format

```json
{"detail": "Descriptive error message"}
```

---

## 7. DynamoDB Schema

### 7.1 Table Definition

| Property | Value |
|----------|-------|
| Table Name | `Books` (configurable via `BOOKS_TABLE_NAME` env var) |
| Partition Key | `id` (String) |
| Billing Mode | `PAY_PER_REQUEST` |

### 7.2 Item Structure

```json
{
  "id": "/books/id1",
  "author": "/authors/id1",
  "name": "Fancy Tech",
  "note": "Awesome book for beginners in Fancy.",
  "serial": "C040102"
}
```

---

## 8. Testing Strategy

### 8.1 TDD Methodology

All code follows **Red-Green-Refactor** cycle:
1. **Red** — Write failing test
2. **Green** — Minimal implementation
3. **Refactor** — Clean up while tests green

### 8.2 Coverage Requirement

**Minimum 90% line coverage** across all `src/` files.

```bash
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90 -v
```

### 8.3 Test Categories

| Category | Files | Scope |
|----------|-------|-------|
| Config | `tests/test_config.py` | Settings defaults |
| Models | `tests/test_models.py` | Pydantic validation |
| Exceptions | `tests/test_exceptions.py` | Custom exception behavior |
| Auth | `tests/test_auth.py` | Login, token validation, middleware |
| Services | `tests/test_services/test_book_service.py` | DynamoDB CRUD |
| Routes | `tests/test_routes/test_books.py` | Endpoint behaviors |
| Routes | `tests/test_routes/test_auth.py` | Auth endpoint behaviors |
| Integration | `tests/integration/test_books.py` | Full lifecycle with auth |

### 8.4 Integration Test

1. POST `/api/auth/login` → get token
2. POST `/api/books` with token → verify 201
3. GET `/api/books/{id}` with token → verify 200
4. GET `/api/books/{id}` without token → verify 401
5. GET non-existent book → verify 404

---

## 9. Deployment (Serverless Framework)

### 9.1 serverless.yml

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

### 9.2 Static File Serving

The `static/index.html` is served via a catch-all route in FastAPI:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")
```

**Note:** `StaticFiles` works locally. For Lambda deployment, the HTML file is served via a dedicated route that reads the file content (Lambda filesystem is read-only after deployment). Alternative: serve HTML from a route handler that returns `FileResponse`.

---

## 10. CORS (Bonus Requirement)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

`cors: true` in `serverless.yml` enables API Gateway CORS headers. Combined with FastAPI middleware, supports direct browser access.

---

## 11. Single-Page HTML Client

### 11.1 Purpose

A single `static/index.html` file that provides a browser-based UI for:
- Login (username/password → stores token in localStorage)
- Create book (form with id, author, name, note, serial)
- View book by ID (input field + fetch button)
- Displays results and errors inline

### 11.2 Tech

- Vanilla HTML + CSS + JavaScript (no frameworks)
- `fetch()` API for HTTP requests
- `localStorage` for token persistence
- Minimal, clean styling

### 11.3 UI Sections

1. **Login Panel** — Username/password fields, Login button
2. **Books Panel** (hidden until authenticated)
   - Create Book form (5 fields + Submit)
   - Get Book by ID (input + Fetch button)
   - Results display area (JSON or formatted)
   - Error display area
   - Logout button (clears token)

### 11.4 API Base URL

Configurable via a constant at the top of the script:

```javascript
const API_BASE = "http://localhost:8000";  // Change for deployed URL
```

---

## 12. Dependencies & Tooling

### 12.1 Package Management: uv

All dependency management via `uv`. `pyproject.toml` is the single source of truth.

### 12.2 Runtime Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server (local dev) |
| `boto3` | AWS SDK for DynamoDB |
| `pydantic-settings` | Environment-based configuration |
| `mangum` | ASGI adapter for AWS Lambda |

### 12.3 Development Dependencies

| Package | Purpose |
|---------|---------|
| `pytest` | Test framework |
| `pytest-cov` | Coverage measurement |
| `httpx` | Async test client |
| `moto` | AWS service mocking |
| `ruff` | Linter + formatter |
| `pre-commit` | Git hook framework |

---

## 13. Code Quality: Ruff + pre-commit

### 13.1 Ruff Configuration

```toml
[tool.ruff]
target-version = "py314"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

### 13.2 pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

---

## 14. Makefile — Developer Task Runner

### 14.1 Targets

| Target | Command | Description |
|--------|---------|-------------|
| `make help` | — | List all available targets |
| `make setup` | `uv sync --all-extras && uv run pre-commit install` | Install deps + hooks |
| `make dev` | `uv run fastapi dev src.main:app` | Start dev server |
| `make test` | `uv run pytest -v` | Run all tests |
| `make test-unit` | `uv run pytest tests/ -v --ignore=tests/integration` | Run unit tests only |
| `make test-integration` | `uv run pytest tests/integration/ -v` | Run integration tests only |
| `make coverage` | `uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90 -v` | 90% coverage gate |
| `make lint` | `uv run ruff check .` | Lint source code |
| `make format` | `uv run ruff format .` | Format source code |
| `make fix` | `uv run ruff check . --fix && uv run ruff format .` | Auto-fix lint + format |
| `make precommit` | `uv run pre-commit run --all-files` | Run pre-commit on all files |
| `make deploy` | `serverless deploy` | Deploy to AWS |
| `make deploy-prod` | `serverless deploy --stage production` | Deploy to production |
| `make remove` | `serverless remove` | Remove AWS resources |
| `make clean` | `rm -rf .venv .ruff_cache .pytest_cache __pycache__ .serverless .coverage htmlcov` | Clean artifacts |

---

## 15. FastAPI Best Practices Applied

| Practice | Implementation |
|----------|----------------|
| `Annotated` params | `Path()`, `Body()` declarations |
| No `...` ellipsis | Required fields without defaults |
| Return types | `-> BookResponse` on routes |
| Router-level config | `prefix`, `tags` on `APIRouter` |
| `def` not `async def` | boto3 is blocking → threadpool |
| One HTTP op per function | Separate handlers |
| `pyproject.toml` entrypoint | `[tool.fastapi]` config |
| No RootModels | `Annotated` + type annotations |
| CORS middleware | `CORSMiddleware` |
| Pydantic 2 | `model_dump()`, v2 validation |

---

## 16. Local Development

### 16.1 Setup

```bash
make setup
```

### 16.2 Run Locally

```bash
make dev
```

Access the HTML client at: `http://localhost:8000/static/index.html`

### 16.3 Run Tests

```bash
make test
make coverage
```

### 16.4 Lint & Format

```bash
make fix
```

### 16.5 Deploy

```bash
make deploy
```

---

## 17. Risks and Tradeoffs

| Risk | Mitigation |
|------|------------|
| Lambda cold start | FastAPI lightweight; ~200-500ms |
| DynamoDB throttling | `PAY_PER_REQUEST` auto-scales |
| CORS `allow_origins=["*"]` | OK for challenge; restrict in production |
| In-memory token store | Tokens lost on Lambda cold start; acceptable for challenge scope |
| Python 3.14 on Lambda | May not be available; fallback to 3.13 |
| 90% coverage | Small codebase makes it achievable; test all error paths |
| Static files on Lambda | Lambda filesystem read-only; serve HTML via route handler instead of `StaticFiles` |

---

## 18. Success Criteria

- [ ] POST `/api/auth/login` returns 200 with token on valid credentials
- [ ] POST `/api/auth/login` returns 401 on invalid credentials
- [ ] POST `/api/books` returns 201 with valid token + payload
- [ ] POST `/api/books` returns 401 without token
- [ ] POST `/api/books` returns 400 on missing fields
- [ ] GET `/api/books/{id}` returns 200 with valid token
- [ ] GET `/api/books/{id}` returns 401 without token
- [ ] GET `/api/books/{id}` returns 404 for non-existent ID
- [ ] Unit tests cover all endpoints and error cases
- [ ] At least one integration test passes (with auth flow)
- [ ] CORS headers present (browser-accessible)
- [ ] `serverless deploy` succeeds
- [ ] README documents setup, run, test, deploy
- [ ] pre-commit hooks installed and passing
- [ ] ruff linting clean on all source files
- [ ] Makefile targets all functional
- [ ] Test coverage ≥ 90%
- [ ] All code written TDD-style
- [ ] `static/index.html` functional: login → create book → get book → logout

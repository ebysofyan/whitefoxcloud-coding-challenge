# Books API — Python Coding Challenge

RESTful API built with FastAPI for book management, backed by AWS DynamoDB and deployable via Serverless Framework on AWS Lambda.

## Tech Stack

- **Python 3.14** with **FastAPI** + **Pydantic 2**
- **AWS DynamoDB** (local via Docker or cloud)
- **AWS Lambda** + **API Gateway** via [Serverless Framework](https://www.serverless.com/)
- **uv** — package manager
- **ruff** — linter & formatter
- **pytest** + **pytest-cov** — testing with ≥90% coverage gate

## Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Docker (for DynamoDB Local)
- [Serverless Framework](https://www.serverless.com/) v3 (`npm i -g serverless@3`)
- AWS CLI configured (for deployment)

## Getting Started

```bash
# 1. Install dependencies and pre-commit hooks
make setup

# 2. Start DynamoDB Local
make db

# 3. Create .env (only needed once)
echo "DYNAMODB_ENDPOINT=http://localhost:18749" > .env

# 4. Start dev server (http://localhost:9876)
make dev
```

## Running Tests

```bash
# Run all tests (unit + integration)
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with 90% coverage gate
make coverage
```

**Current coverage: 100% (55 tests)**

## API Endpoints

All `/api/books` endpoints require authentication via Bearer token.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/auth/login` | No | Login, returns access token |
| `POST` | `/api/books` | Yes | Create a book |
| `GET` | `/api/books` | Yes | List books (cursor-paginated) |
| `GET` | `/api/books/{id}` | Yes | Get a book by ID |
| `DELETE` | `/api/books/{id}` | Yes | Delete a book |

### Example: Create a Book

```bash
# Login
curl -s -X POST http://localhost:9876/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Create book (use token from login response)
curl -X POST http://localhost:9876/api/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "id": "/books/id1",
    "author": "/authors/id1",
    "name": "Fancy Tech",
    "note": "Awesome book for beginners in Fancy.",
    "serial": "C040102"
  }'
# → 201 Created

# Get book
curl http://localhost:9876/api/books/id1 \
  -H "Authorization: Bearer <token>"
# → 200 OK with book JSON
```

Default credentials: `admin` / `admin123`

### Error Responses

| Status | When |
|--------|------|
| `400 Bad Request` | Missing required fields in the payload |
| `401 Unauthorized` | Missing or invalid Bearer token |
| `404 Not Found` | Book ID does not exist |
| `500 Internal Server Error` | Unexpected server-side error |

## Web UI (Bonus)

Open `http://localhost:9876` in a browser for a single-page client that supports login/logout, listing books, viewing details, creating, and deleting books.

## Project Structure

```
├── src/
│   ├── main.py              # FastAPI app + Lambda handler (mangum)
│   ├── config.py            # Pydantic settings
│   ├── models.py            # Request/response schemas
│   ├── exceptions.py        # Custom exception classes
│   ├── auth.py              # Token-based authentication
│   ├── routes/
│   │   ├── auth.py          # Login endpoint
│   │   └── books.py         # Book CRUD endpoints
│   └── services/
│       └── book_service.py  # DynamoDB operations
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_auth.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_main.py
│   ├── test_models.py
│   ├── test_routes/         # Route-level tests
│   ├── test_services/       # Service-level tests
│   └── integration/         # Integration tests
├── static/
│   └── index.html           # Web UI client
├── serverless.yml           # AWS Lambda deployment config
├── pyproject.toml           # Project metadata + dependencies
├── Makefile                 # Developer task runner
└── docker-compose.yml       # DynamoDB Local
```

## Deployment

```bash
make deploy          # Deploy to AWS (dev stage)
make deploy-prod     # Deploy to AWS (production)
make remove          # Remove deployed AWS resources
```

# Books API

FastAPI-based REST API for book management with DynamoDB backend, deployed on AWS Lambda via Serverless Framework.

## Tech Stack

- **Runtime**: Python 3.14
- **Framework**: FastAPI + Pydantic 2
- **Database**: Amazon DynamoDB
- **Deployment**: Serverless Framework on AWS Lambda
- **Package Manager**: uv
- **Linting/Formatting**: ruff + pre-commit
- **Testing**: pytest + pytest-cov (≥90% coverage)

## Quick Start

### Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- AWS CLI configured (for deployment)
- Serverless Framework (`npm i -g serverless`)

### Local Development

**Option A: With DynamoDB Local (no AWS credentials needed)**

```bash
# Start DynamoDB Local
make db

# Create .env file
echo "DYNAMODB_ENDPOINT=http://localhost:18749" > .env

# Install dependencies + pre-commit hooks
make setup

# Start dev server (runs on port 9876)
make dev
```

**Option B: With AWS DynamoDB (requires AWS credentials)**

```bash
# Configure AWS credentials
aws configure

# Install dependencies + pre-commit hooks
make setup

# Start dev server
make dev
```

**Common commands:**

```bash
# Run tests with coverage
make test

# Lint and format
make lint
make format

# Auto-fix lint issues + format
make fix

# Run tests with 90% coverage gate
make coverage
```

### API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/auth/login` | Login with username/password | No |
| GET | `/api/books` | List all books | Yes |
| POST | `/api/books` | Create a book | Yes |
| GET | `/api/books/{book_id}` | Get a book by ID | Yes |
| DELETE | `/api/books/{book_id}` | Delete a book | Yes |
| GET | `/` | Web UI client | No |

### Authentication

Basic token-based auth. Login returns an access token to use in subsequent requests:

```bash
# Login
curl -X POST http://localhost:9876/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token
curl http://localhost:9876/api/books/book-1 \
  -H "Authorization: Bearer <token>"
```

Default credentials: `admin` / `admin123`

### Web UI

Open `http://localhost:9876` in a browser for a single-page client with:
- Login / Logout
- List all books
- View book detail
- Create new book
- Delete book

### AWS Free Tier

DynamoDB is included in the [AWS Free Tier](https://aws.amazon.com/free/):

| Resource | Free Tier Limit |
|----------|----------------|
| Storage | 25 GB |
| Read Requests | 2.5 million/month |
| Write Requests | 1 million/month |
| Duration | 12 months |

Sufficient for development, demos, and small projects. No charges if you stay within these limits.

## Deployment

```bash
# Deploy to AWS (dev stage)
make deploy

# Deploy to production
make deploy-prod

# Remove deployment
make remove
```

## Project Structure

```
├── src/
│   ├── main.py              # FastAPI app + Lambda handler (mangum)
│   ├── config.py            # Pydantic settings
│   ├── models.py            # Request/response schemas
│   ├── exceptions.py        # Custom exceptions
│   ├── auth.py              # Token-based authentication
│   ├── routes/
│   │   ├── auth.py          # Login endpoint
│   │   └── books.py         # Book CRUD endpoints
│   └── services/
│       └── book_service.py  # DynamoDB operations
├── tests/
│   ├── test_auth.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_models.py
│   ├── test_routes/
│   │   ├── test_auth.py
│   │   └── test_books.py
│   └── test_services/
│       └── test_book_service.py
├── static/
│   └── index.html           # Web UI client
├── serverless.yml           # AWS Lambda deployment config
├── pyproject.toml           # Project metadata + deps
├── Makefile                 # Developer task runner
└── .pre-commit-config.yaml  # Git hooks
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup` | Install dependencies + pre-commit hooks |
| `make db` | Start DynamoDB Local (Docker) |
| `make dev` | Start FastAPI dev server |
| `make test` | Run all tests |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make coverage` | Run tests with 90% coverage gate |
| `make lint` | Run ruff linter |
| `make format` | Run ruff formatter |
| `make fix` | Auto-fix lint issues + format |
| `make precommit` | Run pre-commit hooks on all files |
| `make deploy` | Deploy to AWS (dev stage) |
| `make deploy-prod` | Deploy to AWS (production) |
| `make remove` | Remove deployed AWS resources |
| `make clean` | Remove local artifacts and caches |
| `make help` | Show all available targets |

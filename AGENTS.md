# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-17 14:30 UTC
**Commit:** 78a46b4
**Branch:** dev

## OVERVIEW
FastAPI Python app for book CRUD, backed by DynamoDB. Dual runtime: local dev via `uv run fastapi dev`, prod via Serverless Framework → AWS Lambda (Mangum adapter). SPA frontend served at root. Rate limiting middleware added.

## STRUCTURE
```
├── src/                    # Application package (src-layout)
│   ├── main.py            # FastAPI app + Mangum handler ← ENTRY POINT
│   ├── config.py          # Pydantic Settings + TableConfig (env-driven table naming)
│   ├── core/              # Cross-cutting infrastructure
│   │   ├── exceptions.py  # Custom exception hierarchy (BookAPIError base)
│   │   └── aws.py         # DynamoDB resource factory
│   ├── auth/              # Authentication package
│   │   └── token_store.py # TokenStore + FastAPI dependency
│   ├── schemas/           # Pydantic v2 request/response schemas
│   ├── middleware/        # ASGI middleware
│   │   ├── rate_limit.py  # Rate limit middleware dispatch
│   │   └── rate_limiter.py# Sliding window rate limiter
│   ├── routes/            # FastAPI APIRouter modules
│   └── services/          # Business logic + DynamoDB access
├── tests/                  # Mirrors src/ structure, 60+ tests, 99% coverage
├── static/index.html       # SPA frontend (served at /)
├── scripts/init_db.py      # DynamoDB table bootstrap
├── serverless.yml          # AWS infra-as-code (Lambda + API Gateway + DynamoDB)
├── docker-compose.yml      # DynamoDB Local (port 18749, in-memory)
├── pyproject.toml          # Python deps + tool configs (uv, ruff, pytest)
├── requirements.txt        # Runtime deps (for Lambda bundle, kept in sync with pyproject.toml)
├── package.json            # Vestigial — only for serverless-python-requirements plugin
├── .env.example            # Environment variable template
└── Makefile                # Task runner (setup/test/lint/deploy/clean)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add endpoint | `src/routes/` + register in `src/main.py` | Thin controller, delegate to services |
| Add business logic | `src/services/` | DynamoDB access, cursor pagination |
| Add schema | `src/schemas/` | Pydantic v2 BaseModel, split by domain |
| Add exception | `src/core/exceptions.py` | Subclass BookAPIError, add handler in main.py |
| Add config | `src/config.py` | Pydantic BaseSettings, env vars |
| Add test | Mirror path in `tests/` | Use moto for AWS, not unittest.mock |
| Add middleware | `src/middleware/` | ASGI middleware, register in main.py |
| Add auth logic | `src/auth/token_store.py` | Token management, FastAPI dependency |
| Change deployment | `serverless.yml` | Lambda runtime, IAM, API Gateway, CORS |
| Change lint rules | `pyproject.toml` [tool.ruff] | E, F, I, UP, B, SIM enabled |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | FastAPI | `src/main.py:20` | App instance, CORS, routers, exception handlers |
| `handler` | Mangum | `src/main.py:116` | Lambda entry point |
| `Settings` | BaseSettings | `src/config.py` | ENVIRONMENT (auto-prefixes tables), DYNAMODB_ENDPOINT, AWS_REGION |
| `TableConfig` | BaseModel | `src/config.py` | Table base names, env-driven prefixing |
| `TokenStore` | class | `src/auth/token_store.py` | In-memory token store, hardcoded creds (admin/admin123) |
| `get_current_user` | FastAPI Depends | `src/auth/token_store.py` | Auth dependency, extracts Bearer token |
| `BookService` | class | `src/services/book_service.py` | DynamoDB CRUD, cursor pagination via base64 LEK |
| `get_dynamodb_resource` | function | `src/core/aws.py` | Factory for DynamoDB resource with endpoint handling |
| `BookAPIError` | Exception | `src/core/exceptions.py` | Base exception for all API errors |
| `BookNotFoundError` | Exception | `src/core/exceptions.py` | → 404 |
| `NotAuthenticatedError` | Exception | `src/core/exceptions.py` | → 401 |
| `InvalidCursorError` | Exception | `src/core/exceptions.py` | → 400 |
| `RateLimitExceededError` | Exception | `src/core/exceptions.py` | → 429 |
| `RateLimiter` | class | `src/middleware/rate_limiter.py` | Sliding window rate limiter, async-safe |
| `rate_limit_middleware` | function | `src/middleware/rate_limit.py` | ASGI middleware dispatch |

## CONVENTIONS
- **Python 3.14** — bleeding edge, released Oct 2025
- **uv** package manager — `uv sync --all-extras`, not pip/poetry
- **ruff** — single tool for lint + format + import sort, line-length 88 (not 79)
- **pytest** — module-level test functions, no Test* classes, no pytest-asyncio (use `asyncio.run()`)
- **moto** — AWS mocking via fixtures, never `unittest.mock`
- **Service layer** — LRU-cached singleton in routes (`@lru_cache`)
- **Cursor pagination** — base64-encoded DynamoDB LastEvaluatedKey
- **Table naming** — `ENVIRONMENT` env var auto-prefixes: `{env}-books`, `{env}-users`
- **Rate limiting** — sliding window, separate limits for login (5/min) and API (60/min)

## ANTI-PATTERNS (THIS PROJECT)
- Never use `unittest.mock` / `MagicMock` for AWS — use `moto` via `dynamodb_table` fixture
- Never add `pytest-asyncio` — async tests use `asyncio.run()` directly
- Never modify `requirements.txt` manually — it's generated from `pyproject.toml` for Lambda bundle
- Never set `DYNAMODB_ENDPOINT` in production `.env` — unset means real AWS endpoint
- Never add type error suppression (`# type: ignore`) — no mypy configured anyway
- Never put business logic in routes — delegate to services
- Never bypass `core/aws.py` factory — it handles endpoint URL logic for local vs cloud

## UNIQUE STYLES
- `package.json` `"main": "index.js"` is a dead reference — no JS entry exists, file only for serverless plugin
- Two static routes serve same file (`/` and `/static/index.html`) — intentional for both root and explicit access
- `deps/` directory at root — Lambda dependency bundle, gitignored, created by `make deps`
- Pre-commit hooks run ruff in 3 steps: lint --fix, import sort, format
- CORS explicitly allows `Authorization` header for SPA auth
- Exception hierarchy: `BookAPIError` base → specific subclasses → HTTP status mapping in `main.py`
- Rate limiter: async-safe via `asyncio.Lock`, max 10k keys, sliding window

## COMMANDS
```bash
make setup        # uv sync --all-extras + pre-commit install
make db           # docker compose up -d dynamodb-local
make db-init      # python scripts/init_db.py (create table)
make dev          # uv run fastapi dev src/main.py --port 9876
make test         # pytest -v (all tests)
make test-unit    # pytest tests/ -v --ignore=tests/integration
make test-integration  # pytest tests/integration -v
make coverage     # pytest --cov=src --cov-fail-under=90 -v
make lint         # ruff check .
make format       # ruff format .
make deploy       # make deps + serverless deploy (dev)
make deploy-prod  # make deps + serverless deploy --stage prod
make clean        # rm -rf deps/ .serverless/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/ __pycache__/
```

## NOTES
- DynamoDB Local runs in-memory — data wiped on container restart
- Default creds: admin / admin123 (coding challenge only)
- CORS allow_origins=["*"] — intentional for challenge, restrict in production
- Coverage gate: 90% minimum, currently at 99% (60 tests)
- No CI/CD pipeline — deployment is fully manual via `make deploy`
- Serverless Framework v4, region ap-southeast-1 (Singapore)
- Lambda layer bundles deps/ with PYTHONPATH=/var/task/deps, strips boto3/botocore (provided by runtime)
- SPA at `static/index.html` requires CORS `Authorization` header for browser auth
- Rate limits: login 5 req/min, API 60 req/min, non-API paths exempt

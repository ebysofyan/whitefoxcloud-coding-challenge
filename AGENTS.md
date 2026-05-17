# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-16 17:36 UTC
**Commit:** 1e82611
**Branch:** main

## OVERVIEW
FastAPI Python app for book CRUD, backed by DynamoDB. Dual runtime: local dev via `uv run fastapi dev`, prod via Serverless Framework → AWS Lambda (Mangum adapter).

## STRUCTURE
```
├── src/                    # Application package (src-layout)
│   ├── main.py            # FastAPI app + Mangum handler ← ENTRY POINT
│   ├── config.py          # Pydantic Settings (env-based)
│   ├── models.py          # Pydantic v2 request/response schemas
│   ├── exceptions.py      # Custom exception hierarchy
│   ├── auth.py            # Token store + FastAPI dependency
│   ├── routes/            # FastAPI APIRouter modules
│   └── services/          # Business logic + DynamoDB access
├── tests/                  # Mirrors src/ structure, 55 tests, 100% coverage
├── static/index.html       # SPA frontend (served at /)
├── scripts/init_db.py      # DynamoDB table bootstrap
├── serverless.yml          # AWS infra-as-code (Lambda + API Gateway + DynamoDB)
├── docker-compose.yml      # DynamoDB Local (port 18749, in-memory)
├── pyproject.toml          # Python deps + tool configs (uv, ruff, pytest)
├── requirements.txt        # Runtime deps (for Lambda bundle, kept in sync with pyproject.toml)
├── package.json            # Vestigial — only for serverless-python-requirements plugin
└── Makefile                # Task runner (setup/test/lint/deploy/clean)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add endpoint | `src/routes/` + register in `src/main.py` | Thin controller, delegate to services |
| Add business logic | `src/services/` | DynamoDB access, cursor pagination |
| Add schema | `src/models.py` | Pydantic v2 BaseModel |
| Add config | `src/config.py` | Pydantic BaseSettings, env vars |
| Add test | Mirror path in `tests/` | Use moto for AWS, not unittest.mock |
| Change deployment | `serverless.yml` | Lambda runtime, IAM, API Gateway |
| Change lint rules | `pyproject.toml` [tool.ruff] | E, F, I, UP, B, SIM enabled |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | FastAPI | `src/main.py:20` | App instance, CORS, routers, exception handlers |
| `handler` | Mangum | `src/main.py:116` | Lambda entry point |
| `Settings` | BaseSettings | `src/config.py` | ENVIRONMENT (auto-prefixes tables), DYNAMODB_ENDPOINT, AWS_REGION |
| `TokenStore` | class | `src/auth.py` | In-memory token store, hardcoded creds (admin/admin123) |
| `get_current_user` | FastAPI Depends | `src/auth.py` | Auth dependency, extracts Bearer token |
| `BookService` | class | `src/services/book_service.py` | DynamoDB CRUD, cursor pagination via base64 LEK |
| `BookNotFoundError` | Exception | `src/exceptions.py` | → 404 |
| `NotAuthenticatedError` | Exception | `src/exceptions.py` | → 401 |
| `InvalidCursorError` | Exception | `src/exceptions.py` | → 400 |

## CONVENTIONS
- **Python 3.14** — bleeding edge, released Oct 2025
- **uv** package manager — `uv sync --all-extras`, not pip/poetry
- **ruff** — single tool for lint + format + import sort, line-length 88 (not 79)
- **pytest** — module-level test functions, no Test* classes, no pytest-asyncio (use `asyncio.run()`)
- **moto** — AWS mocking via fixtures, never `unittest.mock`
- **Service layer** — LRU-cached singleton in routes (`@lru_cache`)
- **Cursor pagination** — base64-encoded DynamoDB LastEvaluatedKey

## ANTI-PATTERNS (THIS PROJECT)
- Never use `unittest.mock` / `MagicMock` for AWS — use `moto` via `dynamodb_table` fixture
- Never add `pytest-asyncio` — async tests use `asyncio.run()` directly
- Never modify `requirements.txt` manually — it's generated from `pyproject.toml` for Lambda bundle
- Never set `DYNAMODB_ENDPOINT` in production `.env` — unset means real AWS endpoint
- Never add type error suppression (`# type: ignore`) — no mypy configured anyway

## UNIQUE STYLES
- `package.json` `"main": "index.js"` is a dead reference — no JS entry exists, file only for serverless plugin
- Two static routes serve same file (`/` and `/static/index.html`) — intentional for both root and explicit access
- `deps/` directory at root — Lambda dependency bundle, gitignored, created by `make deps`
- Pre-commit hooks run ruff in 3 steps: lint --fix, import sort, format

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
- Coverage gate: 90% minimum, currently at 100% (55 tests)
- No CI/CD pipeline — deployment is fully manual via `make deploy`
- Serverless Framework v4, region ap-southeast-1 (Singapore)
- Lambda layer bundles deps/ with PYTHONPATH=/var/task/deps, strips boto3/botocore (provided by runtime)

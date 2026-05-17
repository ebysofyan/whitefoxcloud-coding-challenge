# tests/ — Test Suite

**Score:** 21 (distinct test domain, 60 tests, 99% coverage)

## OVERVIEW
pytest test suite mirroring src/ structure — unit, route, service, and integration tests.

## STRUCTURE
```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures (client, aws_mock, dynamodb_table, auth_token)
├── test_auth.py          # TokenStore, authenticate, get_current_user (9 tests)
├── test_config.py        # Settings defaults + TableConfig + env isolation (4 tests)
├── test_exceptions.py    # Custom exception messages (5 tests)
├── test_main.py          # CORS, static serving, health, error handlers (6 tests)
├── test_models.py        # Pydantic model validation (4 tests)
├── test_routes/          # Route-level HTTP tests
│   ├── __init__.py
│   ├── test_auth.py      # Login endpoint tests (3 tests)
│   └── test_books.py     # Book CRUD via TestClient (14 tests)
├── test_services/        # Service-level unit tests
│   ├── __init__.py
│   └── test_book_service.py  # DynamoDB CRUD, cursor pagination, resource factory (14 tests)
└── integration/          # Full-flow integration tests
    ├── __init__.py
    └── test_books.py     # Login→create→get→unauthorized→not-found (1 test)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add route test | `test_routes/test_<resource>.py` | Use `client` fixture, `auth_token` for protected endpoints |
| Add service test | `test_services/test_<resource>.py` | Use `dynamodb_table` fixture (moto) |
| Add integration test | `integration/test_<resource>.py` | Full lifecycle, still uses moto (not real DynamoDB) |
| Add shared fixture | `conftest.py` | Available to all tests via pytest discovery |

## CONVENTIONS
- **pytest only** — no unittest, no Test* classes, module-level functions
- **moto** for AWS mocking — `dynamodb_table` fixture creates table in mock DynamoDB
- **monkeypatch** for config isolation — `_isolate_settings` autouse fixture
- **async tests** via `asyncio.run()` — no pytest-asyncio
- **Naming**: `test_<description>()` — descriptive function names
- **Coverage gate**: 90% minimum (`make coverage`)
- **No parametrize** — each test case is its own function

## FIXTURES (conftest.py)
| Fixture | Purpose |
|---------|---------|
| `_isolate_settings` | autouse — stops real DynamoDB endpoint, injects dummy AWS creds, clears service cache |
| `client` | `TestClient(app)` for HTTP testing |
| `aws_mock` | `moto.mock_aws()` context manager |
| `dynamodb_table` | Creates DynamoDB table via boto3 inside moto mock |
| `auth_token` | Pre-created admin token from `token_store.create_token("admin")` |

## ANTI-PATTERNS
- Never use `unittest.mock` / `MagicMock` for AWS — use `moto`
- Never add `pytest-asyncio` — use `asyncio.run()` directly
- Never redefine `client` fixture locally (inconsistency in `test_routes/test_auth.py`)
- Integration tests still use moto — not real AWS DynamoDB
- Service tests use their own `mock_aws()` fixture, not conftest's `dynamodb_table`

# src/ — Application Core

**Score:** 23 (app core, module boundary, distinct domain)

## OVERVIEW
FastAPI application package — entry point, config, schemas, auth, routes, services.

## STRUCTURE
```
src/
├── __init__.py           # Package marker
├── main.py               # FastAPI app, CORS, routers, exception handlers, Mangum handler
├── config.py             # Pydantic Settings (DYNAMODB_ENDPOINT, BOOKS_TABLE_NAME, AWS_REGION, ENVIRONMENT)
├── models.py             # Pydantic v2 request/response schemas (LoginRequest, BookCreate, BookResponse, pagination)
├── exceptions.py         # Custom exception hierarchy (BookNotFoundError, NotAuthenticatedError, InvalidCursorError)
├── auth.py               # TokenStore (in-memory), get_current_user FastAPI dependency
├── routes/               # APIRouter modules (see routes/AGENTS.md)
│   ├── __init__.py
│   ├── auth.py           # POST /api/auth/login
│   └── books.py          # CRUD /api/books
└── services/             # Business logic + DynamoDB access
    ├── __init__.py       # Empty package marker
    └── book_service.py   # BookService class, DynamoDB CRUD, cursor pagination
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Add router | `routes/<resource>.py` | Create APIRouter, register in `main.py` |
| Add service | `services/<resource>_service.py` | LRU-cached singleton in routes |
| Add exception | `exceptions.py` | Subclass BookAPIError, add handler in `main.py` |
| Add schema | `models.py` | Pydantic v2 BaseModel |
| Add config | `config.py` | Pydantic BaseSettings, add to Settings class |
| Change Lambda handler | `main.py:handler` | Mangum(app) wraps FastAPI |

## CONVENTIONS
- **Service layer**: LRU-cached singleton in routes (`@lru_cache`)
- **Exception hierarchy**: `BookAPIError` base → specific subclasses → HTTP status mapping in `main.py`
- **Auth**: `get_current_user` FastAPI dependency, extracts Bearer token, validates against TokenStore
- **Config**: Pydantic BaseSettings reads from env vars + `.env` file

## ANTI-PATTERNS
- `auth.py` lives at src root (not in `auth/` subpackage) — acceptable for small project size
- `__init__.py` in `services/` is empty — add docstring if extending

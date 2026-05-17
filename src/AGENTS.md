# src/ — Application Core

**Score:** 23 (app core, module boundary, distinct domain)

## OVERVIEW
FastAPI application package — entry point, config, schemas, auth, routes, services.

## STRUCTURE
```
src/
├── __init__.py           # Package marker
├── main.py               # FastAPI app, CORS, routers, exception handlers, Mangum handler
├── config.py             # Pydantic Settings (ENVIRONMENT auto-prefixes tables, DYNAMODB_ENDPOINT, AWS_REGION)
├── core/                 # Cross-cutting infrastructure
│   ├── __init__.py
│   ├── exceptions.py     # Custom exception hierarchy (BookNotFoundError, NotAuthenticatedError, InvalidCursorError)
│   └── aws.py            # DynamoDB resource factory (endpoint handling)
├── auth/                 # Authentication package
│   ├── __init__.py
│   └── token_store.py    # TokenStore (in-memory), get_current_user FastAPI dependency, authenticate
├── schemas/              # Pydantic v2 request/response schemas
│   ├── __init__.py       # Re-exports all schemas
│   ├── auth.py           # LoginRequest, LoginResponse
│   └── books.py          # BookCreate, BookResponse, BookListResponse
├── middleware/           # ASGI middleware
│   ├── __init__.py
│   ├── rate_limit.py     # Rate limit middleware (dispatch function)
│   └── rate_limiter.py   # RateLimiter class (sliding window)
├── routes/               # APIRouter modules (see routes/AGENTS.md)
│   ├── __init__.py
│   ├── auth.py           # POST /api/auth/login
│   └── books.py          # CRUD /api/books
└── services/             # Business logic + DynamoDB access (see services/AGENTS.md)
    ├── __init__.py       # Empty package marker
    └── book_service.py   # BookService class, DynamoDB CRUD, cursor pagination
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Add router | `routes/<resource>.py` | Create APIRouter, register in `main.py` |
| Add service | `services/<resource>_service.py` | LRU-cached singleton in routes |
| Add exception | `core/exceptions.py` | Subclass BookAPIError, add handler in `main.py` |
| Add schema | `schemas/books.py` or `schemas/auth.py` | Pydantic v2 BaseModel, re-exported from `schemas/__init__.py` |
| Add config | `config.py` | Pydantic BaseSettings, add to Settings class |
| Add DynamoDB factory | `core/aws.py` | Resource factory with endpoint handling |
| Add auth logic | `auth/token_store.py` | Token management, FastAPI dependency |
| Add middleware | `middleware/<name>.py` | ASGI middleware, register in `main.py` |
| Change Lambda handler | `main.py:handler` | Mangum(app) wraps FastAPI |

## CONVENTIONS
- **Service layer**: LRU-cached singleton in routes (`@lru_cache`)
- **Exception hierarchy**: `BookAPIError` base → specific subclasses → HTTP status mapping in `main.py`
- **Auth**: `get_current_user` FastAPI dependency, extracts Bearer token, validates against TokenStore
- **Config**: Pydantic BaseSettings reads from env vars + `.env` file
- **DynamoDB**: Use `get_dynamodb_resource()` factory from `core.aws`, not direct `boto3.resource()`
- **Schemas**: Import from `src.schemas` (re-exports all); split new schemas by domain into `schemas/auth.py` or `schemas/books.py`

## ANTI-PATTERNS
- Never bypass `core/aws.py` factory — it handles endpoint URL logic for local vs cloud
- Never put schemas back at src root — always in `schemas/` package
- Never put auth logic back at src root — always in `auth/` package

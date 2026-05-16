# src/routes/ — HTTP Endpoints

**Score:** 10 (distinct HTTP layer domain)

## OVERVIEW
FastAPI APIRouter modules — thin controllers delegating to service layer.

## STRUCTURE
```
src/routes/
├── __init__.py
├── auth.py           # POST /api/auth/login → delegates to src.auth.TokenStore
└── books.py          # CRUD /api/books → delegates to src.services.BookService
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Add auth endpoint | `auth.py` | Login only, token generation via TokenStore |
| Add book endpoint | `books.py` | All CRUD operations, auth dependency injection |
| Add new resource | Create `<resource>.py` | Follow books.py pattern: APIRouter, Depends, service call |

## CONVENTIONS
- **Thin controllers**: Routes extract request data, call service, return response
- **Auth dependency**: `Depends(get_current_user)` on protected endpoints
- **Service injection**: `BookService()` via `@lru_cache` singleton pattern
- **Response codes**: 201 for create, 200 for read/list, 204 for delete
- **Cursor pagination**: base64-encoded DynamoDB LastEvaluatedKey in list endpoint

## ANTI-PATTERNS
- Never put business logic in routes — delegate to services
- Never use `unittest.mock` for DynamoDB in tests — use `moto`
- Never add `pytest-asyncio` — use `asyncio.run()` for async test helpers

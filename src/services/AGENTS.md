# src/services/ — Business Logic

**Score:** 8 (distinct domain, DynamoDB access layer)

## OVERVIEW
Business logic + DynamoDB access — CRUD operations, cursor pagination.

## STRUCTURE
```
src/services/
├── __init__.py       # Empty package marker
└── book_service.py   # BookService class (DynamoDB CRUD, cursor pagination)
```

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `BookService` | class | `book_service.py:34` | DynamoDB CRUD, cursor pagination |
| `_encode_cursor` | function | `book_service.py:12` | Base64-encode DynamoDB LastEvaluatedKey |
| `_decode_cursor` | function | `book_service.py:20` | Decode client cursor → ExclusiveStartKey |

## CONVENTIONS
- **DynamoDB resource**: Injected via constructor, defaults to `get_dynamodb_resource()`
- **Table name**: `settings.books_table_name` (auto-prefixed by ENVIRONMENT)
- **Pagination**: base64-encoded LEK, one-step prev cursor (echo incoming)
- **Total count**: `table.item_count` (eventually consistent, from table metadata)
- **Error handling**: Raises `BookNotFoundError` / `InvalidCursorError` from `src.exceptions`

## ANTI-PATTERNS
- Never use `boto3.resource()` directly — use `get_dynamodb_resource()` from `src/aws.py`
- Never inline DynamoDB logic in routes — keep in service layer
- Never use `unittest.mock` for DynamoDB in tests — use `moto` via `dynamodb_table` fixture

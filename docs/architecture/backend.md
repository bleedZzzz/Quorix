# Quorix — Backend Architecture

## Stack

- **Python 3.12+**
- **FastAPI** — async HTTP/SSE API with OpenAPI docs
- **Pydantic v2** — schema validation
- **SQLAlchemy 2.x** — async ORM
- **asyncpg** — PostgreSQL driver
- **Alembic** — database migrations
- **PostgreSQL 16** — system of record
- **Qdrant** — vector database
- **Redis** — cache, job queue, transient state
- **LangGraph** — agent orchestration
- **PyMuPDF (fitz)** — PDF parsing
- **MinIO / S3** — object storage

---

## Layered Architecture

```
┌──────────────────────────────────────┐
│            API Layer                  │
│   FastAPI route handlers (thin)       │
│   Request/response validation         │
│   Authentication middleware           │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│        Application Layer              │
│   Services: business workflows        │
│   Commands: write operations          │
│   Queries: read operations            │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│          Domain Layer                 │
│   Domain models & value objects       │
│   Business rules & constraints        │
│   Domain events                       │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│       Infrastructure Layer            │
│   Database repositories               │
│   Qdrant client                       │
│   Object storage client               │
│   LLM/embedding/reranker providers    │
│   External API clients                │
│   Redis client                        │
└──────────────────────────────────────┘
```

---

## Backend Directory Structure

```
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory
│   ├── dependencies.py             # Dependency injection
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # Aggregated v1 router
│   │       ├── auth.py             # /auth endpoints
│   │       ├── workspaces.py       # /workspaces endpoints
│   │       ├── projects.py         # /projects endpoints
│   │       ├── papers.py           # /papers endpoints
│   │       ├── discovery.py        # /discovery endpoints
│   │       ├── ingestion.py        # /ingestion endpoints
│   │       ├── documents.py        # /documents endpoints
│   │       ├── chat.py             # /chat endpoints
│   │       ├── compare.py          # /compare endpoints
│   │       ├── graph.py            # /graph endpoints
│   │       ├── gaps.py             # /gaps endpoints
│   │       ├── reviews.py          # /reviews endpoints
│   │       ├── notes.py            # /notes endpoints
│   │       ├── search.py           # /search endpoints
│   │       ├── jobs.py             # /jobs endpoints
│   │       ├── models.py           # /models endpoints
│   │       └── health.py           # /health endpoint
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── workspace_service.py
│   │   │   ├── paper_service.py
│   │   │   ├── discovery_service.py
│   │   │   ├── ingestion_service.py
│   │   │   ├── document_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── research_service.py
│   │   │   ├── comparison_service.py
│   │   │   ├── graph_service.py
│   │   │   ├── gap_service.py
│   │   │   ├── review_service.py
│   │   │   ├── note_service.py
│   │   │   └── job_service.py
│   │   ├── commands/               # Write operation handlers
│   │   └── queries/                # Read operation handlers
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── papers/
│   │   │   ├── models.py           # Paper, Author, PaperSource
│   │   │   ├── repository.py       # Abstract repository interface
│   │   │   └── services.py         # Domain-level business rules
│   │   ├── research/
│   │   │   ├── models.py           # Conversation, Message
│   │   │   └── services.py
│   │   ├── evidence/
│   │   │   ├── models.py           # Claim, EvidenceSpan, Citation
│   │   │   └── services.py
│   │   ├── reviews/
│   │   │   ├── models.py           # LiteratureReview, Screening
│   │   │   └── services.py
│   │   └── graph/
│   │       ├── models.py           # GraphEntity, GraphRelation
│   │       └── services.py
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── engine.py           # Async engine setup
│   │   │   ├── session.py          # Session factory
│   │   │   ├── base.py             # Declarative base
│   │   │   └── models/             # SQLAlchemy table models
│   │   │       ├── user.py
│   │   │       ├── workspace.py
│   │   │       ├── paper.py
│   │   │       ├── document.py
│   │   │       ├── conversation.py
│   │   │       ├── evidence.py
│   │   │       ├── note.py
│   │   │       ├── review.py
│   │   │       ├── job.py
│   │   │       └── ...
│   │   ├── repositories/
│   │   │   ├── paper_repository.py
│   │   │   ├── workspace_repository.py
│   │   │   ├── conversation_repository.py
│   │   │   ├── evidence_repository.py
│   │   │   └── ...
│   │   ├── qdrant/
│   │   │   ├── client.py           # Qdrant connection manager
│   │   │   ├── collections.py      # Collection configuration
│   │   │   └── indexer.py          # Vector indexing operations
│   │   ├── storage/
│   │   │   ├── base.py             # Abstract object storage
│   │   │   ├── minio_storage.py    # MinIO implementation
│   │   │   └── s3_storage.py       # S3 implementation
│   │   ├── providers/
│   │   │   ├── llm/
│   │   │   │   ├── base.py         # LLMProvider interface
│   │   │   │   ├── openai_compat.py
│   │   │   │   ├── anthropic.py
│   │   │   │   ├── google.py
│   │   │   │   ├── groq.py
│   │   │   │   └── ollama.py
│   │   │   ├── embeddings/
│   │   │   │   ├── base.py         # EmbeddingProvider interface
│   │   │   │   └── ...
│   │   │   ├── rerankers/
│   │   │   │   ├── base.py         # RerankerProvider interface
│   │   │   │   └── ...
│   │   │   └── vision/
│   │   │       ├── base.py
│   │   │       └── ...
│   │   ├── search/
│   │   │   ├── base.py             # PaperSource interface
│   │   │   ├── arxiv.py
│   │   │   ├── openalex.py
│   │   │   ├── crossref.py
│   │   │   └── semantic_scholar.py
│   │   └── cache/
│   │       └── redis_client.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── workspace.py
│   │   ├── paper.py
│   │   ├── document.py
│   │   ├── conversation.py
│   │   ├── evidence.py
│   │   ├── job.py
│   │   └── common.py               # Pagination, errors, etc.
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Pydantic Settings
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication
│   │   ├── authorization.py        # Workspace authorization
│   │   ├── password.py             # Password hashing
│   │   └── tokens.py               # JWT token management
│   │
│   └── observability/
│       ├── __init__.py
│       ├── logging.py              # Structured JSON logging
│       └── middleware.py           # Request ID, timing
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── pyproject.toml
└── requirements.txt
```

---

## API Design

### Base Path

```
/api/v1
```

### Module Endpoints

| Module       | Path             | Purpose                        |
|-------------|------------------|--------------------------------|
| Health      | `/health`         | Health check                   |
| Auth        | `/auth`           | Login, register, logout, refresh |
| Workspaces  | `/workspaces`     | CRUD, members                  |
| Projects    | `/projects`       | Workspace projects             |
| Papers      | `/papers`         | CRUD, metadata, versions       |
| Discovery   | `/discovery`      | External paper search          |
| Ingestion   | `/ingestion`      | Import, ingest papers          |
| Documents   | `/documents`      | Pages, sections, chunks        |
| Chat        | `/chat`           | Conversations, messages, SSE   |
| Compare     | `/compare`        | Paper comparison               |
| Graph       | `/graph`          | Knowledge graph entities       |
| Gaps        | `/gaps`           | Research gap analysis          |
| Reviews     | `/reviews`        | Literature reviews             |
| Notes       | `/notes`          | Notes, annotations             |
| Search      | `/search`         | Full-text search               |
| Jobs        | `/jobs`           | Background job status          |
| Models      | `/models`         | Model configuration            |

### Response Contract

All API responses use consistent Pydantic schemas:

```python
class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: dict | None = None

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    request_id: str | None = None
```

---

## Authentication Architecture

### Strategy

- JWT-based authentication (access + refresh tokens)
- Password hashing with bcrypt
- HTTP-only cookies for token storage (or Authorization header)
- Session-based refresh token rotation
- Provider-independent design (OAuth-ready)

### Flow

```
Register → Hash password → Create user → Issue tokens
Login → Verify credentials → Issue tokens
Protected request → Extract token → Validate → Resolve user → Check workspace membership
```

### Middleware

```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract and validate the current user from the JWT token."""

async def get_workspace_member(
    workspace_id: UUID,
    user: User = Depends(get_current_user)
) -> WorkspaceMember:
    """Verify user has access to the requested workspace."""
```

---

## Configuration

Pydantic Settings with environment variable loading:

```python
class Settings(BaseSettings):
    # Application
    app_env: str = "development"
    app_name: str = "Quorix"
    log_level: str = "INFO"
    debug: bool = False

    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "quorix_chunks"

    # Object Storage
    storage_endpoint: str = "http://localhost:9000"
    storage_access_key: str
    storage_secret_key: str
    storage_bucket: str = "quorix"

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI Providers (optional)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # External Search
    tavily_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env")
```

---

## Observability

Every request includes:
- `request_id` (UUID, generated per request)
- `user_id` (from auth context)
- `workspace_id` (from route context)
- `operation` (endpoint name)

AI requests additionally log:
- `provider`, `model`, `task`
- `latency_ms`, `input_tokens`, `output_tokens`
- `estimated_cost`, `status`

All logging is structured JSON. No secrets or raw document content in logs.

---

## Error Handling

```python
class QuorixError(Exception):
    """Base application error."""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

class NotFoundError(QuorixError):
    status_code = 404
    error_code = "NOT_FOUND"

class AuthenticationError(QuorixError):
    status_code = 401
    error_code = "AUTHENTICATION_FAILED"

class AuthorizationError(QuorixError):
    status_code = 403
    error_code = "FORBIDDEN"

class ValidationError(QuorixError):
    status_code = 422
    error_code = "VALIDATION_ERROR"

class ConflictError(QuorixError):
    status_code = 409
    error_code = "CONFLICT"
```

Global exception handler converts these to consistent `ErrorResponse` objects with `request_id`.

---

## Security Controls

1. **Authentication** — JWT validation on all protected routes
2. **Authorization** — Workspace membership check
3. **Input validation** — Pydantic schemas on all request bodies
4. **File validation** — MIME type check, file size limits on uploads
5. **SSRF protection** — URL allowlist for external fetches
6. **Rate limiting** — Per-user, per-endpoint limits
7. **Output sanitization** — No raw error traces in production
8. **Secret management** — Environment variables, never committed

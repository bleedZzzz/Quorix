# Quorix — Architecture Overview

## System Identity

**Quorix** is an evidence-first agentic research workspace. It combines paper discovery, ingestion, reading, grounded RAG, multi-paper reasoning, citation verification, knowledge graphs, research-gap discovery, and literature-review workflows into a single platform.

**Core principle:** Evidence first. Intelligence second.

---

## High-Level System Diagram

```
                         ┌─────────────────────────────┐
                         │       Quorix Web (Next.js)   │
                         │  TypeScript + Tailwind CSS   │
                         │  Custom Design System        │
                         └──────────────┬──────────────┘
                                        │
                              HTTPS / SSE
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │     FastAPI Application      │
                         │  Python 3.12+ / Pydantic v2  │
                         └──────────────┬──────────────┘
                                        │
              ┌─────────────────────────┼──────────────────────────┐
              │                         │                          │
              ▼                         ▼                          ▼
     ┌────────────────┐       ┌──────────────────┐       ┌────────────────┐
     │ Research        │       │ Ingestion         │       │ Discovery       │
     │ Services        │       │ Pipeline          │       │ Services        │
     └───────┬────────┘       └────────┬─────────┘       └───────┬────────┘
             │                         │                          │
             ▼                         ▼                          ▼
     ┌───────────────┐        ┌────────────────┐        Academic API
     │ LangGraph      │        │ Redis Queue     │        connectors
     │ Agent Runtime  │        └───────┬────────┘        (arXiv, OpenAlex,
     └──────┬────────┘                 │                 Crossref, Semantic Scholar)
            │                          ▼
            │                ┌───────────────────┐
            │                │ Background         │
            │                │ Workers            │
            │                └────────┬──────────┘
            │                         │
            ├───────────────┐         ├── PDF parsing
            │               │         ├── chunking
            ▼               ▼         ├── embeddings
     ┌──────────────┐ ┌────────────┐  └── analysis
     │ Retrieval     │ │ AI          │
     │ Engine        │ │ Providers   │
     └──────┬───────┘ └────────────┘
            │
      ┌─────┴──────────────┐
      ▼                    ▼
┌──────────────┐     ┌──────────────┐
│ PostgreSQL    │     │ Qdrant        │
│ metadata,     │     │ vectors,      │
│ relations     │     │ retrieval     │
└──────┬───────┘     └──────────────┘
       ▼
┌──────────────────┐
│ Object Storage    │
│ (MinIO / S3)      │
│ PDFs & artifacts  │
└──────────────────┘
```

---

## Technology Stack

### Backend

| Layer                | Technology            | Purpose                                      |
|----------------------|-----------------------|----------------------------------------------|
| Language             | Python 3.12+          | AI, data processing, backend                 |
| API framework        | FastAPI               | Async HTTP API, SSE, OpenAPI                  |
| Validation           | Pydantic v2           | Request/response/domain schemas               |
| ORM                  | SQLAlchemy 2.x        | PostgreSQL access (async)                     |
| DB driver            | asyncpg               | Async PostgreSQL connectivity                 |
| Migrations           | Alembic               | Versioned schema migrations                   |
| Primary database     | PostgreSQL 16         | System of record                              |
| Vector database      | Qdrant                | Embeddings & semantic retrieval               |
| Cache/queue          | Redis                 | Job queue, caching, transient state           |
| Workers              | Python worker service  | Ingestion, analysis, embeddings               |
| Agent orchestration  | LangGraph             | Stateful conditional research workflows       |
| PDF parsing          | PyMuPDF               | Text/page extraction baseline                 |
| Object storage       | MinIO (dev) / S3      | PDFs and large artifacts                      |
| Logging              | Structured JSON       | Diagnostics and observability                 |
| Tests                | Pytest                | Unit/integration tests                        |

### Frontend

| Layer                | Technology                       |
|----------------------|----------------------------------|
| Framework            | Next.js (App Router) + TypeScript|
| Styling              | Tailwind CSS                     |
| Component system     | **Custom design system** (no shadcn/ui) |
| Design tokens        | CSS variables + Tailwind config  |
| Server-state         | TanStack Query                   |
| Forms                | React Hook Form + Zod            |
| Graph visualization  | React Flow                       |
| PDF reader           | React PDF-compatible solution    |
| E2E tests            | Playwright                       |

> **ADR-001:** shadcn/ui has been explicitly excluded. All UI components will be custom-built using Tailwind CSS, CSS variables, and accessible primitives. See `docs/decisions/001-no-shadcn.md`.

### Infrastructure (Local Dev)

Docker Compose services:
- `quorix-web` — Next.js frontend
- `quorix-api` — FastAPI backend
- `quorix-worker` — Background job processor
- `postgres` — PostgreSQL 16
- `qdrant` — Vector database
- `redis` — Cache and job queue
- `minio` — S3-compatible object storage

---

## Architectural Layers (Backend)

```
API Layer (FastAPI route handlers — thin)
    ↓
Application Layer (services, commands, queries)
    ↓
Domain Layer (papers, research, evidence, reviews, graph)
    ↓
Infrastructure Layer (database, qdrant, storage, providers, repositories)
```

Route handlers must remain thin. Business logic lives in the application/domain layer. All infrastructure concerns (database, Qdrant, object storage, LLM providers, external APIs) are behind interface abstractions.

---

## Core Architectural Principles

1. **Evidence provenance** — Every chunk, claim, and citation traces back to paper → page → passage
2. **Workspace isolation** — All resources scoped to workspace; enforced server-side
3. **Provider abstraction** — No LLM/embedding/reranker vendor locks into business logic
4. **Hybrid retrieval** — Dense + lexical + metadata filtering + reranking
5. **Explicit state machines** — LangGraph for agentic flows, not implicit chaining
6. **Background processing** — Long tasks via Redis queue + workers, never blocking HTTP
7. **Progressive disclosure** — UI reveals complexity contextually, not all at once
8. **Graceful degradation** — If a provider is down, keep indexed research usable

---

## Repository Structure

```
quorix/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── app/                # App Router pages
│   │   ├── components/         # React components
│   │   │   ├── ui/             # Design system primitives
│   │   │   ├── shell/          # App shell (sidebar, topbar, inspector)
│   │   │   ├── papers/         # Paper-related components
│   │   │   ├── reader/         # PDF reader
│   │   │   ├── chat/           # Research chat
│   │   │   ├── evidence/       # Evidence/citation components
│   │   │   ├── comparison/     # Paper comparison
│   │   │   ├── graph/          # Knowledge graph
│   │   │   ├── reviews/        # Literature reviews
│   │   │   └── notes/          # Notes/annotations
│   │   ├── lib/                # Utilities, API client, constants
│   │   ├── hooks/              # Custom React hooks
│   │   ├── styles/             # Global styles, design tokens
│   │   └── types/              # TypeScript type definitions
│   └── api/                    # FastAPI backend
│       ├── app/
│       │   ├── main.py
│       │   ├── api/v1/         # Route handlers
│       │   ├── application/    # Services, commands, queries
│       │   ├── domain/         # Domain models and logic
│       │   ├── infrastructure/ # DB, Qdrant, storage, providers
│       │   ├── schemas/        # Pydantic schemas
│       │   ├── config/         # Configuration
│       │   ├── security/       # Auth, authorization
│       │   └── observability/  # Logging, metrics
│       ├── tests/
│       └── alembic/            # Database migrations
├── workers/
│   ├── ingestion/              # Paper ingestion worker
│   ├── analysis/               # Deep analysis worker
│   └── common/                 # Shared worker utilities
├── packages/
│   ├── types/                  # Shared TypeScript types
│   └── config/                 # Shared configuration
├── infra/
│   ├── docker/                 # Dockerfiles
│   └── migrations/             # Migration scripts
├── docs/
│   ├── architecture/           # Architecture documentation
│   ├── decisions/              # Architecture Decision Records
│   └── api/                    # API documentation
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/                    # Playwright tests
├── docker-compose.yml
├── .env.example
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Build Order (Phases)

| Phase | Focus                                                    |
|-------|----------------------------------------------------------|
| 0     | Planning, architecture docs, contracts, design system    |
| 1     | Repository structure, Docker, PostgreSQL, Alembic, auth, workspaces, frontend shell |
| 2     | Paper discovery, imports, storage, ingestion, PDF reader  |
| 3     | Chunking, embeddings, Qdrant, lexical, hybrid retrieval, reranking |
| 4     | LangGraph workflow, routing, query rewriting, auditing, streaming |
| 5     | Claims, evidence spans, citation verification, source navigation |
| 6     | Deep paper analysis, comparison, knowledge graph, research gaps |
| 7     | Notes, annotations, literature reviews, exports, saved searches |
| 8     | Evaluation, caching, model routing, cost/latency tracking |
| 9     | Security hardening, reliability, deployment, documentation |

---

## Cross-References

- Frontend architecture: `docs/architecture/frontend.md`
- Backend architecture: `docs/architecture/backend.md`
- RAG architecture: `docs/architecture/rag.md`
- Database architecture: `docs/architecture/database.md`
- Background jobs: `docs/architecture/jobs.md`
- Decision records: `docs/decisions/`

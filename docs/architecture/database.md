# Quorix — Database Architecture

## Engine

**PostgreSQL 16** is the system of record for all structured data.
**Qdrant** stores vector embeddings (see RAG architecture).
**Redis** handles cache and job queues (see Jobs architecture).

Large binary artifacts (PDFs, generated files) are stored in **S3-compatible object storage** — never in PostgreSQL rows.

---

## ORM & Migrations

- **SQLAlchemy 2.x** with async support (asyncpg driver)
- **Alembic** for versioned schema migrations
- All models use UUID primary keys
- All models include `created_at` and `updated_at` timestamps
- Soft-delete via `deleted_at` where appropriate

---

## Entity Relationship Diagram

```
┌──────────┐       ┌──────────────────┐       ┌──────────────┐
│  users    │──────<│ workspace_members │>──────│  workspaces  │
└──────────┘       └──────────────────┘       └──────┬───────┘
                                                      │
                              ┌────────────────────────┤
                              │                        │
                        ┌─────▼──────┐          ┌──────▼───────┐
                        │  projects   │          │   papers      │
                        └────────────┘          └──────┬───────┘
                                                       │
                    ┌──────────────────────────────────┤
                    │               │                   │
              ┌─────▼──────┐ ┌─────▼──────┐    ┌──────▼────────┐
              │ paper_     │ │  authors    │    │  documents     │
              │ sources    │ └────────────┘    └──────┬────────┘
              └────────────┘                          │
                                          ┌───────────┼───────────┐
                                    ┌─────▼───┐ ┌─────▼────┐ ┌───▼──────────┐
                                    │ document│ │ document │ │ document     │
                                    │ _pages  │ │ _sections│ │ _chunks      │
                                    └─────────┘ └──────────┘ └──────────────┘

              ┌──────────────┐       ┌──────────────┐
              │conversations │───────│  messages     │
              └──────────────┘       └──────┬───────┘
                                            │
                                    ┌───────▼───────┐
                                    │    claims      │
                                    └───────┬───────┘
                                            │
                              ┌─────────────┼──────────────┐
                        ┌─────▼──────┐             ┌──────▼───────┐
                        │evidence    │             │  citations    │
                        │_spans      │             └──────────────┘
                        └────────────┘

              ┌──────────────┐      ┌──────────────┐
              │ annotations  │      │    notes      │
              └──────────────┘      └──────────────┘

              ┌──────────────┐      ┌──────────────┐
              │ literature   │──────│   review     │
              │ _reviews     │      │  _screening  │
              └──────────────┘      └──────────────┘

              ┌──────────────┐      ┌──────────────┐
              │    jobs      │──────│  job_events   │
              └──────────────┘      └──────────────┘
```

---

## Core Entity Definitions

### Users & Workspaces

```sql
-- users
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100),
    avatar_url      VARCHAR(500),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- workspaces
CREATE TABLE workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    owner_id        UUID NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- workspace_members
CREATE TABLE workspace_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role            VARCHAR(50) NOT NULL DEFAULT 'member',  -- owner, admin, member
    joined_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(workspace_id, user_id)
);

-- projects
CREATE TABLE projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Papers & Documents

```sql
-- papers
CREATE TABLE papers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    abstract        TEXT,
    year            INTEGER,
    venue           VARCHAR(300),
    doi             VARCHAR(200),
    arxiv_id        VARCHAR(50),
    pdf_url         VARCHAR(500),
    status          VARCHAR(50) NOT NULL DEFAULT 'imported',  
                    -- imported, ingesting, ready, failed
    paper_type      VARCHAR(50),  -- article, preprint, report, thesis, etc.
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_papers_workspace ON papers(workspace_id);
CREATE INDEX idx_papers_doi ON papers(doi) WHERE doi IS NOT NULL;
CREATE INDEX idx_papers_arxiv ON papers(arxiv_id) WHERE arxiv_id IS NOT NULL;

-- authors
CREATE TABLE authors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(300) NOT NULL,
    affiliation     VARCHAR(500),
    external_ids    JSONB DEFAULT '{}'
);

-- paper_authors (junction)
CREATE TABLE paper_authors (
    paper_id        UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    author_id       UUID NOT NULL REFERENCES authors(id),
    position        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (paper_id, author_id)
);

-- paper_sources (external identifiers)
CREATE TABLE paper_sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id        UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    source          VARCHAR(50) NOT NULL,  -- arxiv, openalex, crossref, semantic_scholar
    external_id     VARCHAR(200) NOT NULL,
    metadata        JSONB DEFAULT '{}',
    UNIQUE(paper_id, source)
);

-- documents (physical PDF files)
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id        UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    storage_key     VARCHAR(500) NOT NULL,  -- object storage path
    file_name       VARCHAR(300),
    file_size       BIGINT,
    mime_type       VARCHAR(100),
    checksum        VARCHAR(128),
    page_count      INTEGER,
    status          VARCHAR(50) NOT NULL DEFAULT 'uploaded',
                    -- uploaded, parsing, parsed, failed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- document_pages
CREATE TABLE document_pages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number     INTEGER NOT NULL,
    text_content    TEXT,
    width           FLOAT,
    height          FLOAT,
    UNIQUE(document_id, page_number)
);

-- document_sections
CREATE TABLE document_sections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title           VARCHAR(500),
    section_type    VARCHAR(100),  -- abstract, introduction, method, results, etc.
    start_page      INTEGER,
    end_page        INTEGER,
    level           INTEGER NOT NULL DEFAULT 1,
    parent_id       UUID REFERENCES document_sections(id),
    order_index     INTEGER NOT NULL DEFAULT 0
);

-- document_chunks
CREATE TABLE document_chunks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    paper_id        UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    section_id      UUID REFERENCES document_sections(id),
    page_number     INTEGER NOT NULL,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    token_count     INTEGER,
    start_offset    INTEGER,    -- character offset in page (where available)
    end_offset      INTEGER,
    embedding_id    VARCHAR(200),  -- Qdrant point ID
    text_hash       VARCHAR(128),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_chunks_paper ON document_chunks(paper_id);
CREATE INDEX idx_chunks_workspace ON document_chunks(workspace_id);
CREATE INDEX idx_chunks_document ON document_chunks(document_id);
```

### Conversations & Research

```sql
-- conversations
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(300),
    scope_type      VARCHAR(50),     -- workspace, project, paper, multi_paper
    scope_ids       UUID[] DEFAULT '{}',  -- paper_ids or project_id
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- messages
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL,  -- user, assistant, system
    content         TEXT NOT NULL,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- claims
CREATE TABLE claims (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id          UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    claim_text          TEXT NOT NULL,
    verification_state  VARCHAR(30) NOT NULL DEFAULT 'unverified',
                        -- verified, partial, unverified, missing
    confidence          FLOAT,
    order_index         INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- evidence_spans
CREATE TABLE evidence_spans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    chunk_id        UUID REFERENCES document_chunks(id),
    paper_id        UUID NOT NULL REFERENCES papers(id),
    document_id     UUID REFERENCES documents(id),
    page_number     INTEGER,
    section         VARCHAR(200),
    evidence_text   TEXT NOT NULL,
    relevance_grade VARCHAR(30),   -- HIGH_RELEVANCE, PARTIAL_RELEVANCE, IRRELEVANT
    retrieval_score FLOAT,
    reranker_score  FLOAT,
    grader_score    FLOAT,
    source_type     VARCHAR(30) NOT NULL DEFAULT 'paper',  -- paper, external
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- citations
CREATE TABLE citations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    evidence_id     UUID NOT NULL REFERENCES evidence_spans(id) ON DELETE CASCADE,
    paper_id        UUID NOT NULL REFERENCES papers(id),
    page_number     INTEGER,
    citation_text   VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Notes & Annotations

```sql
-- tags
CREATE TABLE tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    color           VARCHAR(20),
    UNIQUE(workspace_id, name)
);

-- annotations (highlights on documents)
CREATE TABLE annotations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id),
    page_number     INTEGER NOT NULL,
    highlight_text  TEXT,
    annotation_text TEXT,
    color           VARCHAR(20),
    position_data   JSONB,   -- coordinates for highlight rendering
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- notes
CREATE TABLE notes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(300),
    content         TEXT,
    paper_id        UUID REFERENCES papers(id),
    folder          VARCHAR(200),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- note_links (backlinks)
CREATE TABLE note_links (
    source_note_id  UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    target_note_id  UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    link_type       VARCHAR(50) DEFAULT 'reference',
    PRIMARY KEY (source_note_id, target_note_id)
);

-- paper_tags
CREATE TABLE paper_tags (
    paper_id        UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    tag_id          UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (paper_id, tag_id)
);
```

### Research Intelligence

```sql
-- paper_relationships
CREATE TABLE paper_relationships (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    source_paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    target_paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    relationship    VARCHAR(50) NOT NULL,
                    -- cites, cited_by, builds_on, extends, contradicts, supports, similar_to
    confidence      FLOAT,
    evidence_ids    UUID[] DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- research_gaps
CREATE TABLE research_gaps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    gap_description TEXT NOT NULL,
    gap_type        VARCHAR(100),
    confidence      FLOAT,
    why_detected    TEXT,
    potential_direction TEXT,
    supporting_paper_ids UUID[] DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- literature_reviews
CREATE TABLE literature_reviews (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id),
    title               VARCHAR(300) NOT NULL,
    research_question   TEXT,
    scope               TEXT,
    inclusion_criteria  TEXT,
    exclusion_criteria  TEXT,
    notes               TEXT,
    synthesis           TEXT,
    status              VARCHAR(50) NOT NULL DEFAULT 'draft',
                        -- draft, in_progress, completed
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- review_screening
CREATE TABLE review_screening (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id       UUID NOT NULL REFERENCES literature_reviews(id) ON DELETE CASCADE,
    paper_id        UUID NOT NULL REFERENCES papers(id),
    status          VARCHAR(50) NOT NULL DEFAULT 'candidate',
                    -- candidate, screening, included, excluded, needs_review
    reason          TEXT,
    screened_at     TIMESTAMPTZ,
    UNIQUE(review_id, paper_id)
);
```

### Jobs & System

```sql
-- jobs
CREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    job_type        VARCHAR(100) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'queued',
                    -- queued, running, completed, failed, retrying, cancelled
    payload         JSONB DEFAULT '{}',
    result          JSONB,
    error           TEXT,
    progress        FLOAT DEFAULT 0,
    retry_count     INTEGER DEFAULT 0,
    max_retries     INTEGER DEFAULT 3,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_jobs_workspace ON jobs(workspace_id);
CREATE INDEX idx_jobs_status ON jobs(status);

-- job_events
CREATE TABLE job_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    event_type      VARCHAR(100) NOT NULL,
    message         TEXT,
    data            JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- saved_searches
CREATE TABLE saved_searches (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id),
    name            VARCHAR(200) NOT NULL,
    query           TEXT NOT NULL,
    filters         JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- model_requests (observability)
CREATE TABLE model_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id),
    provider        VARCHAR(50) NOT NULL,
    model           VARCHAR(100) NOT NULL,
    task            VARCHAR(100) NOT NULL,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    latency_ms      INTEGER,
    estimated_cost  FLOAT,
    status          VARCHAR(30) NOT NULL,
    error           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## Key Constraints

1. **Workspace isolation** — Every query must filter by `workspace_id`
2. **Foreign key integrity** — Cascading deletes where appropriate
3. **UUID primary keys** — All entities use UUIDs
4. **Timestamps** — `created_at` and `updated_at` on all mutable entities
5. **Indexes** — On foreign keys, frequently filtered columns, and status fields
6. **No large blobs** — PDFs stored in object storage, referenced by `storage_key`

---

## Migration Strategy

- Alembic with auto-generation from SQLAlchemy models
- Migrations stored in `apps/api/alembic/versions/`
- Each migration is reversible where practical
- Naming convention: `YYYYMMDD_HHMM_description.py`

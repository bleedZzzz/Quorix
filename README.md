# Quorix — Evidence-First Agentic Research AI

> **Evidence first. Intelligence second.**

Quorix is an open-source AI research workspace that helps users discover, ingest, read, understand, compare, verify, connect, and synthesize academic and technical knowledge.

## Features

- **Paper Discovery** — Search arXiv, OpenAlex, Crossref, Semantic Scholar
- **PDF Reader** — Read, highlight, annotate, and navigate research papers
- **Grounded RAG** — Ask questions and receive evidence-backed answers
- **Citation Verification** — Every claim traces to paper → page → passage
- **Multi-Paper Comparison** — Compare methodologies, results, and findings
- **Knowledge Graph** — Explore relationships between papers, methods, and concepts
- **Research Gap Analysis** — Identify underexplored areas in your corpus
- **Literature Reviews** — Structured review workflows with screening and synthesis

## Tech Stack

### Backend
- Python 3.12+ / FastAPI / Pydantic v2
- PostgreSQL / SQLAlchemy / Alembic
- Qdrant (vector search) / Redis (cache & queues)
- LangGraph (agentic orchestration)
- PyMuPDF (PDF processing)
- MinIO / S3 (object storage)

### Frontend
- Next.js (App Router) / TypeScript
- Tailwind CSS / Custom design system
- TanStack Query / React Hook Form / Zod

### Infrastructure
- Docker Compose for local development
- Ollama support for local AI

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Node.js](https://nodejs.org/) 20+

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/quorix.git
cd quorix

# Copy environment file
cp .env.example .env

# Start infrastructure
docker compose up -d

# Backend
cd apps/api
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# Frontend
cd apps/web
npm install
npm run dev
```

## Architecture

See [docs/architecture/](docs/architecture/) for detailed architecture documentation.

## License

[Apache License 2.0](LICENSE)

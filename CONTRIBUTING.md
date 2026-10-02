# Contributing to Quorix

Thank you for your interest in contributing to Quorix!

## Development Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://docs.astral.sh/uv/) — Python package manager
- [Node.js](https://nodejs.org/) 20+
- Git

### Getting Started

1. **Clone the repository**

```bash
git clone https://github.com/your-org/quorix.git
cd quorix
```

2. **Copy environment configuration**

```bash
cp .env.example .env
```

3. **Start infrastructure services**

```bash
docker compose up -d
```

4. **Set up the backend**

```bash
cd apps/api
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

5. **Set up the frontend**

```bash
cd apps/web
npm install
npm run dev
```

## Architecture

See [docs/architecture/](docs/architecture/) for the full architecture documentation.

## Code Style

### Python (Backend)

- Use `ruff` for linting and formatting
- Type hints on all function signatures
- Async where IO-bound

### TypeScript (Frontend)

- ESLint + Prettier via Next.js defaults
- Strict TypeScript

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

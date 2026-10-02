# ADR-004: Use uv for Python Package Management

## Status

**Accepted**

## Date

2026-10-02

## Context

The Python ecosystem has multiple package management options: pip, pip-tools, Poetry, PDM, and uv. The project needs fast, reliable dependency resolution for both development and Docker builds.

## Decision

Use **uv** as the Python package manager and virtual environment tool.

## Rationale

- **Speed** — uv is 10–100× faster than pip for dependency resolution and installation
- **Lockfile** — `uv.lock` provides reproducible builds
- **Standards-compliant** — Works with `pyproject.toml` (PEP 621)
- **Drop-in replacement** — Compatible with pip's interface where needed
- **Docker-friendly** — Fast installs reduce Docker build times significantly
- **Single tool** — Replaces pip, pip-tools, virtualenv, and pipx

## Consequences

- All Python dependency management uses `uv` commands
- `pyproject.toml` is the single source of truth for dependencies
- `uv.lock` is committed to the repository
- Docker images use `uv` for installation
- Contributors need `uv` installed (or can fall back to `pip install -e .`)

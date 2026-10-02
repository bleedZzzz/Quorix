"""Quorix API — FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.settings import Settings, get_settings
from app.infrastructure.database.engine import create_engine
from app.infrastructure.database.session import create_session_factory
from app.observability.logging import setup_logging
from app.observability.middleware import RequestIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown."""
    settings: Settings = app.state.settings

    # Create database engine and session factory
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    app.state.engine = engine
    app.state.session_factory = session_factory

    yield

    # Shutdown
    await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if settings is None:
        settings = get_settings()

    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        description="Evidence-First Agentic Research AI",
        version="0.1.0",
        docs_url="/api/docs" if settings.is_development else None,
        redoc_url="/api/redoc" if settings.is_development else None,
        openapi_url="/api/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    app.state.settings = settings

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Dependency overrides ─────────────────────────────────────────────────
    # Override the AsyncSession dependency to use our session factory
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.infrastructure.database.session import get_session

    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async for session in get_session(app.state.session_factory):
            yield session

    app.dependency_overrides[AsyncSession] = _get_session

    # ── Error Monitoring & Exception Handlers ────────────────────────────────
    import structlog
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from starlette.exceptions import HTTPException as StarletteHTTPException

    logger = structlog.get_logger()

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc: StarletteHTTPException):
        request_id = getattr(request.state, "request_id", None)
        await logger.awarning(
            "http_error",
            status_code=exc.status_code,
            detail=str(exc.detail),
            request_id=request_id,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
                "detail": exc.detail,
                "request_id": request_id,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", None)
        errors = exc.errors()
        await logger.awarning(
            "validation_error",
            errors=errors,
            request_id=request_id,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": "Request validation failed",
                "detail": errors,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        await logger.aerror(
            "unhandled_server_error",
            error=str(exc),
            exc_info=True,
            request_id=request_id,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please contact support with the request_id.",
                "request_id": request_id,
            },
        )

    # ── Routes ───────────────────────────────────────────────────────────────
    app.include_router(api_router)

    return app


# Module-level app instance for uvicorn
app = create_app()

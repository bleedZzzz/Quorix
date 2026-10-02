"""v1 route aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.compare import router as compare_router
from app.api.v1.discovery import router as discovery_router
from app.api.v1.documents import router as documents_router
from app.api.v1.gaps import router as gaps_router
from app.api.v1.graph import router as graph_router
from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.notes import router as notes_router
from app.api.v1.papers import router as papers_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.workspaces import router as workspaces_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(workspaces_router)
api_router.include_router(papers_router)
api_router.include_router(documents_router)
api_router.include_router(ingestion_router)
api_router.include_router(discovery_router)
api_router.include_router(chat_router)
api_router.include_router(compare_router)
api_router.include_router(graph_router)
api_router.include_router(gaps_router)
api_router.include_router(reviews_router)
api_router.include_router(notes_router)
api_router.include_router(jobs_router)

"""Quorix API — Knowledge graph endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.application.services.graph_service import GraphService
from app.dependencies import get_graph_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.research import RelationshipCreateRequest, RelationshipResponse
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_model=ApiResponse[dict[str, Any]])
async def get_graph(
    workspace_id: uuid.UUID = Query(...),
    paper_id: uuid.UUID | None = Query(None),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: GraphService = Depends(get_graph_service),
) -> ApiResponse[dict[str, Any]]:
    """Get research knowledge graph (nodes and edges)."""
    graph_data = await service.get_graph(workspace_id=workspace_id, paper_id=paper_id)
    return ApiResponse(data=graph_data)


@router.post("/relationships", response_model=ApiResponse[RelationshipResponse], status_code=status.HTTP_201_CREATED)
async def create_relationship(
    request: RelationshipCreateRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: GraphService = Depends(get_graph_service),
) -> ApiResponse[RelationshipResponse]:
    """Add a relationship edge between papers."""
    rel = await service.create_relationship(
        workspace_id=workspace_id,
        source_paper_id=request.source_paper_id,
        target_paper_id=request.target_paper_id,
        relationship_type=request.relationship_type,
        confidence=request.confidence,
        evidence_ids=request.evidence_ids,
    )
    return ApiResponse(data=RelationshipResponse.model_validate(rel))

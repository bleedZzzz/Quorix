"""Research gaps endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.application.services.gap_service import GapService
from app.dependencies import get_gap_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.research import GapResponse
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/gaps", tags=["gaps"])


class AnalyzeGapsRequest(BaseModel):
    paper_ids: list[uuid.UUID] = Field(default_factory=list)


@router.get("", response_model=ApiResponse[list[GapResponse]])
async def list_gaps(
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: GapService = Depends(get_gap_service),
) -> ApiResponse[list[GapResponse]]:
    """List detected research gaps in workspace."""
    gaps = await service.list_gaps(workspace_id)
    return ApiResponse(data=[GapResponse.model_validate(g) for g in gaps])


@router.post("/analyze", response_model=ApiResponse[list[GapResponse]])
async def analyze_gaps(
    request: AnalyzeGapsRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: GapService = Depends(get_gap_service),
) -> ApiResponse[list[GapResponse]]:
    """Analyze literature corpus and detect research gaps."""
    gaps = await service.analyze_gaps(workspace_id=workspace_id, paper_ids=request.paper_ids)
    return ApiResponse(data=[GapResponse.model_validate(g) for g in gaps])

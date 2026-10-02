"""Literature comparison endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.application.services.comparison_service import ComparisonService
from app.dependencies import get_comparison_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/compare", tags=["compare"])


class CompareRequest(BaseModel):
    paper_ids: list[uuid.UUID] = Field(min_length=2)
    dimensions: list[str] | None = None


@router.post("", response_model=ApiResponse[dict[str, Any]])
async def compare_papers(
    request: CompareRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ComparisonService = Depends(get_comparison_service),
) -> ApiResponse[dict[str, Any]]:
    """Synthesize comparative matrix across papers."""
    matrix = await service.compare_papers(
        workspace_id=workspace_id,
        paper_ids=request.paper_ids,
        dimensions=request.dimensions,
    )
    return ApiResponse(data=matrix)

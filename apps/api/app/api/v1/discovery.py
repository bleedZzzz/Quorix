"""Discovery endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.application.services.discovery_service import DiscoveryService
from app.dependencies import get_discovery_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job import DiscoverySearchResponse
from app.security.auth import get_current_user

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get("/search", response_model=ApiResponse[DiscoverySearchResponse])
async def search_literature(
    query: str = Query(..., min_length=2),
    max_results: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    service: DiscoveryService = Depends(get_discovery_service),
) -> ApiResponse[DiscoverySearchResponse]:
    """Search external literature repositories (arXiv, open indexes)."""
    results = await service.search(query=query, max_results=max_results)
    return ApiResponse(
        data=DiscoverySearchResponse(
            results=results,
            query=query,
            total=len(results),
        )
    )

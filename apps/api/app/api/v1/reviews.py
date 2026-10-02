"""Literature review and screening endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.application.services.review_service import ReviewService
from app.dependencies import get_review_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.research import ReviewCreateRequest, ReviewResponse, ScreeningResponse
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/reviews", tags=["reviews"])


class AddScreeningCandidateRequest(BaseModel):
    paper_id: uuid.UUID
    status: str = "candidate"
    reason: str | None = None


class UpdateScreeningStatusRequest(BaseModel):
    status: str  # candidate, screening, included, excluded, needs_review
    reason: str | None = None


@router.post("", response_model=ApiResponse[ReviewResponse], status_code=status.HTTP_201_CREATED)
async def create_review(
    request: ReviewCreateRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ReviewService = Depends(get_review_service),
) -> ApiResponse[ReviewResponse]:
    """Create a new systematic literature review protocol."""
    review = await service.create_review(
        workspace_id=workspace_id,
        user_id=current_user.id,
        title=request.title,
        research_question=request.research_question,
        scope=request.scope,
        inclusion_criteria=request.inclusion_criteria,
        exclusion_criteria=request.exclusion_criteria,
    )
    return ApiResponse(data=ReviewResponse.model_validate(review))


@router.get("", response_model=ApiResponse[list[ReviewResponse]])
async def list_reviews(
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ReviewService = Depends(get_review_service),
) -> ApiResponse[list[ReviewResponse]]:
    """List literature reviews in workspace."""
    reviews = await service.list_reviews(workspace_id)
    return ApiResponse(data=[ReviewResponse.model_validate(r) for r in reviews])


@router.get("/{review_id}", response_model=ApiResponse[ReviewResponse])
async def get_review(
    review_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ReviewService = Depends(get_review_service),
) -> ApiResponse[ReviewResponse]:
    """Get review details and screening list."""
    review = await service.get_review(review_id, workspace_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return ApiResponse(data=ReviewResponse.model_validate(review))


@router.post("/{review_id}/screenings", response_model=ApiResponse[ScreeningResponse], status_code=status.HTTP_201_CREATED)
async def add_screening_candidate(
    review_id: uuid.UUID,
    request: AddScreeningCandidateRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ReviewService = Depends(get_review_service),
) -> ApiResponse[ScreeningResponse]:
    """Add a candidate paper to the review screening pool."""
    screening = await service.add_screening_candidate(
        review_id=review_id,
        paper_id=request.paper_id,
        status=request.status,
        reason=request.reason,
    )
    return ApiResponse(data=ScreeningResponse.model_validate(screening))


@router.put("/{review_id}/screenings/{paper_id}", response_model=ApiResponse[ScreeningResponse])
async def update_screening_status(
    review_id: uuid.UUID,
    paper_id: uuid.UUID,
    request: UpdateScreeningStatusRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ReviewService = Depends(get_review_service),
) -> ApiResponse[ScreeningResponse]:
    """Update paper screening decision (included, excluded, needs_review)."""
    screening = await service.update_screening(
        review_id=review_id,
        paper_id=paper_id,
        status=request.status,
        reason=request.reason,
    )
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening record not found")
    return ApiResponse(data=ScreeningResponse.model_validate(screening))

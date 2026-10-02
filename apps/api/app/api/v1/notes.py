"""Quorix API — Notes, annotations, and tags endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.note_service import NoteService
from app.dependencies import get_note_service
from app.infrastructure.database.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.notes import (
    AnnotationCreateRequest,
    AnnotationResponse,
    NoteCreateRequest,
    NoteResponse,
    NoteUpdateRequest,
    TagCreateRequest,
    TagResponse,
)
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/notes", tags=["notes"])


# Notes
@router.post("", response_model=ApiResponse[NoteResponse], status_code=status.HTTP_201_CREATED)
async def create_note(
    request: NoteCreateRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[NoteResponse]:
    """Create a research note."""
    note = await service.create_note(
        workspace_id=workspace_id,
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        paper_id=request.paper_id,
        folder=request.folder,
    )
    return ApiResponse(data=NoteResponse.model_validate(note))


@router.get("", response_model=ApiResponse[list[NoteResponse]])
async def list_notes(
    workspace_id: uuid.UUID = Query(...),
    paper_id: uuid.UUID | None = Query(None),
    folder: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[list[NoteResponse]]:
    """List notes in workspace."""
    notes = await service.list_notes(workspace_id=workspace_id, paper_id=paper_id, folder=folder)
    return ApiResponse(data=[NoteResponse.model_validate(n) for n in notes])


@router.get("/{note_id}", response_model=ApiResponse[NoteResponse])
async def get_note(
    note_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[NoteResponse]:
    """Get note by ID."""
    note = await service.get_note(note_id, workspace_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return ApiResponse(data=NoteResponse.model_validate(note))


@router.put("/{note_id}", response_model=ApiResponse[NoteResponse])
async def update_note(
    note_id: uuid.UUID,
    request: NoteUpdateRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[NoteResponse]:
    """Update note title, content, or folder."""
    note = await service.update_note(
        note_id=note_id,
        workspace_id=workspace_id,
        title=request.title,
        content=request.content,
        folder=request.folder,
    )
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return ApiResponse(data=NoteResponse.model_validate(note))


@router.delete("/{note_id}", response_model=ApiResponse[dict[str, bool]])
async def delete_note(
    note_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[dict[str, bool]]:
    """Delete a note."""
    deleted = await service.delete_note(note_id, workspace_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return ApiResponse(data={"deleted": True})


# Annotations
@router.post("/annotations", response_model=ApiResponse[AnnotationResponse], status_code=status.HTTP_201_CREATED)
async def create_annotation(
    request: AnnotationCreateRequest,
    current_user: User = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[AnnotationResponse]:
    """Create a highlight or annotation on a document page."""
    annotation = await service.create_annotation(
        document_id=request.document_id,
        user_id=current_user.id,
        page_number=request.page_number,
        highlight_text=request.highlight_text,
        annotation_text=request.annotation_text,
        color=request.color or "#facc15",
        position_data=request.position_data,
    )
    return ApiResponse(data=AnnotationResponse.model_validate(annotation))


@router.get("/annotations/document/{document_id}", response_model=ApiResponse[list[AnnotationResponse]])
async def list_annotations(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[list[AnnotationResponse]]:
    """List all annotations for a document."""
    annotations = await service.list_annotations(document_id)
    return ApiResponse(data=[AnnotationResponse.model_validate(a) for a in annotations])


# Tags
@router.post("/tags", response_model=ApiResponse[TagResponse], status_code=status.HTTP_201_CREATED)
async def create_tag(
    request: TagCreateRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[TagResponse]:
    """Create a workspace tag."""
    tag = await service.create_tag(workspace_id, request.name, request.color)
    return ApiResponse(data=TagResponse.model_validate(tag))


@router.get("/tags", response_model=ApiResponse[list[TagResponse]])
async def list_tags(
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: NoteService = Depends(get_note_service),
) -> ApiResponse[list[TagResponse]]:
    """List all workspace tags."""
    tags = await service.list_tags(workspace_id)
    return ApiResponse(data=[TagResponse.model_validate(t) for t in tags])

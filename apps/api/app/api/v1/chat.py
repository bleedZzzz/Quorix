"""Quorix API — Chat and research execution endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.application.services.chat_service import ChatService
from app.dependencies import get_chat_service
from app.infrastructure.database.models.user import User
from app.schemas.chat import (
    ChatMessageRequest,
    ConversationCreateRequest,
    ConversationResponse,
    MessageResponse,
)
from app.schemas.common import ApiResponse
from app.security.auth import get_current_user, get_workspace_member

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", response_model=ApiResponse[ConversationResponse], status_code=status.HTTP_201_CREATED)
async def create_conversation(
    workspace_id: uuid.UUID = Query(...),
    request: ConversationCreateRequest = ...,
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ChatService = Depends(get_chat_service),
) -> ApiResponse[ConversationResponse]:
    """Create a new research session."""
    conv = await service.create_conversation(
        workspace_id=workspace_id,
        user_id=current_user.id,
        title=request.title,
        scope_type=request.scope_type,
        scope_ids=request.scope_ids,
    )
    return ApiResponse(data=ConversationResponse.model_validate(conv))


@router.get("/conversations", response_model=ApiResponse[list[ConversationResponse]])
async def list_conversations(
    workspace_id: uuid.UUID = Query(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ChatService = Depends(get_chat_service),
) -> ApiResponse[list[ConversationResponse]]:
    """List research conversations in workspace."""
    convs = await service.list_conversations(
        workspace_id=workspace_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(data=[ConversationResponse.model_validate(c) for c in convs])


@router.get("/conversations/{conversation_id}", response_model=ApiResponse[ConversationResponse])
async def get_conversation(
    conversation_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ChatService = Depends(get_chat_service),
) -> ApiResponse[ConversationResponse]:
    """Get conversation and full message history with claims and citations."""
    conv = await service.get_conversation(conversation_id, workspace_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return ApiResponse(data=ConversationResponse.model_validate(conv))


@router.post("/conversations/{conversation_id}/messages", response_model=ApiResponse[MessageResponse])
async def send_message(
    conversation_id: uuid.UUID,
    request: ChatMessageRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ChatService = Depends(get_chat_service),
) -> ApiResponse[MessageResponse]:
    """Execute evidence-first research query and generate grounded answer with citations."""
    assistant_msg = await service.execute_query(
        conversation_id=conversation_id,
        workspace_id=workspace_id,
        query=request.content,
        paper_ids=request.paper_ids,
    )
    return ApiResponse(data=MessageResponse.model_validate(assistant_msg))


@router.post("/conversations/{conversation_id}/stream")
async def stream_message(
    conversation_id: uuid.UUID,
    request: ChatMessageRequest,
    workspace_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    _member=Depends(get_workspace_member),
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Stream research pipeline progress and token synthesis via Server-Sent Events (SSE)."""
    return StreamingResponse(
        service.stream_query_events(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            query=request.content,
            paper_ids=request.paper_ids,
        ),
        media_type="text/event-stream",
    )

"""Quorix API — Schemas package."""

from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.chat import (
    ChatMessageRequest,
    CitationResponse,
    ClaimResponse,
    ConversationCreateRequest,
    ConversationResponse,
    EvidenceSpanResponse,
    MessageResponse,
)
from app.schemas.common import ErrorDetail, ErrorResponse, HealthResponse, PaginatedResponse
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentPageResponse,
    DocumentResponse,
    DocumentSectionResponse,
)
from app.schemas.job import (
    DiscoverySearchResponse,
    DiscoverySearchResult,
    JobEventResponse,
    JobResponse,
)
from app.schemas.notes import (
    AnnotationCreateRequest,
    AnnotationResponse,
    NoteCreateRequest,
    NoteResponse,
    NoteUpdateRequest,
    TagCreateRequest,
    TagResponse,
)
from app.schemas.paper import (
    AuthorSchema,
    PaperAuthorResponse,
    PaperCreateRequest,
    PaperListResponse,
    PaperResponse,
    PaperSourceSchema,
    PaperUpdateRequest,
)
from app.schemas.research import (
    GapResponse,
    RelationshipCreateRequest,
    RelationshipResponse,
    ReviewCreateRequest,
    ReviewResponse,
    ScreeningResponse,
)
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "UserResponse",
    "WorkspaceCreateRequest",
    "WorkspaceUpdateRequest",
    "WorkspaceResponse",
    "WorkspaceMemberResponse",
    "AuthorSchema",
    "PaperAuthorResponse",
    "PaperSourceSchema",
    "PaperCreateRequest",
    "PaperUpdateRequest",
    "PaperResponse",
    "PaperListResponse",
    "DocumentResponse",
    "DocumentPageResponse",
    "DocumentSectionResponse",
    "DocumentChunkResponse",
    "ConversationCreateRequest",
    "ConversationResponse",
    "MessageResponse",
    "ChatMessageRequest",
    "ClaimResponse",
    "EvidenceSpanResponse",
    "CitationResponse",
    "TagCreateRequest",
    "TagResponse",
    "NoteCreateRequest",
    "NoteUpdateRequest",
    "NoteResponse",
    "AnnotationCreateRequest",
    "AnnotationResponse",
    "RelationshipCreateRequest",
    "RelationshipResponse",
    "GapResponse",
    "ReviewCreateRequest",
    "ReviewResponse",
    "ScreeningResponse",
    "JobResponse",
    "JobEventResponse",
    "DiscoverySearchResult",
    "DiscoverySearchResponse",
]

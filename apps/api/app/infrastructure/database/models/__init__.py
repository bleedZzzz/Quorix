"""Quorix API — Database models package."""

from app.infrastructure.database.models.conversation import Conversation, Message
from app.infrastructure.database.models.document import (
    Document,
    DocumentChunk,
    DocumentPage,
    DocumentSection,
)
from app.infrastructure.database.models.evidence import Citation, Claim, EvidenceSpan
from app.infrastructure.database.models.job import Job, JobEvent, ModelRequest, SavedSearch
from app.infrastructure.database.models.notes import Annotation, Note, NoteLink, PaperTag, Tag
from app.infrastructure.database.models.paper import Author, Paper, PaperAuthor, PaperSource
from app.infrastructure.database.models.research import (
    LiteratureReview,
    PaperRelationship,
    ResearchGap,
    ReviewScreening,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.workspace import Project, Workspace, WorkspaceMember

__all__ = [
    "User",
    "Workspace",
    "WorkspaceMember",
    "Project",
    "Paper",
    "Author",
    "PaperAuthor",
    "PaperSource",
    "Document",
    "DocumentPage",
    "DocumentSection",
    "DocumentChunk",
    "Conversation",
    "Message",
    "Claim",
    "EvidenceSpan",
    "Citation",
    "Tag",
    "PaperTag",
    "Annotation",
    "Note",
    "NoteLink",
    "PaperRelationship",
    "ResearchGap",
    "LiteratureReview",
    "ReviewScreening",
    "Job",
    "JobEvent",
    "SavedSearch",
    "ModelRequest",
]

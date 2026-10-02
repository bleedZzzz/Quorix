"""Quorix API — Dependency injection factories."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.chat_service import ChatService
from app.application.services.comparison_service import ComparisonService
from app.application.services.discovery_service import DiscoveryService
from app.application.services.document_service import DocumentService
from app.application.services.gap_service import GapService
from app.application.services.graph_service import GraphService
from app.application.services.ingestion_service import IngestionService
from app.application.services.job_service import JobService
from app.application.services.note_service import NoteService
from app.application.services.paper_service import PaperService
from app.application.services.review_service import ReviewService
from app.infrastructure.providers.embeddings import EmbeddingProvider, get_embedding_provider
from app.infrastructure.providers.llm import LLMProvider, get_llm_provider
from app.infrastructure.providers.reranker import RerankerProvider, get_reranker_provider
from app.infrastructure.qdrant.client import QdrantManager
from app.infrastructure.repositories.conversation_repository import ConversationRepository
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.evidence_repository import EvidenceRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.notes_repository import NotesRepository
from app.infrastructure.repositories.paper_repository import PaperRepository
from app.infrastructure.repositories.research_repository import ResearchRepository
from app.infrastructure.retrieval.dense import DenseRetriever
from app.infrastructure.retrieval.hybrid import HybridRetriever
from app.infrastructure.retrieval.lexical import LexicalRetriever
from app.infrastructure.storage.service import S3StorageService, StorageService

# Lazily initialized singletons
_storage: StorageService | None = None
_qdrant: QdrantManager | None = None
_llm: LLMProvider | None = None
_embedder: EmbeddingProvider | None = None
_reranker: RerankerProvider | None = None


def get_storage_service() -> StorageService:
    global _storage
    if _storage is None:
        _storage = S3StorageService()
    return _storage


def get_qdrant_manager() -> QdrantManager:
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantManager()
    return _qdrant


def get_llm() -> LLMProvider:
    global _llm
    if _llm is None:
        _llm = get_llm_provider()
    return _llm


def get_embedder() -> EmbeddingProvider:
    global _embedder
    if _embedder is None:
        _embedder = get_embedding_provider()
    return _embedder


def get_reranker() -> RerankerProvider:
    global _reranker
    if _reranker is None:
        _reranker = get_reranker_provider()
    return _reranker


def get_discovery_service() -> DiscoveryService:
    return DiscoveryService()


def get_paper_service(session: AsyncSession = Depends()) -> PaperService:
    return PaperService(paper_repo=PaperRepository(session))


def get_document_service(session: AsyncSession = Depends()) -> DocumentService:
    return DocumentService(
        doc_repo=DocumentRepository(session),
        storage_service=get_storage_service(),
    )


def get_ingestion_service(session: AsyncSession = Depends()) -> IngestionService:
    return IngestionService(
        paper_repo=PaperRepository(session),
        doc_repo=DocumentRepository(session),
        storage_service=get_storage_service(),
        qdrant_manager=get_qdrant_manager(),
        embedding_provider=get_embedder(),
    )


def get_chat_service(session: AsyncSession = Depends()) -> ChatService:
    doc_repo = DocumentRepository(session)
    qdrant = get_qdrant_manager()
    embedder = get_embedder()
    reranker = get_reranker()
    llm = get_llm()

    dense = DenseRetriever(qdrant=qdrant, embedding_provider=embedder, doc_repo=doc_repo)
    lexical = LexicalRetriever(document_repository=doc_repo)
    hybrid = HybridRetriever(dense_retriever=dense, lexical_retriever=lexical, reranker=reranker)

    return ChatService(
        conversation_repo=ConversationRepository(session),
        evidence_repo=EvidenceRepository(session),
        hybrid_retriever=hybrid,
        llm_provider=llm,
    )


def get_comparison_service(session: AsyncSession = Depends()) -> ComparisonService:
    return ComparisonService(paper_repo=PaperRepository(session), llm=get_llm())


def get_graph_service(session: AsyncSession = Depends()) -> GraphService:
    return GraphService(
        research_repo=ResearchRepository(session),
        paper_repo=PaperRepository(session),
    )


def get_gap_service(session: AsyncSession = Depends()) -> GapService:
    return GapService(
        research_repo=ResearchRepository(session),
        paper_repo=PaperRepository(session),
        llm=get_llm(),
    )


def get_review_service(session: AsyncSession = Depends()) -> ReviewService:
    return ReviewService(research_repo=ResearchRepository(session))


def get_note_service(session: AsyncSession = Depends()) -> NoteService:
    return NoteService(notes_repo=NotesRepository(session))


def get_job_service(session: AsyncSession = Depends()) -> JobService:
    return JobService(job_repo=JobRepository(session))

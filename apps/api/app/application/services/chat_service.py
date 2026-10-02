"""Quorix API — Chat and research execution service."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from app.application.research.graph import build_research_graph
from app.application.research.nodes import ResearchPipelineNodes
from app.application.research.state import ResearchState
from app.infrastructure.database.models.conversation import Conversation, Message
from app.infrastructure.providers.llm import LLMProvider, get_llm_provider
from app.infrastructure.repositories.conversation_repository import ConversationRepository
from app.infrastructure.repositories.evidence_repository import EvidenceRepository
from app.infrastructure.retrieval.hybrid import HybridRetriever


class ChatService:
    """Service handling multi-turn conversational research and grounded agent execution."""

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        evidence_repo: EvidenceRepository,
        hybrid_retriever: HybridRetriever,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.conv_repo = conversation_repo
        self.evidence_repo = evidence_repo
        self.llm = llm_provider or get_llm_provider()
        self.nodes = ResearchPipelineNodes(hybrid_retriever=hybrid_retriever, llm_provider=self.llm)
        self.graph = build_research_graph(self.nodes)

    async def create_conversation(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str = "New Research Session",
        scope_type: str = "workspace",
        scope_ids: list[uuid.UUID] | None = None,
    ) -> Conversation:
        return await self.conv_repo.create(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            scope_type=scope_type,
            scope_ids=scope_ids,
        )

    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> Conversation | None:
        return await self.conv_repo.get_by_id(conversation_id, workspace_id)

    async def list_conversations(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Conversation]:
        return await self.conv_repo.list_conversations(
            workspace_id=workspace_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    async def execute_query(
        self,
        conversation_id: uuid.UUID,
        workspace_id: uuid.UUID,
        query: str,
        paper_ids: list[uuid.UUID] | None = None,
    ) -> Message:
        """Run the full agentic graph pipeline synchronously and store response with claims and citations."""
        # Save user message
        await self.conv_repo.add_message(
            conversation_id=conversation_id,
            role="user",
            content=query,
        )

        initial_state: ResearchState = {
            "query": query,
            "conversation_id": str(conversation_id),
            "workspace_id": str(workspace_id),
            "paper_ids": [str(p) for p in paper_ids] if paper_ids else None,
            "research_events": [],
        }

        # Execute LangGraph state workflow
        final_state = await self.graph.ainvoke(initial_state)

        answer = final_state.get("final_answer") or "No definitive answer could be derived from the available evidence."
        diagnostics = final_state.get("diagnostics") or {}

        # Save assistant message
        assistant_msg = await self.conv_repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            metadata={
                "intent": final_state.get("intent"),
                "diagnostics": diagnostics,
                "events_count": len(final_state.get("research_events") or []),
            },
        )

        # Save claims and citations
        claims = final_state.get("claims") or []
        for idx, cl in enumerate(claims):
            claim_rec = await self.evidence_repo.create_claim(
                message_id=assistant_msg.id,
                claim_text=cl["claim_text"],
                verification_state=cl.get("verification_state", "verified"),
                confidence=cl.get("confidence", 1.0),
                order_index=idx,
            )

            # Link evidence span
            if cl.get("evidence_chunk_id") and cl.get("paper_id"):
                span_rec = await self.evidence_repo.add_evidence_span(
                    claim_id=claim_rec.id,
                    paper_id=uuid.UUID(str(cl["paper_id"])),
                    chunk_id=uuid.UUID(str(cl["evidence_chunk_id"])),
                    page_number=cl.get("page_number"),
                    evidence_text=cl["claim_text"],
                    relevance_grade="HIGH_RELEVANCE",
                )

                # Link citation
                await self.evidence_repo.add_citation(
                    claim_id=claim_rec.id,
                    evidence_id=span_rec.id,
                    paper_id=uuid.UUID(str(cl["paper_id"])),
                    page_number=cl.get("page_number"),
                    citation_text=f"[{idx + 1}] Paper {cl['paper_id']} (p. {cl.get('page_number')})",
                )

        # Refresh messages with relations
        msgs = await self.conv_repo.get_messages(conversation_id)
        return next((m for m in msgs if m.id == assistant_msg.id), assistant_msg)

    async def stream_query_events(
        self,
        conversation_id: uuid.UUID,
        workspace_id: uuid.UUID,
        query: str,
        paper_ids: list[uuid.UUID] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream SSE status updates and final token synthesis."""
        # Yield start event
        yield f"data: {json.dumps({'type': 'status', 'step': 'init', 'message': 'Starting research agent...'})}\n\n"

        assistant_msg = await self.execute_query(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            query=query,
            paper_ids=paper_ids,
        )

        # Stream the full response
        yield f"data: {json.dumps({'type': 'token', 'content': assistant_msg.content})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'message_id': str(assistant_msg.id)})}\n\n"

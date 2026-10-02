"""Quorix API — LangGraph Research Agent workflow builder."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.application.research.nodes import ResearchPipelineNodes
from app.application.research.state import ResearchState


def build_research_graph(nodes: ResearchPipelineNodes) -> Any:
    """Build and compile the evidence-first research StateGraph."""
    builder = StateGraph(ResearchState)  # type: ignore[arg-type]

    # Register nodes
    builder.add_node("conversation_context", nodes.conversation_context)
    builder.add_node("intent_classifier", nodes.intent_classifier)
    builder.add_node("query_analyzer", nodes.query_analyzer)
    builder.add_node("query_rewriter", nodes.query_rewriter)
    builder.add_node("paper_scope", nodes.paper_scope)
    builder.add_node("retrieval_router", nodes.retrieval_router)
    builder.add_node("hybrid_retrieval", nodes.hybrid_retrieval)
    builder.add_node("evidence_grader", nodes.evidence_grader)
    builder.add_node("knowledge_auditor", nodes.knowledge_auditor)
    builder.add_node("external_search", nodes.external_search)
    builder.add_node("claim_builder", nodes.claim_builder)
    builder.add_node("citation_verifier", nodes.citation_verifier)
    builder.add_node("response_generator", nodes.response_generator)
    builder.add_node("response_validator", nodes.response_validator)

    # Wire edges
    builder.add_edge(START, "conversation_context")
    builder.add_edge("conversation_context", "intent_classifier")
    builder.add_edge("intent_classifier", "query_analyzer")
    builder.add_edge("query_analyzer", "query_rewriter")
    builder.add_edge("query_rewriter", "paper_scope")
    builder.add_edge("paper_scope", "retrieval_router")
    builder.add_edge("retrieval_router", "hybrid_retrieval")
    builder.add_edge("hybrid_retrieval", "evidence_grader")
    builder.add_edge("evidence_grader", "knowledge_auditor")

    # Conditional routing after knowledge audit
    def audit_route(state: ResearchState) -> str:
        if state.get("evidence_sufficient", True):
            return "claim_builder"
        return "external_search"

    builder.add_conditional_edges(
        "knowledge_auditor",
        audit_route,
        {
            "claim_builder": "claim_builder",
            "external_search": "external_search",
        },
    )

    builder.add_edge("external_search", "claim_builder")
    builder.add_edge("claim_builder", "citation_verifier")
    builder.add_edge("citation_verifier", "response_generator")
    builder.add_edge("response_generator", "response_validator")
    builder.add_edge("response_validator", END)

    return builder.compile()


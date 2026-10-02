import uuid

import pytest

from app.application.research.graph import build_research_graph
from app.application.research.nodes import ResearchPipelineNodes
from app.application.research.state import ResearchState
from app.infrastructure.providers.llm import MockLLMProvider
from app.infrastructure.retrieval import RetrievalResult


class MockHybridRetriever:
    async def retrieve(self, query, scope, top_k=10, rerank=True):
        return [
            RetrievalResult(
                chunk_id=uuid.uuid4(),
                paper_id=uuid.uuid4(),
                document_id=uuid.uuid4(),
                page_number=1,
                content="The Transformer model relies entirely on multi-head self-attention mechanisms to compute representations of input and output.",
                score=0.92,
                retrieval_type="hybrid",
                section_title="Model Architecture",
                section_type="method",
            ),
            RetrievalResult(
                chunk_id=uuid.uuid4(),
                paper_id=uuid.uuid4(),
                document_id=uuid.uuid4(),
                page_number=2,
                content="Self-attention allows the model to connect all positions with a constant number of sequentially executed operations.",
                score=0.85,
                retrieval_type="hybrid",
                section_title="Attention",
                section_type="method",
            ),
        ]


@pytest.mark.asyncio
async def test_research_agent_graph():
    nodes = ResearchPipelineNodes(
        hybrid_retriever=MockHybridRetriever(),  # type: ignore
        llm_provider=MockLLMProvider(),
    )
    graph = build_research_graph(nodes)

    initial_state: ResearchState = {
        "query": "How does self-attention operate in transformer models?",
        "workspace_id": str(uuid.uuid4()),
        "research_events": [],
    }

    result = await graph.ainvoke(initial_state)

    assert result["intent"] == "factual"
    assert len(result["reranked_evidence"]) == 2
    assert len(result["claims"]) > 0
    assert len(result["citations"]) > 0
    assert result["final_answer"] is not None
    assert len(result["research_events"]) > 5

# Quorix — RAG Architecture

## Core Principle

> Evidence first. Intelligence second.

Quorix is NOT a simple PDF chatbot. The RAG pipeline is evidence-first and agentic, using an explicit state graph (LangGraph) rather than implicit prompt chaining.

---

## Agentic RAG Pipeline

```
User Query
    ↓
Conversation Context
    ↓
Intent Analysis
    ↓
Query Rewriting
    ↓
Paper / Workspace Scoping
    ↓
Retrieval Router
    ├───────────────┐
    ↓               ↓
Hybrid Search    Metadata
    └───────┬───────┘
            ↓
          Rerank
            ↓
       Evidence Grade
            ↓
      Knowledge Audit
        ├─────────────┐
        ↓             ↓
      enough       insufficient
        ↓             ↓
      claims      External Search
        │             ↓
        └────── merge ┘
                 ↓
          Claim Construction
                 ↓
        Citation Verification
                 ↓
          Response Generation
                 ↓
              Validation
                 ↓
               Answer
```

---

## LangGraph Nodes

| #  | Node                    | Purpose                                         | Model Policy |
|----|-------------------------|--------------------------------------------------|-------------|
| 1  | `conversation_context`  | Load conversation history, set context window   | None        |
| 2  | `intent_classifier`     | Classify query intent (factual, comparison, gap, etc.) | FAST   |
| 3  | `query_analyzer`        | Extract entities, constraints, scope            | FAST        |
| 4  | `query_rewriter`        | Rewrite query for retrieval optimization        | FAST        |
| 5  | `paper_scope`           | Determine which papers/workspace to search      | None        |
| 6  | `retrieval_router`      | Decide retrieval strategy based on intent       | None        |
| 7  | `dense_retrieval`       | Semantic vector search in Qdrant                | EMBEDDING   |
| 8  | `lexical_retrieval`     | BM25/full-text search in PostgreSQL             | None        |
| 9  | `hybrid_merge`          | Merge and deduplicate candidates (RRF)          | None        |
| 10 | `reranker`              | Cross-encoder reranking of candidates           | RERANKING   |
| 11 | `evidence_grader`       | Grade evidence relevance                        | FAST        |
| 12 | `knowledge_auditor`     | Assess evidence sufficiency                     | FAST        |
| 13 | `external_search`       | Search external sources if knowledge gap found  | None        |
| 14 | `claim_builder`         | Construct individual claims from evidence       | REASONING   |
| 15 | `citation_verifier`     | Verify each claim maps to real evidence         | FAST        |
| 16 | `response_generator`    | Generate the final grounded response            | REASONING   |
| 17 | `response_validator`    | Validate response coherence and completeness    | FAST        |

---

## LangGraph State

```python
class ResearchState(TypedDict):
    # Input
    query: str
    conversation_id: str | None
    conversation_context: list[dict] | None

    # Analysis
    intent: str | None               # factual, comparison, summary, gap, etc.
    rewritten_query: str | None
    query_entities: list[str]
    query_constraints: dict

    # Scope
    workspace_id: str
    project_id: str | None
    paper_ids: list[str] | None      # Specific papers to search

    # Retrieval
    dense_candidates: list[dict]
    lexical_candidates: list[dict]
    merged_candidates: list[dict]
    reranked_evidence: list[dict]

    # Grading
    graded_evidence: list[dict]      # With relevance grades
    evidence_sufficient: bool

    # External
    knowledge_gaps: list[dict]
    external_sources: list[dict]
    merged_evidence: list[dict]

    # Claims
    claims: list[dict]               # Structured claim objects
    citations: list[dict]            # Citation verification results

    # Output
    final_answer: str | None
    research_events: list[dict]      # Status events for streaming

    # Diagnostics
    diagnostics: dict                # Timing, scores, debug info
```

---

## Retrieval Architecture

### Hybrid Retrieval

Quorix uses hybrid retrieval — NEVER vector-only.

```
Query
  │
  ├── Dense Retrieval (Qdrant)
  │   └── Semantic similarity via embeddings
  │
  ├── Lexical Retrieval (PostgreSQL full-text / BM25)
  │   └── Exact term matching
  │
  └── Metadata Filtering
      └── workspace_id, paper_id, section, date, etc.
          ↓
     Candidate Merge (Reciprocal Rank Fusion)
          ↓
     Reranker (cross-encoder)
          ↓
     Top-N Evidence
```

### Retriever Interfaces

```python
class Retriever(ABC):
    """Base retriever interface."""
    async def retrieve(
        self,
        query: str,
        scope: RetrievalScope,
        filters: RetrievalFilters | None = None,
        top_k: int = 20,
    ) -> list[RetrievalResult]: ...

class DenseRetriever(Retriever):
    """Qdrant-based semantic search."""

class LexicalRetriever(Retriever):
    """PostgreSQL full-text search."""

class HybridRetriever(Retriever):
    """Combines dense + lexical with RRF merge."""

class ScopedRetriever(Retriever):
    """Applies workspace/paper/project scoping to retrieval."""

class Reranker(ABC):
    """Cross-encoder reranker."""
    async def rerank(
        self,
        query: str,
        candidates: list[RetrievalResult],
        top_n: int = 10,
    ) -> list[RetrievalResult]: ...
```

---

## Evidence Grading

Retrieved evidence is graded BEFORE answer generation:

```
HIGH_RELEVANCE    — directly answers the query
PARTIAL_RELEVANCE — related but incomplete
IRRELEVANT        — not useful for the query
```

Each graded evidence record stores:
- `retrieval_score` (from vector/lexical search)
- `reranker_score` (from cross-encoder)
- `grader_score` (from LLM grading)
- `source_paper_id`, `page_number`, `section`
- `evidence_text` (the actual passage)

---

## Knowledge Auditing

After grading, the knowledge auditor determines if the evidence is sufficient:

```
Sufficient evidence → proceed to claim construction
Insufficient evidence → identify gaps → optional external search → merge → re-verify
```

If external search is triggered:
- External evidence is clearly tagged as `source_type: "external"`
- External evidence NEVER replaces or is confused with paper corpus evidence
- UI clearly distinguishes paper-sourced vs. externally-sourced evidence

---

## Claim-Level Citations

This is a core differentiator for Quorix.

```
Claim
  ↓
Evidence span (exact passage from paper)
  ↓
Paper (metadata)
  ↓
Page + Section
```

### Claim Object

```python
class Claim(BaseModel):
    claim_id: str
    claim_text: str
    evidence_ids: list[str]
    verification_state: Literal["verified", "partial", "unverified", "missing"]
    
    confidence: float  # 0.0 - 1.0
```

### Citation Verification States

| State        | Meaning                                              |
|-------------|------------------------------------------------------|
| `verified`  | Claim is directly supported by cited evidence         |
| `partial`   | Claim is partially supported, some aspects unsupported|
| `unverified`| Claim exists but evidence link could not be confirmed |
| `missing`   | No evidence found to support the claim                |

**The LLM must NOT be the authority for bibliographic metadata.** Paper metadata comes from the database, not from generation.

---

## Model Provider Abstraction

```python
class LLMProvider(ABC):
    async def generate(self, messages: list[dict], **kwargs) -> LLMResponse: ...
    async def stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]: ...

class EmbeddingProvider(ABC):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

class RerankerProvider(ABC):
    async def rerank(self, query: str, documents: list[str]) -> list[float]: ...

class VisionProvider(ABC):
    async def analyze(self, image: bytes, prompt: str) -> str: ...
```

### Model Routing Policies

| Policy    | Use Case                                | Cost    |
|-----------|------------------------------------------|---------|
| FAST      | Classification, extraction, grading      | Low     |
| REASONING | Synthesis, comparison, gap analysis       | Higher  |
| EMBEDDING | Vector embedding generation              | Low     |
| RERANKING | Cross-encoder reranking                  | Medium  |
| VISION    | Figure/table analysis                    | Higher  |

Use FAST models where quality permits; reserve REASONING models for synthesis tasks.

---

## Streaming

Research chat uses SSE (Server-Sent Events) for real-time status and answer streaming.

### Event Types

```typescript
type StreamEvent =
  | { type: "status"; stage: string; message: string }
  | { type: "evidence"; evidence: Evidence[] }
  | { type: "token"; content: string }
  | { type: "citation"; claim: Claim }
  | { type: "complete"; message: Message }
  | { type: "error"; error: string }
```

### Visible Status Stages (user-facing)

```
Analyzing question
Searching papers
Retrieving evidence
Reranking sources
Checking evidence
Verifying citations
Generating answer
```

**Never expose private chain-of-thought or internal diagnostics to the user.**

---

## External Search

Uses a search-provider abstraction:

```python
class ExternalSearchProvider(ABC):
    async def search(self, query: str, max_results: int = 5) -> list[ExternalResult]: ...
```

Initial implementation: Tavily or similar compatible provider.

External evidence is:
- Clearly distinct from paper corpus evidence in the UI
- Tagged with `source_type: "external"` in all data structures
- Subject to the same evidence grading pipeline

---

## Qdrant Vector Architecture

### Collection Schema

```json
{
  "collection_name": "quorix_chunks",
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "workspace_id": "keyword",
    "paper_id": "keyword",
    "document_id": "keyword",
    "page_number": "integer",
    "section": "keyword",
    "subsection": "keyword",
    "chunk_id": "keyword",
    "text_hash": "keyword"
  }
}
```

Retrieval is always filtered by `workspace_id` at minimum. Additional filters for `paper_id`, `section`, and other metadata are applied based on the scoping step.

---

## Evaluation

Quorix tracks repeatable evaluation cases:

| Metric                 | What it measures                         |
|------------------------|------------------------------------------|
| Retrieval precision    | Relevant docs in retrieved set           |
| Retrieval recall       | Coverage of all relevant docs            |
| Context precision      | Relevant context in provided chunks      |
| Context recall         | Coverage of needed context               |
| Answer faithfulness    | Answer supported by provided evidence    |
| Citation correctness   | Claims correctly linked to sources       |
| Citation completeness  | All claims have supporting citations     |
| Latency                | End-to-end response time                 |
| Estimated cost         | Token usage → cost estimation            |

**Do not publish made-up scores.** Evaluation must use real test cases.

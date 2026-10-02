# ADR-003: Hybrid Retrieval Architecture

## Status

**Accepted**

## Date

2026-10-02

## Context

Simple vector-only RAG frequently misses exact terms, paper IDs, method names, and specific technical phrases that are critical in academic research. Pure lexical search misses semantic similarity.

## Decision

Use **hybrid retrieval** combining:
1. **Dense retrieval** (Qdrant vector similarity)
2. **Lexical retrieval** (PostgreSQL full-text search / BM25)
3. **Metadata filtering** (workspace, paper, section scoping)
4. **Reciprocal Rank Fusion** (RRF) for candidate merging
5. **Cross-encoder reranking** (provider-abstracted)

## Rationale

- Academic queries often contain exact terms ("Transformer", "ImageNet", "BLEU score") that lexical search handles better
- Semantic search captures paraphrases and conceptual similarity
- RRF is a simple, effective merge strategy that doesn't require learned weights
- Reranking significantly improves top-N precision at moderate cost
- Metadata filtering ensures workspace isolation and allows paper-scoped queries

## Consequences

- More retrieval infrastructure to build and maintain
- PostgreSQL full-text search must be configured with appropriate indexes
- Reranking adds latency (mitigated by selective reranking only when needed)
- Evaluation must measure both retrieval precision and recall to validate the hybrid approach

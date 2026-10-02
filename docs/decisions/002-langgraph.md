# ADR-002: LangGraph for Agent Orchestration

## Status

**Accepted**

## Date

2026-10-02

## Context

Quorix's RAG pipeline is agentic — it requires conditional routing, evidence auditing, external search fallback, and citation verification as distinct steps in a stateful graph.

Options considered:
1. **Implicit prompt chaining** — Simple but opaque, hard to debug, no conditional routing
2. **LangChain LCEL** — Expression-based, works but limited graph control
3. **LangGraph** — Explicit state graph with conditional edges, checkpointing, debugging
4. **Custom state machine** — Full control but significant implementation effort

## Decision

Use **LangGraph** for the agentic research workflow.

## Rationale

- **Explicit state** — `ResearchState` is a typed, serializable dict. Every node reads and writes known fields.
- **Conditional routing** — Knowledge auditor decides whether to proceed to claims or trigger external search. LangGraph's conditional edges express this naturally.
- **Debuggability** — Each node can be tested independently. The graph execution trace shows exactly what happened.
- **Streaming** — LangGraph supports node-level streaming events, which map directly to Quorix's research status events.
- **Provider independence** — LangGraph is orchestration infrastructure, not an LLM provider. Provider switching remains a separate concern.

## Consequences

- LangGraph is a dependency in the backend
- Team must understand LangGraph's graph definition and state management patterns
- Graph complexity should be managed — start with the core pipeline, add nodes incrementally

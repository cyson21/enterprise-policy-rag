# Project 02 Foundation Plan

작성일: 2026-05-20

## Goal

Build the foundation for `Enterprise Policy RAG`, a portfolio-grade AI-native backend project focused on permission-aware RAG, citation, eval, latency, and cost tracking.

This plan prepares the repository for a separate implementation agent. It does not implement application code yet.

## Context

The project is based on an AI Native Back-end Engineer benchmark where RAG, LLM API integration, agent workflow, eval, monitoring, and enterprise document handling are central signals.

The project deliberately excludes on-premise deployment from the first scope. It should remain small enough for a side project while still proving backend depth.

## Core Concept

```text
기업 내부 정책, 업무 매뉴얼, 보안 지침 문서를 권한 기반으로 검색하고,
근거가 있는 답변과 운영 지표를 제공하는 RAG 백엔드
```

## MVP Boundary

In scope:

- document ingestion
- chunking
- embedding storage
- PostgreSQL + pgvector retrieval
- workspace/user/department permission filtering
- retrieval-only API
- LLM provider interface
- fake LLM provider
- OpenAI adapter later
- citation answer API
- token, latency, estimated cost logging
- golden question set eval

Out of scope for the first pass:

- on-premise deployment
- complex multi-agent workflow
- Kubernetes operation
- billing productization
- large-scale document parsing product
- external design-tool-only artifacts

## Recommended Phase Order

### Phase 0: Foundation

Exit criteria:

- README, TODO, project tracking, and next-agent bootstrap exist.
- Project 02 is listed in the side-projects hub.
- First implementation agent can start from this repo without relying on chat history.

### Phase 1: Retrieval Core

Exit criteria:

- FastAPI app starts locally.
- PostgreSQL + pgvector starts through Docker Compose.
- Documents can be registered and chunked.
- Fake embeddings allow deterministic retrieval tests.
- Retrieval API applies permission filters.

### Phase 2: Answer Generation

Exit criteria:

- `LLMProvider` abstraction exists.
- Fake LLM provider supports deterministic tests.
- OpenAI adapter works only when `OPENAI_API_KEY` is present.
- Answer API returns citations and refuses unsupported answers.
- Query logs capture latency, token usage, and estimated cost.

### Phase 3: Eval and Operations

Exit criteria:

- Golden question set can run from CLI.
- Retrieval hit and citation coverage are reported.
- Query logs can be inspected through an admin API or CLI.
- README documents the measured demo result.

### Phase 4: Portfolio Packaging

Exit criteria:

- Public README explains the problem, architecture, run path, and verified scenarios.
- Architecture visual exists as source-trackable SVG/PNG.
- Portfolio one-pager and interview guide exist.
- Demo runbook is reproducible.

## Initial Architecture Sketch

```text
Client/API caller
  -> FastAPI API
  -> Document Service
  -> Chunking Pipeline
  -> EmbeddingProvider
  -> PostgreSQL + pgvector
  -> Retrieval Service with permission filter
  -> LLMProvider
  -> Answer Service with citations
  -> Query Log / Eval Report
```

## Provider Rule

All external AI calls must be behind provider interfaces.

- `EmbeddingProvider`
- `LLMProvider`

The first implementation should use fake providers for tests and local no-key runs. OpenAI integration should be added after retrieval and logging boundaries are stable.

## Verification Strategy

- Unit tests for chunking and provider interfaces
- API tests for document ingestion and retrieval
- Permission filter tests for workspace/user/department combinations
- Deterministic fake provider tests for answer generation
- Eval fixture tests for retrieval hit and citation coverage
- Docker Compose smoke after DB wiring exists

## Next-Agent Instruction

Start with `docs/next-agent-bootstrap.md`. Do not jump directly into OpenAI API wiring. The first implementation slice should be Phase 1 retrieval core with fake embeddings and permission filter tests.

# API and Data Model Draft

Date: 2026-05-21

## API Surface

| Method | Path | Status | Purpose |
|---|---|---|---|
| `GET` | `/health` | implemented | API smoke |
| `GET` | `/workspaces/current` | implemented | demo workspace context |
| `GET` | `/personas` | implemented | demo persona and permission context |
| `GET` | `/auth/session` | implemented | current auth/permission context boundary |
| `POST` | `/documents` | implemented | Markdown/TXT document ingestion |
| `GET` | `/documents` | implemented | Knowledge Library document list |
| `GET` | `/documents/{document_id}` | implemented | document detail and chunk preview |
| `PATCH` | `/admin/documents/{document_id}` | implemented | admin document replacement and synchronous re-index |
| `DELETE` | `/admin/documents/{document_id}` | implemented | admin document deletion |
| `GET` | `/admin/audit-logs` | implemented | session-bound admin audit log list |
| `POST` | `/retrieve` | implemented | permission-aware retrieval-only flow |
| `POST` | `/answer` | implemented | fake-provider answer with citations and refusal |
| `POST` | `/auth/retrieve` | implemented | session-bound retrieval that derives permissions from auth context |
| `POST` | `/auth/answer` | implemented | session-bound answer that derives citations from auth context |
| `GET` | `/metrics/summary` | implemented | query-log-based Operations metrics |
| `GET` | `/metrics/trend` | implemented | daily retrieval/answer query trend |
| `GET` | `/queries/recent` | implemented | recent retrieval/answer query rows |
| `GET` | `/queries/{query_id}` | implemented | stored query detail with retrieval/answer/citation snapshots |
| `GET` | `/evidence/top` | implemented | top evidence documents from retrieval results and citations |
| `POST` | `/eval-runs` | implemented | fake-provider golden eval run |
| `GET` | `/eval-runs` | implemented | persisted fake-provider eval run history |

## Runtime Storage

| Environment | Document repository | Query log repository | Eval run repository |
|---|---|---|---|
| no `DATABASE_URL` | in-memory | in-memory | in-memory |
| `DATABASE_URL` set | PostgreSQL | PostgreSQL | PostgreSQL |

Normal local tests run without `DATABASE_URL` so they stay API-key-free and Docker-free. PostgreSQL integration tests set `RUN_POSTGRES_TESTS=1` and `DATABASE_URL`.

## Provider Selection

| Environment | LLM provider | Notes |
|---|---|---|
| no `LLM_PROVIDER` | `FakeLLMProvider` | default local and CI path |
| `LLM_PROVIDER=fake` | `FakeLLMProvider` | API-key-free |
| `LLM_PROVIDER=openai` | `OpenAILLMProvider` + `OpenAIHTTPTransport` | requires `OPENAI_API_KEY`; live HTTP path is opt-in and not part of default verification |

## Auth Context Selection

| Environment | Auth provider | Notes |
|---|---|---|
| no `AUTH_CONTEXT_PROVIDER` | `demo` | default local and CI path, uses demo persona context |
| `AUTH_CONTEXT_PROVIDER=demo` | `demo` | API-key-free and IdP-free |
| `AUTH_CONTEXT_PROVIDER=trusted_headers` | `trusted_headers` | future gateway/SSO handoff mode; expects trusted identity headers from a protected upstream |

## Core Request Models

### `DocumentCreate`

| Field | Type | Notes |
|---|---|---|
| `workspace_id` | string | workspace boundary |
| `title` | string | document title |
| `source_uri` | string or null | source pointer |
| `content` | string | Markdown/TXT body |
| `content_type` | string | `text/plain`, `text/markdown`, `text/x-markdown` |
| `owner_user_id` | string | private owner and audit context |
| `department_ids` | string[] | normalized unique list |
| `visibility` | string | `public`, `department`, `private` |

### `RetrievalQuery` / `AnswerQuery`

| Field | Type | Notes |
|---|---|---|
| `workspace_id` | string | required |
| `user_id` | string | current persona |
| `department_ids` | string[] | current persona departments |
| `query` | string | user question |
| `top_k` | integer | `1..20` |
| `score_threshold` | number | `0..1` |

### `AuthSession`

| Field | Type | Notes |
|---|---|---|
| `workspace_id` | string | tenant/workspace boundary |
| `user_id` | string | authenticated subject |
| `display_name` | string | display hint |
| `department_ids` | string[] | permission filter input |
| `role` | string | `employee` or `admin` |
| `auth_mode` | string | `demo` or `trusted_headers` |
| `source` | string | source of the session context |

### `SessionSearchQuery`

Used by `/auth/retrieve` and `/auth/answer`.

| Field | Type | Notes |
|---|---|---|
| `query` | string | user question |
| `top_k` | integer | `1..20` |
| `score_threshold` | number | `0..1` |

If `user_id`, `workspace_id`, or `department_ids` are sent in this body, the session-bound endpoints ignore them and derive permission inputs from `AuthSession`.

### `DocumentUpdate`

Used by `PATCH /admin/documents/{document_id}`. The endpoint is session-bound and requires `role=admin`.

| Field | Type | Notes |
|---|---|---|
| `title` | string or null | replacement title |
| `source_uri` | string or null | source pointer |
| `content` | string or null | when present, chunks and embeddings are regenerated |
| `content_type` | string or null | same supported values as `DocumentCreate` |
| `owner_user_id` | string or null | replacement owner |
| `department_ids` | string[] or null | normalized unique list |
| `visibility` | string or null | `public`, `department`, `private` |

## Response Highlights

### Retrieval

`POST /retrieve` returns `query` and ranked `results`. Each result includes:

- `rank`
- `chunk_id`
- `document_id`
- `title`
- `source_uri`
- `chunk_index`
- `text`
- `score`
- `visibility`
- `department_ids`
- `access_reason`

### Answer

`POST /answer` returns:

- `answer`: fake-provider answer text or `null`
- `citations`: cited chunks from permission-filtered retrieval results
- `refusal_reason`: `insufficient_evidence` when citations are empty
- `provider`: `fake`
- `token_count`
- `estimated_cost_usd`
- `latency_ms`
- `retrieved_count`

### Eval

`POST /eval-runs` returns:

- `dataset_id`
- `provider`
- `case_count`
- `retrieval_hit_rate`
- `citation_coverage`
- per-case expected, retrieved, and cited document ids

### Operations

`GET /metrics/summary` returns metrics computed from stored query logs:

- `searches`
- `p95_latency_ms`
- `estimated_cost_usd`
- `retrieval_hit_rate`
- `zero_result_rate`
- `provider`

`GET /metrics/trend` returns daily trend points computed from stored query logs:

- `date`
- `retrieval_count`
- `answer_count`
- `zero_result_count`
- `avg_latency_ms`

`GET /queries/recent` returns the latest query logs. Each row includes:

- `id`
- `workspace_id`
- `user_id`
- `query`
- `mode`: `retrieval` or `answer`
- `latency_ms`
- `retrieved_count`
- `top_score`
- `provider`
- `created_at`

`GET /queries/{query_id}` returns one stored query detail. The response includes:

- `query`: the same row shape as `/queries/recent`
- `retrieval_results`: stored rank, chunk, document, score, and access reason snapshots
- `answer`: stored answer metadata when the row is an answer query
- `citations`: stored citation quote, document, and score snapshots

`GET /evidence/top` returns top evidence documents. Each item includes:

- `document_id`
- `title`
- `source_uri`
- `retrieval_count`
- `citation_count`
- `avg_score`

### Admin

`PATCH /admin/documents/{document_id}` returns:

- `document`: updated document summary including `indexing_status`
- `chunk_count`: regenerated chunk count

`DELETE /admin/documents/{document_id}` returns:

- `document_id`
- `workspace_id`
- `deleted`

`GET /admin/audit-logs` returns append-only admin audit log entries:

- `id`
- `workspace_id`
- `actor_user_id`
- `action`
- `document_id`
- `details`
- `created_at`

## Current PostgreSQL Schema

### `workspaces`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `name` | `TEXT NOT NULL` |
| `created_at` | `TIMESTAMPTZ` |

### `documents`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `title` | `TEXT` |
| `source_uri` | `TEXT` |
| `content_type` | `TEXT` |
| `owner_user_id` | `TEXT` |
| `department_ids` | `TEXT[]` |
| `visibility` | `TEXT` |
| `indexing_status` | `TEXT` |
| `created_at` | `TIMESTAMPTZ` |

### `document_chunks`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `document_id` | `TEXT REFERENCES documents(id)` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `chunk_index` | `INTEGER` |
| `text` | `TEXT` |
| `embedding` | `vector(64)` |
| `created_at` | `TIMESTAMPTZ` |

### `query_logs`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `user_id` | `TEXT` |
| `query` | `TEXT` |
| `mode` | `TEXT CHECK (mode IN ('retrieval', 'answer'))` |
| `latency_ms` | `INTEGER` |
| `retrieved_count` | `INTEGER` |
| `top_score` | `DOUBLE PRECISION` |
| `provider` | `TEXT` |
| `token_count` | `INTEGER` |
| `estimated_cost_usd` | `NUMERIC(12, 6)` |
| `refusal_reason` | `TEXT` |
| `created_at` | `TIMESTAMPTZ` |

### `retrieval_results`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `query_log_id` | `TEXT REFERENCES query_logs(id)` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `chunk_id` | `TEXT` |
| `document_id` | `TEXT` |
| `title` | `TEXT` |
| `source_uri` | `TEXT` |
| `rank` | `INTEGER` |
| `score` | `DOUBLE PRECISION` |
| `access_reason` | `TEXT` |
| `created_at` | `TIMESTAMPTZ` |

### `answers`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `query_log_id` | `TEXT UNIQUE REFERENCES query_logs(id)` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `answer_text` | `TEXT` |
| `refusal_reason` | `TEXT` |
| `provider` | `TEXT` |
| `token_count` | `INTEGER` |
| `estimated_cost_usd` | `NUMERIC(12, 6)` |
| `latency_ms` | `INTEGER` |
| `created_at` | `TIMESTAMPTZ` |

### `citations`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `answer_id` | `TEXT REFERENCES answers(id)` |
| `query_log_id` | `TEXT REFERENCES query_logs(id)` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `rank` | `INTEGER` |
| `chunk_id` | `TEXT` |
| `document_id` | `TEXT` |
| `title` | `TEXT` |
| `source_uri` | `TEXT` |
| `quote_text` | `TEXT` |
| `score` | `DOUBLE PRECISION` |
| `created_at` | `TIMESTAMPTZ` |

### `eval_runs`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `dataset_id` | `TEXT` |
| `provider` | `TEXT` |
| `case_count` | `INTEGER` |
| `retrieval_hit_rate` | `DOUBLE PRECISION` |
| `citation_coverage` | `DOUBLE PRECISION` |
| `created_at` | `TIMESTAMPTZ` |

### `eval_case_results`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `eval_run_id` | `TEXT REFERENCES eval_runs(id)` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `case_id` | `TEXT` |
| `question` | `TEXT` |
| `user_id` | `TEXT` |
| `expected_document_ids` | `TEXT[]` |
| `retrieved_document_ids` | `TEXT[]` |
| `citation_document_ids` | `TEXT[]` |
| `retrieval_hit` | `BOOLEAN` |
| `citation_covered` | `BOOLEAN` |
| `created_at` | `TIMESTAMPTZ` |

### `admin_audit_logs`

| Field | Type |
|---|---|
| `id` | `TEXT PRIMARY KEY` |
| `workspace_id` | `TEXT REFERENCES workspaces(id)` |
| `actor_user_id` | `TEXT` |
| `action` | `TEXT` |
| `document_id` | `TEXT` |
| `details` | `JSONB` |
| `created_at` | `TIMESTAMPTZ` |

## Planned Persistent Tables

| Table | Purpose |
|---|---|
| `eval_datasets` | named eval datasets |
| `eval_cases` | golden questions and expected document ids |

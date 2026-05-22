CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source_uri TEXT,
    content_type TEXT NOT NULL CHECK (content_type IN ('text/plain', 'text/markdown', 'text/x-markdown')),
    owner_user_id TEXT NOT NULL,
    department_ids TEXT[] NOT NULL DEFAULT '{}',
    visibility TEXT NOT NULL CHECK (visibility IN ('public', 'department', 'private')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding vector(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_documents_workspace_visibility
    ON documents (workspace_id, visibility);

CREATE INDEX IF NOT EXISTS idx_documents_owner
    ON documents (workspace_id, owner_user_id);

CREATE INDEX IF NOT EXISTS idx_documents_department_ids
    ON documents USING gin (department_ids);

CREATE INDEX IF NOT EXISTS idx_document_chunks_workspace
    ON document_chunks (workspace_id);

CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
    ON document_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE TABLE IF NOT EXISTS query_logs (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    query TEXT NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('retrieval', 'answer')),
    latency_ms INTEGER NOT NULL CHECK (latency_ms >= 0),
    retrieved_count INTEGER NOT NULL CHECK (retrieved_count >= 0),
    top_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    provider TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0 CHECK (token_count >= 0),
    estimated_cost_usd NUMERIC(12, 6) NOT NULL DEFAULT 0 CHECK (estimated_cost_usd >= 0),
    refusal_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_query_logs_workspace_created_at
    ON query_logs (workspace_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_query_logs_workspace_mode
    ON query_logs (workspace_id, mode);

CREATE TABLE IF NOT EXISTS retrieval_results (
    id TEXT PRIMARY KEY,
    query_log_id TEXT NOT NULL REFERENCES query_logs(id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    title TEXT NOT NULL,
    source_uri TEXT,
    rank INTEGER NOT NULL CHECK (rank >= 1),
    score DOUBLE PRECISION NOT NULL DEFAULT 0,
    access_reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_retrieval_results_workspace_document
    ON retrieval_results (workspace_id, document_id);

CREATE INDEX IF NOT EXISTS idx_retrieval_results_query_log
    ON retrieval_results (query_log_id, rank);

CREATE TABLE IF NOT EXISTS answers (
    id TEXT PRIMARY KEY,
    query_log_id TEXT NOT NULL UNIQUE REFERENCES query_logs(id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    answer_text TEXT,
    refusal_reason TEXT,
    provider TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0 CHECK (token_count >= 0),
    estimated_cost_usd NUMERIC(12, 6) NOT NULL DEFAULT 0 CHECK (estimated_cost_usd >= 0),
    latency_ms INTEGER NOT NULL CHECK (latency_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_answers_workspace_created_at
    ON answers (workspace_id, created_at DESC);

CREATE TABLE IF NOT EXISTS citations (
    id TEXT PRIMARY KEY,
    answer_id TEXT NOT NULL REFERENCES answers(id) ON DELETE CASCADE,
    query_log_id TEXT NOT NULL REFERENCES query_logs(id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL CHECK (rank >= 1),
    chunk_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    title TEXT NOT NULL,
    source_uri TEXT,
    quote_text TEXT NOT NULL,
    score DOUBLE PRECISION NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_citations_workspace_document
    ON citations (workspace_id, document_id);

CREATE INDEX IF NOT EXISTS idx_citations_answer_rank
    ON citations (answer_id, rank);

CREATE TABLE IF NOT EXISTS eval_runs (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    dataset_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    case_count INTEGER NOT NULL CHECK (case_count >= 0),
    retrieval_hit_rate DOUBLE PRECISION NOT NULL DEFAULT 0,
    citation_coverage DOUBLE PRECISION NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_eval_runs_workspace_created_at
    ON eval_runs (workspace_id, created_at DESC);

CREATE TABLE IF NOT EXISTS eval_case_results (
    id TEXT PRIMARY KEY,
    eval_run_id TEXT NOT NULL REFERENCES eval_runs(id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    case_id TEXT NOT NULL,
    question TEXT NOT NULL,
    user_id TEXT NOT NULL,
    expected_document_ids TEXT[] NOT NULL DEFAULT '{}',
    retrieved_document_ids TEXT[] NOT NULL DEFAULT '{}',
    citation_document_ids TEXT[] NOT NULL DEFAULT '{}',
    retrieval_hit BOOLEAN NOT NULL DEFAULT false,
    citation_covered BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_eval_case_results_eval_run
    ON eval_case_results (eval_run_id, case_id);

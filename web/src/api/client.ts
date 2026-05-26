import { normalizePersona, personas, workspace, type ApiPersona, type Persona } from "../fixtures/personas";
import { isStaticDemoMode } from "../config/demoMode";

export async function getCurrentWorkspace() {
  return fetchJson("/api/workspaces/current", workspace);
}

export async function getPersonas() {
  const fallback = { personas };
  const response = await fetchJson<{ personas: ApiPersona[] }>("/api/personas", {
    personas: personas.map((persona) => ({
      id: persona.id,
      display_name: persona.displayName,
      department_ids: persona.departmentIds,
      role: persona.role,
    })),
  });

  return {
    personas: response.personas.map(normalizePersona),
  };
}

export type AuthSession = {
  workspace_id: string;
  user_id: string;
  display_name: string;
  department_ids: string[];
  role: "employee" | "admin";
  auth_mode: "demo" | "trusted_headers";
  source: string;
};

export async function getAuthSession() {
  return fetchJson<AuthSession>("/api/auth/session", fallbackAuthSession);
}

export type RetrievalResult = {
  rank: number;
  chunk_id: string;
  document_id: string;
  workspace_id: string;
  title: string;
  source_uri: string | null;
  chunk_index: number;
  text: string;
  score: number;
  visibility: "public" | "department" | "private";
  department_ids: string[];
  access_reason: "owner" | "public" | "department_match";
};

export type RetrievalResponse = {
  query: string;
  results: RetrievalResult[];
};

export type AnswerCitation = {
  rank: number;
  chunk_id: string;
  document_id: string;
  title: string;
  source_uri: string | null;
  quote: string;
  score: number;
};

export type AnswerResponse = {
  query: string;
  answer: string | null;
  citations: AnswerCitation[];
  refusal_reason: string | null;
  provider: "fake";
  token_count: number;
  estimated_cost_usd: number;
  latency_ms: number;
  retrieved_count: number;
};

export type DocumentSummary = {
  id: string;
  workspace_id: string;
  title: string;
  source_uri: string | null;
  content_type: string;
  owner_user_id: string;
  department_ids: string[];
  visibility: "public" | "department" | "private";
  chunk_count: number;
};

export type DocumentChunkPreview = {
  id: string;
  document_id: string;
  workspace_id: string;
  chunk_index: number;
  text: string;
  embedding_dimensions: number;
};

export type DocumentListResponse = {
  documents: DocumentSummary[];
};

export type DocumentDetailResponse = {
  document: DocumentSummary;
  chunks: DocumentChunkPreview[];
};

export type MetricsSummary = {
  workspace_id: string;
  searches: number;
  p95_latency_ms: number;
  estimated_cost_usd: number;
  retrieval_hit_rate: number;
  zero_result_rate: number;
  provider: string;
};

export type QueryTrendPoint = {
  date: string;
  retrieval_count: number;
  answer_count: number;
  zero_result_count: number;
  avg_latency_ms: number;
};

export type QueryTrendResponse = {
  workspace_id: string;
  points: QueryTrendPoint[];
};

export type RecentQuery = {
  id: string;
  workspace_id: string;
  user_id: string;
  query: string;
  mode: "retrieval" | "answer";
  latency_ms: number;
  retrieved_count: number;
  top_score: number;
  provider: string;
  created_at: string;
};

export type RecentQueriesResponse = {
  queries: RecentQuery[];
};

export type QueryRetrievalSnapshot = {
  rank: number;
  chunk_id: string;
  document_id: string;
  title: string;
  source_uri: string | null;
  score: number;
  access_reason: string;
};

export type QueryAnswerSnapshot = {
  answer: string | null;
  refusal_reason: string | null;
  provider: string;
  token_count: number;
  estimated_cost_usd: number;
  latency_ms: number;
};

export type QueryCitationSnapshot = {
  rank: number;
  chunk_id: string;
  document_id: string;
  title: string;
  source_uri: string | null;
  quote: string;
  score: number;
};

export type QueryDetailResponse = {
  query: RecentQuery;
  retrieval_results: QueryRetrievalSnapshot[];
  answer: QueryAnswerSnapshot | null;
  citations: QueryCitationSnapshot[];
};

export type TopEvidenceItem = {
  document_id: string;
  title: string;
  source_uri: string | null;
  retrieval_count: number;
  citation_count: number;
  avg_score: number;
};

export type TopEvidenceResponse = {
  workspace_id: string;
  items: TopEvidenceItem[];
};

export type EvalCaseResult = {
  case_id: string;
  question: string;
  user_id: string;
  expected_document_ids: string[];
  retrieved_document_ids: string[];
  citation_document_ids: string[];
  retrieval_hit: boolean;
  citation_covered: boolean;
};

export type EvalRun = {
  id: string;
  workspace_id: string;
  dataset_id: string;
  provider: "fake";
  case_count: number;
  retrieval_hit_rate: number;
  citation_coverage: number;
  created_at: string;
  cases: EvalCaseResult[];
};

export type EvalRunsResponse = {
  runs: EvalRun[];
};

export async function loadEvalRuns(workspaceId: string) {
  return fetchJson<EvalRunsResponse>(
    `/api/eval-runs?workspace_id=${encodeURIComponent(workspaceId)}`,
    { runs: [fallbackEvalRun] },
  );
}

export async function loadOperationsSummary(workspaceId: string) {
  return fetchJson<MetricsSummary>(
    `/api/metrics/summary?workspace_id=${encodeURIComponent(workspaceId)}`,
    fallbackMetrics,
  );
}

export async function loadQueryTrend(workspaceId: string) {
  return fetchJson<QueryTrendResponse>(
    `/api/metrics/trend?workspace_id=${encodeURIComponent(workspaceId)}`,
    { workspace_id: workspaceId, points: fallbackTrend },
  );
}

export async function loadRecentQueries(workspaceId: string) {
  return fetchJson<RecentQueriesResponse>(
    `/api/queries/recent?workspace_id=${encodeURIComponent(workspaceId)}`,
    { queries: fallbackQueries },
  );
}

export async function loadQueryDetail(workspaceId: string, queryId: string) {
  return fetchJson<QueryDetailResponse>(
    `/api/queries/${encodeURIComponent(queryId)}?workspace_id=${encodeURIComponent(workspaceId)}`,
    fallbackQueryDetail(workspaceId, queryId),
  );
}

export async function loadTopEvidence(workspaceId: string) {
  return fetchJson<TopEvidenceResponse>(
    `/api/evidence/top?workspace_id=${encodeURIComponent(workspaceId)}`,
    { workspace_id: workspaceId, items: fallbackTopEvidence },
  );
}

export async function loadDocuments(workspaceId: string) {
  return fetchJson<DocumentListResponse>(
    `/api/documents?workspace_id=${encodeURIComponent(workspaceId)}`,
    { documents: fallbackDocuments },
  );
}

export async function loadDocumentDetail(workspaceId: string, documentId: string) {
  return fetchJson<DocumentDetailResponse>(
    `/api/documents/${encodeURIComponent(documentId)}?workspace_id=${encodeURIComponent(workspaceId)}`,
    fallbackDocumentDetail(documentId),
  );
}

export async function loadRetrieval({
  workspaceId,
  persona,
  query,
  topK = 5,
  scoreThreshold = 0,
}: {
  workspaceId: string;
  persona: Persona;
  query: string;
  topK?: number;
  scoreThreshold?: number;
}) {
  return fetchJson<RetrievalResponse>("/api/retrieve", {
    query,
    results: fallbackResults(persona),
  }, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      workspace_id: workspaceId,
      user_id: persona.id,
      department_ids: persona.departmentIds,
      query,
      top_k: topK,
      score_threshold: scoreThreshold,
    }),
  });
}

export async function loadAnswer({
  workspaceId,
  persona,
  query,
  topK = 5,
  scoreThreshold = 0,
}: {
  workspaceId: string;
  persona: Persona;
  query: string;
  topK?: number;
  scoreThreshold?: number;
}) {
  return fetchJson<AnswerResponse>("/api/answer", fallbackAnswer(persona, query), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      workspace_id: workspaceId,
      user_id: persona.id,
      department_ids: persona.departmentIds,
      query,
      top_k: topK,
      score_threshold: scoreThreshold,
    }),
  });
}

async function fetchJson<T>(path: string, fallback: T, init?: RequestInit): Promise<T> {
  if (isStaticDemoMode) {
    return fallback;
  }

  try {
    const response = await fetch(path, init);
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

const fallbackDocuments: DocumentSummary[] = [
  {
    id: "doc_1",
    workspace_id: "acme",
    title: "Remote Access Policy",
    source_uri: "policy://remote-access",
    content_type: "text/markdown",
    owner_user_id: "admin-platform",
    department_ids: ["platform", "security"],
    visibility: "public",
    chunk_count: 1,
  },
  {
    id: "doc_2",
    workspace_id: "acme",
    title: "Security Incident Manual",
    source_uri: "policy://security-incident",
    content_type: "text/markdown",
    owner_user_id: "mina-security",
    department_ids: ["security"],
    visibility: "department",
    chunk_count: 1,
  },
  {
    id: "doc_3",
    workspace_id: "acme",
    title: "Finance Reimbursement Policy",
    source_uri: "policy://finance-reimbursement",
    content_type: "text/markdown",
    owner_user_id: "joon-finance",
    department_ids: ["finance"],
    visibility: "department",
    chunk_count: 1,
  },
  {
    id: "doc_4",
    workspace_id: "acme",
    title: "Executive Access Exception",
    source_uri: "policy://executive-access",
    content_type: "text/markdown",
    owner_user_id: "admin-platform",
    department_ids: ["platform"],
    visibility: "private",
    chunk_count: 1,
  },
];

const fallbackAuthSession: AuthSession = {
  workspace_id: workspace.id,
  user_id: personas[0].id,
  display_name: personas[0].displayName,
  department_ids: personas[0].departmentIds,
  role: personas[0].role,
  auth_mode: "demo",
  source: "demo_persona",
};

function fallbackDocumentDetail(documentId: string): DocumentDetailResponse {
  const document = fallbackDocuments.find((item) => item.id === documentId) ?? fallbackDocuments[0];
  return {
    document,
    chunks: [
      {
        id: `${document.id}-chunk-1`,
        document_id: document.id,
        workspace_id: document.workspace_id,
        chunk_index: 0,
        text: fallbackChunkText(document.title),
        embedding_dimensions: 32,
      },
    ],
  };
}

function fallbackChunkText(title: string): string {
  if (title.includes("Security")) {
    return "보안 사고 발생 시 즉시 Security on-call 채널에 알리고 incident commander를 지정합니다.";
  }
  if (title.includes("Finance")) {
    return "식대 정산 기준은 영수증 제출과 프로젝트 코드 입력을 포함합니다.";
  }
  if (title.includes("Executive")) {
    return "임원 접근 예외 절차는 platform admin owner 승인이 있어야 진행됩니다.";
  }
  return "VPN 등록 절차는 사내 포털에서 기기 등록을 완료한 뒤 보안 승인을 요청합니다.";
}

const fallbackMetrics: MetricsSummary = {
  workspace_id: "acme",
  searches: 128,
  p95_latency_ms: 184,
  estimated_cost_usd: 0,
  retrieval_hit_rate: 0.92,
  zero_result_rate: 0.08,
  provider: "fake",
};

const fallbackQueries: RecentQuery[] = [
  {
    id: "query_001",
    workspace_id: "acme",
    user_id: "mina-security",
    query: "security incident evidence",
    mode: "retrieval",
    latency_ms: 142,
    retrieved_count: 2,
    top_score: 0.603023,
    provider: "fake",
    created_at: "2026-05-21T08:42:00+09:00",
  },
  {
    id: "query_002",
    workspace_id: "acme",
    user_id: "joon-finance",
    query: "meal reimbursement receipt",
    mode: "retrieval",
    latency_ms: 118,
    retrieved_count: 1,
    top_score: 0.512401,
    provider: "fake",
    created_at: "2026-05-21T08:35:00+09:00",
  },
];

const fallbackTrend: QueryTrendPoint[] = [
  {
    date: "2026-05-21",
    retrieval_count: 18,
    answer_count: 11,
    zero_result_count: 2,
    avg_latency_ms: 144,
  },
];

function fallbackQueryDetail(workspaceId: string, queryId: string): QueryDetailResponse {
  const query = fallbackQueries.find((item) => item.id === queryId) ?? {
    ...fallbackQueries[0],
    id: queryId,
    workspace_id: workspaceId,
  };
  const result = fallbackResults(personas[0])[0];
  return {
    query,
    retrieval_results: result
      ? [
          {
            rank: result.rank,
            chunk_id: result.chunk_id,
            document_id: result.document_id,
            title: result.title,
            source_uri: result.source_uri,
            score: result.score,
            access_reason: result.access_reason,
          },
        ]
      : [],
    answer:
      query.mode === "answer"
        ? {
            answer: result ? `제공된 근거 기준으로 답변합니다. ${result.text}` : null,
            refusal_reason: result ? null : "insufficient_evidence",
            provider: "fake",
            token_count: result ? 42 : 1,
            estimated_cost_usd: 0,
            latency_ms: query.latency_ms,
          }
        : null,
    citations:
      query.mode === "answer" && result
        ? [
            {
              rank: result.rank,
              chunk_id: result.chunk_id,
              document_id: result.document_id,
              title: result.title,
              source_uri: result.source_uri,
              quote: result.text,
              score: result.score,
            },
          ]
        : [],
  };
}

const fallbackTopEvidence: TopEvidenceItem[] = [
  {
    document_id: "doc_2",
    title: "Security Incident Manual",
    source_uri: "policy://security-incident",
    retrieval_count: 12,
    citation_count: 8,
    avg_score: 0.88,
  },
  {
    document_id: "doc_3",
    title: "Finance Reimbursement Policy",
    source_uri: "policy://finance-reimbursement",
    retrieval_count: 7,
    citation_count: 4,
    avg_score: 0.81,
  },
];

const fallbackEvalRun: EvalRun = {
  id: "eval_golden-demo_fake",
  workspace_id: "acme",
  dataset_id: "golden-demo",
  provider: "fake",
  case_count: 3,
  retrieval_hit_rate: 1,
  citation_coverage: 1,
  created_at: "2026-05-21T09:00:00+09:00",
  cases: [
    {
      case_id: "security-incident",
      question: "security incident evidence",
      user_id: "mina-security",
      expected_document_ids: ["doc_2"],
      retrieved_document_ids: ["doc_2"],
      citation_document_ids: ["doc_2"],
      retrieval_hit: true,
      citation_covered: true,
    },
  ],
};

function fallbackAnswer(persona: Persona, query: string): AnswerResponse {
  const result = fallbackResults(persona)[0];
  if (!result) {
    return {
      query,
      answer: null,
      citations: [],
      refusal_reason: "insufficient_evidence",
      provider: "fake",
      token_count: 1,
      estimated_cost_usd: 0,
      latency_ms: 0,
      retrieved_count: 0,
    };
  }

  return {
    query,
    answer: `제공된 근거 기준으로 답변합니다. ${result.text}`,
    citations: [
      {
        rank: result.rank,
        chunk_id: result.chunk_id,
        document_id: result.document_id,
        title: result.title,
        source_uri: result.source_uri,
        quote: result.text,
        score: result.score,
      },
    ],
    refusal_reason: null,
    provider: "fake",
    token_count: 42,
    estimated_cost_usd: 0,
    latency_ms: 0,
    retrieved_count: 1,
  };
}

function fallbackResults(persona: Persona): RetrievalResult[] {
  if (persona.departmentIds.includes("finance")) {
    return [
      {
        rank: 1,
        chunk_id: "demo-finance",
        document_id: "demo-finance-doc",
        workspace_id: "acme",
        title: "Finance Reimbursement Policy",
        source_uri: "policy://finance-reimbursement",
        chunk_index: 0,
        text: "식대 정산 기준은 영수증 제출과 프로젝트 코드 입력을 포함합니다.",
        score: 0.84,
        visibility: "department",
        department_ids: ["finance"],
        access_reason: "department_match",
      },
    ];
  }

  return [
    {
      rank: 1,
      chunk_id: "demo-security",
      document_id: "demo-security-doc",
      workspace_id: "acme",
      title: "Security Incident Manual",
      source_uri: "policy://security-incident",
      chunk_index: 0,
      text: "보안 사고 발생 시 즉시 Security on-call 채널에 알리고 incident commander를 지정합니다.",
      score: 0.88,
      visibility: "department",
      department_ids: ["security"],
      access_reason: "department_match",
    },
  ];
}

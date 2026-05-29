"""도메인 모델 모듈: 문서/검색/로그/평가 API가 주고받는 스키마를 경계 기반으로 통합 관리한다."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

SUPPORTED_CONTENT_TYPES = {"text/plain", "text/markdown", "text/x-markdown"}


class Visibility(str, Enum):
    # 공개 범위 규칙을 enum으로 고정해 권한 판정 지점에서 문자열 분기 오동작을 방지한다.
    PUBLIC = "public"
    DEPARTMENT = "department"
    PRIVATE = "private"


class IndexingStatus(str, Enum):
    QUEUED = "queued"
    INDEXING = "indexing"
    READY = "ready"
    FAILED = "failed"


class DocumentCreate(BaseModel):
    workspace_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_uri: Optional[str] = None
    content: str = Field(min_length=1)
    content_type: str
    owner_user_id: str = Field(min_length=1)
    department_ids: list[str] = Field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value: str) -> str:
        # 허용 포맷만 통과시켜 저장 계층의 인덱싱/검색 포맷 가정과 일치성을 유지한다.
        if value not in SUPPORTED_CONTENT_TYPES:
            supported = ", ".join(sorted(SUPPORTED_CONTENT_TYPES))
            raise ValueError(f"unsupported content_type: {value}; supported: {supported}")
        return value

    @field_validator("department_ids")
    @classmethod
    def normalize_departments(cls, value: list[str]) -> list[str]:
        # 공백/중복 department_id를 정리해 정책 조회 및 접근 제어의 비교 집합을 단순화한다.
        return sorted({item.strip() for item in value if item.strip()})


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    source_uri: Optional[str] = None
    content: Optional[str] = Field(default=None, min_length=1)
    content_type: Optional[str] = None
    owner_user_id: Optional[str] = Field(default=None, min_length=1)
    department_ids: Optional[list[str]] = None
    visibility: Optional[Visibility] = None

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value: Optional[str]) -> Optional[str]:
        # 부분 업데이트 시에도 타입 변경이 들어오면 동일 정책 제약을 동일하게 적용한다.
        if value is None:
            return value
        if value not in SUPPORTED_CONTENT_TYPES:
            supported = ", ".join(sorted(SUPPORTED_CONTENT_TYPES))
            raise ValueError(f"unsupported content_type: {value}; supported: {supported}")
        return value

    @field_validator("department_ids")
    @classmethod
    def normalize_departments(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        # 업데이트에서 null/빈값을 구분하고, 실제 값은 공백 제거 및 dedupe로 안정화한다.
        if value is None:
            return value
        return sorted({item.strip() for item in value if item.strip()})


class StoredDocument(BaseModel):
    id: str
    workspace_id: str
    title: str
    source_uri: Optional[str]
    content_type: str
    owner_user_id: str
    department_ids: list[str]
    visibility: Visibility
    indexing_status: IndexingStatus = IndexingStatus.READY


class StoredChunk(BaseModel):
    id: str
    document_id: str
    workspace_id: str
    title: str
    source_uri: Optional[str]
    owner_user_id: str
    department_ids: list[str]
    visibility: Visibility
    chunk_index: int
    text: str
    embedding: list[float]


class DocumentIngestResponse(BaseModel):
    document_id: str
    workspace_id: str
    chunk_count: int


class DocumentSummary(BaseModel):
    id: str
    workspace_id: str
    title: str
    source_uri: Optional[str]
    content_type: str
    owner_user_id: str
    department_ids: list[str]
    visibility: Visibility
    indexing_status: IndexingStatus
    chunk_count: int


class DocumentChunkPreview(BaseModel):
    id: str
    document_id: str
    workspace_id: str
    chunk_index: int
    text: str
    embedding_dimensions: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentSummary]


class DocumentDetailResponse(BaseModel):
    document: DocumentSummary
    chunks: list[DocumentChunkPreview]


class AdminDocumentUpdateResponse(BaseModel):
    document: DocumentSummary
    chunk_count: int


class AdminDocumentDeleteResponse(BaseModel):
    document_id: str
    workspace_id: str
    deleted: bool


class AdminAuditLogCreate(BaseModel):
    workspace_id: str = Field(min_length=1)
    actor_user_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    document_id: Optional[str] = None
    details: dict[str, object] = Field(default_factory=dict)


class StoredAdminAuditLog(AdminAuditLogCreate):
    id: str
    created_at: str


class AdminAuditLogsResponse(BaseModel):
    logs: list[StoredAdminAuditLog]


class RetrievalQuery(BaseModel):
    workspace_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    department_ids: list[str] = Field(default_factory=list)
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0, ge=0, le=1)

    @field_validator("department_ids")
    @classmethod
    def normalize_departments(cls, value: list[str]) -> list[str]:
        # 조회권한 계산을 위해 department_id 집합을 정렬해 비교 결과 재현성을 높인다.
        return sorted({item.strip() for item in value if item.strip()})


class RetrievalResult(BaseModel):
    rank: int
    chunk_id: str
    document_id: str
    workspace_id: str
    title: str
    source_uri: Optional[str]
    chunk_index: int
    text: str
    score: float
    visibility: Visibility
    department_ids: list[str]
    access_reason: str


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalResult]


class AnswerQuery(RetrievalQuery):
    pass


class AnswerCitation(BaseModel):
    rank: int
    chunk_id: str
    document_id: str
    title: str
    source_uri: Optional[str]
    quote: str
    score: float


class AnswerResponse(BaseModel):
    query: str
    answer: Optional[str]
    citations: list[AnswerCitation]
    refusal_reason: Optional[str]
    provider: str
    token_count: int
    estimated_cost_usd: float
    latency_ms: int
    retrieved_count: int


class MetricsSummaryResponse(BaseModel):
    workspace_id: str
    searches: int
    p95_latency_ms: int
    estimated_cost_usd: float
    retrieval_hit_rate: float
    zero_result_rate: float
    provider: str


class QueryTrendPoint(BaseModel):
    date: str
    retrieval_count: int
    answer_count: int
    zero_result_count: int
    avg_latency_ms: int


class QueryTrendResponse(BaseModel):
    workspace_id: str
    points: list[QueryTrendPoint]


class RecentQuery(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    query: str
    mode: str
    latency_ms: int
    retrieved_count: int
    top_score: float
    provider: str
    created_at: str


class RecentQueriesResponse(BaseModel):
    queries: list[RecentQuery]


class TopEvidenceItem(BaseModel):
    document_id: str
    title: str
    source_uri: Optional[str]
    retrieval_count: int
    citation_count: int
    avg_score: float


class TopEvidenceResponse(BaseModel):
    workspace_id: str
    items: list[TopEvidenceItem]


class QueryRetrievalSnapshot(BaseModel):
    rank: int
    chunk_id: str
    document_id: str
    title: str
    source_uri: Optional[str]
    score: float
    access_reason: str


class QueryAnswerSnapshot(BaseModel):
    answer: Optional[str]
    refusal_reason: Optional[str]
    provider: str
    token_count: int
    estimated_cost_usd: float
    latency_ms: int


class QueryCitationSnapshot(BaseModel):
    rank: int
    chunk_id: str
    document_id: str
    title: str
    source_uri: Optional[str]
    quote: str
    score: float


class QueryDetailResponse(BaseModel):
    query: RecentQuery
    retrieval_results: list[QueryRetrievalSnapshot]
    answer: Optional[QueryAnswerSnapshot]
    citations: list[QueryCitationSnapshot]


class QueryLogCreate(BaseModel):
    workspace_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    mode: Literal["retrieval", "answer"]
    latency_ms: int = Field(ge=0)
    retrieved_count: int = Field(ge=0)
    top_score: float = Field(default=0.0, ge=0)
    provider: str = Field(default="fake", min_length=1)
    token_count: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0)
    refusal_reason: Optional[str] = None
    created_at: Optional[str] = None


class StoredQueryLog(QueryLogCreate):
    id: str


class EvalRunRequest(BaseModel):
    workspace_id: str = Field(min_length=1)
    dataset_id: str = Field(default="golden-demo", min_length=1)


class EvalCaseResult(BaseModel):
    case_id: str
    question: str
    user_id: str
    expected_document_ids: list[str]
    retrieved_document_ids: list[str]
    citation_document_ids: list[str]
    retrieval_hit: bool
    citation_covered: bool


class EvalRunResponse(BaseModel):
    id: str
    workspace_id: str
    dataset_id: str
    provider: str
    case_count: int
    retrieval_hit_rate: float
    citation_coverage: float
    created_at: str
    cases: list[EvalCaseResult]


class EvalRunsResponse(BaseModel):
    runs: list[EvalRunResponse]

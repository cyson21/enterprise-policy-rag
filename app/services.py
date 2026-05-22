from __future__ import annotations

from time import perf_counter

from app.chunking import chunk_text
from app.answer import AnswerService
from app.eval_runs import EvalRunRepository, InMemoryEvalRunRepository
from app.models import (
    AnswerQuery,
    AnswerResponse,
    DocumentChunkPreview,
    DocumentCreate,
    DocumentDetailResponse,
    DocumentIngestResponse,
    DocumentListResponse,
    DocumentSummary,
    MetricsSummaryResponse,
    QueryLogCreate,
    QueryDetailResponse,
    QueryTrendResponse,
    RecentQueriesResponse,
    RetrievalQuery,
    RetrievalResponse,
    StoredDocument,
    TopEvidenceResponse,
)
from app.providers import EmbeddingProvider, FakeEmbeddingProvider, LLMProvider
from app.query_logs import (
    InMemoryQueryLogRepository,
    QueryLogRepository,
    build_metrics_summary,
    build_recent_queries,
)
from app.repository import InMemoryPolicyRepository, PolicyRepository
from app.retrieval import RetrievalService


class PolicyRagServices:
    def __init__(
        self,
        repository: PolicyRepository | None = None,
        query_log_repository: QueryLogRepository | None = None,
        eval_run_repository: EvalRunRepository | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.repository = repository or InMemoryPolicyRepository()
        self.query_log_repository = query_log_repository or InMemoryQueryLogRepository()
        self.eval_run_repository = eval_run_repository or InMemoryEvalRunRepository()
        self.embedding_provider = embedding_provider or FakeEmbeddingProvider()
        self.llm_provider = llm_provider

    def ingest_document(self, payload: DocumentCreate) -> DocumentIngestResponse:
        chunks = chunk_text(payload.content)
        embeddings = self.embedding_provider.embed_many([chunk.text for chunk in chunks])
        stored = self.repository.add_document(payload, chunks, embeddings)
        return DocumentIngestResponse(
            document_id=stored.id,
            workspace_id=stored.workspace_id,
            chunk_count=len(chunks),
        )

    def list_documents(self, workspace_id: str) -> DocumentListResponse:
        documents = [
            self._build_document_summary(document)
            for document in self.repository.list_documents(workspace_id)
        ]
        return DocumentListResponse(documents=documents)

    def get_document_detail(self, workspace_id: str, document_id: str) -> DocumentDetailResponse | None:
        document = self.repository.get_document(workspace_id=workspace_id, document_id=document_id)
        if document is None:
            return None

        chunks = [
            DocumentChunkPreview(
                id=chunk.id,
                document_id=chunk.document_id,
                workspace_id=chunk.workspace_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                embedding_dimensions=len(chunk.embedding),
            )
            for chunk in self.repository.list_document_chunks(workspace_id=workspace_id, document_id=document_id)
        ]
        return DocumentDetailResponse(document=self._build_document_summary(document), chunks=chunks)

    def retrieve(self, payload: RetrievalQuery) -> RetrievalResponse:
        started = perf_counter()
        service = RetrievalService(repository=self.repository, embedding_provider=self.embedding_provider)
        response = service.retrieve(payload)
        query_log = self.query_log_repository.add_query_log(
            QueryLogCreate(
                workspace_id=payload.workspace_id,
                user_id=payload.user_id,
                query=payload.query,
                mode="retrieval",
                latency_ms=_elapsed_ms(started),
                retrieved_count=len(response.results),
                top_score=response.results[0].score if response.results else 0.0,
                provider="fake",
            )
        )
        self.query_log_repository.add_retrieval_results(query_log.id, response.results)
        return response

    def answer(self, payload: AnswerQuery) -> AnswerResponse:
        service = AnswerService(
            repository=self.repository,
            embedding_provider=self.embedding_provider,
            llm_provider=self.llm_provider,
        )
        response = service.answer(payload)
        query_log = self.query_log_repository.add_query_log(
            QueryLogCreate(
                workspace_id=payload.workspace_id,
                user_id=payload.user_id,
                query=payload.query,
                mode="answer",
                latency_ms=response.latency_ms,
                retrieved_count=response.retrieved_count,
                top_score=response.citations[0].score if response.citations else 0.0,
                provider=response.provider,
                token_count=response.token_count,
                estimated_cost_usd=response.estimated_cost_usd,
                refusal_reason=response.refusal_reason,
            )
        )
        self.query_log_repository.add_answer_record(query_log.id, response)
        return response

    def get_metrics_summary(self, workspace_id: str) -> MetricsSummaryResponse:
        logs = self.query_log_repository.list_query_logs(workspace_id)
        return build_metrics_summary(workspace_id, logs)

    def list_recent_queries(self, workspace_id: str) -> RecentQueriesResponse:
        logs = self.query_log_repository.list_query_logs(workspace_id, limit=20)
        return build_recent_queries(logs)

    def get_query_detail(self, workspace_id: str, query_id: str) -> QueryDetailResponse | None:
        return self.query_log_repository.get_query_detail(workspace_id=workspace_id, query_id=query_id)

    def list_top_evidence(self, workspace_id: str) -> TopEvidenceResponse:
        return TopEvidenceResponse(
            workspace_id=workspace_id,
            items=self.query_log_repository.list_top_evidence(workspace_id, limit=10),
        )

    def get_query_trend(self, workspace_id: str) -> QueryTrendResponse:
        return QueryTrendResponse(
            workspace_id=workspace_id,
            points=self.query_log_repository.list_query_trend(workspace_id, limit=14),
        )

    def _build_document_summary(self, document: StoredDocument) -> DocumentSummary:
        chunks = self.repository.list_document_chunks(
            workspace_id=document.workspace_id,
            document_id=document.id,
        )
        return DocumentSummary(
            id=document.id,
            workspace_id=document.workspace_id,
            title=document.title,
            source_uri=document.source_uri,
            content_type=document.content_type,
            owner_user_id=document.owner_user_id,
            department_ids=document.department_ids,
            visibility=document.visibility,
            chunk_count=len(chunks),
        )


def _elapsed_ms(started: float) -> int:
    return max(0, int((perf_counter() - started) * 1000))

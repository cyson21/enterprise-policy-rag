from __future__ import annotations

from time import perf_counter

from app.chunking import chunk_text
from app.answer import AnswerService
from app.eval_runs import EvalRunRepository, InMemoryEvalRunRepository
from app.models import (
    AdminAuditLogCreate,
    AdminAuditLogsResponse,
    AdminDocumentDeleteResponse,
    AdminDocumentUpdateResponse,
    AnswerQuery,
    AnswerResponse,
    DocumentChunkPreview,
    DocumentCreate,
    DocumentDetailResponse,
    DocumentIngestResponse,
    DocumentListResponse,
    DocumentSummary,
    DocumentUpdate,
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
    # 서비스는 라우트 요청과 도메인 규칙 사이의 조정자 역할을 하며, provider/저장소 경계를 일관되게 묶는다.
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
        # 업로드 즉시 chunking + embedding으로 검색에 필요한 형태만 저장해 검색 가능 상태로 만들고 응답한다.
        chunks = chunk_text(payload.content)
        embeddings = self.embedding_provider.embed_many([chunk.text for chunk in chunks])
        stored = self.repository.add_document(payload, chunks, embeddings)
        return DocumentIngestResponse(
            document_id=stored.id,
            workspace_id=stored.workspace_id,
            chunk_count=len(chunks),
        )

    def list_documents(self, workspace_id: str) -> DocumentListResponse:
        # list_documents는 read model 생성만 담당하고, 변경 동작 없이 집계만 정제해 반환한다.
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

    def update_document(
        self,
        workspace_id: str,
        document_id: str,
        payload: DocumentUpdate,
        actor_user_id: str,
    ) -> AdminDocumentUpdateResponse | None:
        existing = self.repository.get_document(workspace_id=workspace_id, document_id=document_id)
        if existing is None:
            return None

        existing_chunks = self.repository.list_document_chunks(workspace_id=workspace_id, document_id=document_id)
        content = payload.content
        if content is None:
            # 부분 수정에서 content가 비면 기존 청크를 다시 합쳐서 재색인 입력을 만든다.
            content = "\n\n".join(chunk.text for chunk in existing_chunks) or " "

        replacement = DocumentCreate(
            workspace_id=workspace_id,
            title=payload.title if payload.title is not None else existing.title,
            source_uri=payload.source_uri if payload.source_uri is not None else existing.source_uri,
            content=content,
            content_type=payload.content_type if payload.content_type is not None else existing.content_type,
            owner_user_id=payload.owner_user_id if payload.owner_user_id is not None else existing.owner_user_id,
            department_ids=payload.department_ids if payload.department_ids is not None else existing.department_ids,
            visibility=payload.visibility if payload.visibility is not None else existing.visibility,
        )
        chunks = chunk_text(replacement.content)
        embeddings = self.embedding_provider.embed_many([chunk.text for chunk in chunks])
        stored = self.repository.update_document(
            document_id=document_id,
            document=replacement,
            chunks=chunks,
            embeddings=embeddings,
        )
        if stored is None:
            return None

        self.repository.add_admin_audit_log(
            AdminAuditLogCreate(
                workspace_id=workspace_id,
                actor_user_id=actor_user_id,
                action="document.updated",
                document_id=document_id,
                details={
                    "title": stored.title,
                    "visibility": stored.visibility.value,
                    "department_ids": stored.department_ids,
                    "indexing_status": stored.indexing_status.value,
                },
            )
        )
        return AdminDocumentUpdateResponse(
            document=self._build_document_summary(stored),
            chunk_count=len(chunks),
        )

    def delete_document(
        self,
        workspace_id: str,
        document_id: str,
        actor_user_id: str,
    ) -> AdminDocumentDeleteResponse | None:
        deleted = self.repository.delete_document(workspace_id=workspace_id, document_id=document_id)
        if deleted is None:
            return None
        self.repository.add_admin_audit_log(
            AdminAuditLogCreate(
                workspace_id=workspace_id,
                actor_user_id=actor_user_id,
                action="document.deleted",
                document_id=document_id,
                details={"title": deleted.title, "visibility": deleted.visibility.value},
            )
        )
        return AdminDocumentDeleteResponse(document_id=document_id, workspace_id=workspace_id, deleted=True)

    def list_admin_audit_logs(self, workspace_id: str) -> AdminAuditLogsResponse:
        return AdminAuditLogsResponse(logs=self.repository.list_admin_audit_logs(workspace_id, limit=50))

    def retrieve(self, payload: RetrievalQuery) -> RetrievalResponse:
        # 질의 요청은 즉시 서비스 내부 로그 객체를 먼저 남기고, 검색 결과와 연결해 추적 가능한 분석 단위를 만든다.
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
                # retrieval 단계의 provider는 실제 임베딩 provider 식별자를 기록한다.
                provider=getattr(self.embedding_provider, "provider_name", "fake"),
            )
        )
        self.query_log_repository.add_retrieval_results(query_log.id, response.results)
        return response

    def answer(self, payload: AnswerQuery) -> AnswerResponse:
        # 검색 결과를 바탕으로 근거 기반 답변을 구성하고, 쿼리 로그에 provider/토큰/지연값을 함께 기록한다.
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
        # API 응답용 summary는 소스 문서+청크 개수를 즉시 계산해 list/detail에서 중복 쿼리 없이 쓰기 쉽도록 정리한다.
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
            indexing_status=document.indexing_status,
            chunk_count=len(chunks),
        )


def _elapsed_ms(started: float) -> int:
    return max(0, int((perf_counter() - started) * 1000))

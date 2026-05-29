from __future__ import annotations

from app.models import RetrievalQuery, RetrievalResponse, RetrievalResult, StoredChunk, Visibility
from app.providers import EmbeddingProvider
from app.repository import PolicyRepository


class RetrievalService:
    """질의 임베딩 생성부터 정렬된 증거 집계까지를 담당하는 검색 서비스."""
    def __init__(
        self,
        repository: PolicyRepository,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self.repository = repository
        self.embedding_provider = embedding_provider

    def retrieve(self, query: RetrievalQuery) -> RetrievalResponse:
        query_embedding = self.embedding_provider.embed(query.query)
        scored_results: list[tuple[float, StoredChunk, str]] = []

        for chunk in self.repository.list_chunks(query.workspace_id):
            access_reason = _access_reason(chunk, query)
            if access_reason is None:
                continue
            score = _similarity(query_embedding, chunk.embedding)
            if score <= 0 or score < query.score_threshold:
                continue
            # 점수 임계값 미만은 제거하고, 접근권한 검증이 끝난 항목만 순위 후보로 적재한다.
            scored_results.append((score, chunk, access_reason))

        scored_results.sort(key=lambda item: (-item[0], item[1].document_id, item[1].chunk_index, item[1].id))
        results = [
            RetrievalResult(
                rank=rank,
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                workspace_id=chunk.workspace_id,
                title=chunk.title,
                source_uri=chunk.source_uri,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                score=round(score, 6),
                visibility=chunk.visibility,
                department_ids=chunk.department_ids,
                access_reason=access_reason,
            )
            for rank, (score, chunk, access_reason) in enumerate(scored_results[: query.top_k], start=1)
        ]
        return RetrievalResponse(query=query.query, results=results)


def _access_reason(chunk: StoredChunk, query: RetrievalQuery) -> str | None:
    # 검색 결과의 접근근거를 반환해 감사 추적/UX 피드백에서 왜 보였는지 설명할 수 있게 한다.
    if chunk.workspace_id != query.workspace_id:
        return None
    if chunk.owner_user_id == query.user_id:
        return "owner"
    if chunk.visibility == Visibility.PUBLIC:
        return "public"
    if chunk.visibility == Visibility.DEPARTMENT:
        if set(chunk.department_ids).intersection(query.department_ids):
            return "department_match"
    return None


def _similarity(left: list[float], right: list[float]) -> float:
    # 현재는 내적 기반 유사도만 사용하며, 입력 벡터가 정규화되었음을 전제로 빠른 top-k 정렬을 수행한다.
    return sum(a * b for a, b in zip(left, right))

from __future__ import annotations

from time import perf_counter

from app.models import AnswerCitation, AnswerQuery, AnswerResponse, RetrievalQuery
from app.providers import EmbeddingProvider, FakeLLMProvider, LLMProvider
from app.repository import PolicyRepository
from app.retrieval import RetrievalService


class AnswerService:
    # 검색과 생성형 응답의 결합 지점으로, retrieval 결과를 answer 스냅샷으로 고정하고 토큰/지연 지표를 계산한다.
    def __init__(
        self,
        repository: PolicyRepository,
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider or FakeLLMProvider()

    def answer(self, query: AnswerQuery) -> AnswerResponse:
        started = perf_counter()
        # 답변 계산 전에 retrieval 단계만 먼저 수행해 근거가 없는 상태를 명확히 감지한다.
        retrieval = RetrievalService(
            repository=self.repository,
            embedding_provider=self.embedding_provider,
        ).retrieve(
            RetrievalQuery(
                workspace_id=query.workspace_id,
                user_id=query.user_id,
                department_ids=query.department_ids,
                query=query.query,
                top_k=query.top_k,
                score_threshold=query.score_threshold,
            )
        )

        citations = [
            AnswerCitation(
                rank=result.rank,
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                title=result.title,
                source_uri=result.source_uri,
                quote=result.text,
                score=result.score,
            )
            for result in retrieval.results
        ]

        if not citations:
            # 근거가 없으면 provider 호출 없이 refusal_reason으로 일관된 실패 응답을 반환한다.
            return AnswerResponse(
                query=query.query,
                answer=None,
                citations=[],
                refusal_reason="insufficient_evidence",
                provider=self.llm_provider.provider_name,
                token_count=_estimate_tokens(query.query),
                estimated_cost_usd=0.0,
                latency_ms=_elapsed_ms(started),
                retrieved_count=0,
            )

        prompt = _build_prompt(query.query, citations)
        # answer 생성은 고정된 prompt 포맷을 사용해 근거-문항 연결을 유지한다.
        answer_text = self.llm_provider.complete(prompt)
        return AnswerResponse(
            query=query.query,
            answer=answer_text,
            citations=citations,
            refusal_reason=None,
            provider=self.llm_provider.provider_name,
            token_count=_estimate_tokens(prompt, answer_text),
            estimated_cost_usd=0.0,
            latency_ms=_elapsed_ms(started),
            retrieved_count=len(citations),
        )


def _build_prompt(query: str, citations: list[AnswerCitation]) -> str:
    # 증거 목록을 prompt의 Evidence 블록으로 전달해 LLM이 입력 사실 범위를 벗어나지 않게 유도한다.
    evidence = "\n".join(f"- {citation.quote}" for citation in citations)
    return f"Question: {query}\nEvidence:\n{evidence}\nAnswer with cited evidence only."


def _estimate_tokens(*parts: str) -> int:
    text = " ".join(parts)
    return max(1, (len(text) + 3) // 4)


def _elapsed_ms(started: float) -> int:
    return max(0, int((perf_counter() - started) * 1000))

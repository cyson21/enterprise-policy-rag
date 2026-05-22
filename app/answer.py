from __future__ import annotations

from time import perf_counter

from app.models import AnswerCitation, AnswerQuery, AnswerResponse, RetrievalQuery
from app.providers import EmbeddingProvider, FakeLLMProvider, LLMProvider
from app.repository import PolicyRepository
from app.retrieval import RetrievalService


class AnswerService:
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
    evidence = "\n".join(f"- {citation.quote}" for citation in citations)
    return f"Question: {query}\nEvidence:\n{evidence}\nAnswer with cited evidence only."


def _estimate_tokens(*parts: str) -> int:
    text = " ".join(parts)
    return max(1, (len(text) + 3) // 4)


def _elapsed_ms(started: float) -> int:
    return max(0, int((perf_counter() - started) * 1000))

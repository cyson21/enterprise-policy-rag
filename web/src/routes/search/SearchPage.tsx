import { useEffect, useMemo, useState } from "react";

import { loadAnswer, loadRetrieval, type AnswerResponse, type RetrievalResult } from "../../api/client";
import type { PageProps } from "../../components/layout/AppShell";
import {
  formatAccessReason,
  formatDepartmentIds,
  formatDocumentTitle,
  formatProvider,
  formatRefusalReason,
  formatSourceUri,
  formatUserName,
  formatVisibility,
} from "../../utils/display";

const DEFAULT_QUERY = "보안 사고 발생 시 누구에게 알려야 해?";

export function SearchPage({ workspaceId, activePersona }: PageProps) {
  // 검색 입력값, 조회 결과, 답변, 상세 선택 상태를 분리해 렌더 분기와 재요청 로직을 독립 관리한다.
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [retrieval, setRetrieval] = useState<RetrievalResult[]>([]);
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "empty">("idle");

  // 검색/답변은 동일 query 기준으로 병렬 호출해 응답 갱신 타이밍이 맞도록 맞춘다.
  async function runSearch(nextQuery = query) {
    setStatus("loading");
    const [response, answerResponse] = await Promise.all([
      loadRetrieval({
        workspaceId,
        persona: activePersona,
        query: nextQuery,
        topK: 5,
        scoreThreshold: 0,
      }),
      loadAnswer({
        workspaceId,
        persona: activePersona,
        query: nextQuery,
        topK: 5,
        scoreThreshold: 0,
      }),
    ]);
    setRetrieval(response.results);
    setAnswer(answerResponse);
    setSelectedChunkId(response.results[0]?.chunk_id ?? null);
    setStatus(response.results.length ? "ready" : "empty");
  }

  useEffect(() => {
    void runSearch(DEFAULT_QUERY);
  }, [activePersona.id, workspaceId]);

  // 상세 패널은 현재 선택 chunk 기준, 없으면 첫 번째 결과를 fallback한다.
  const selectedResult = useMemo(
    () => retrieval.find((result) => result.chunk_id === selectedChunkId) ?? retrieval[0],
    [retrieval, selectedChunkId],
  );

  return (
    <section className="screen-grid search-screen">
      <div className="primary-panel">
        <div className="section-heading">
          <span>검색 콘솔</span>
          <h2>정책 질문을 입력하고 현재 권한에서 검색된 근거를 확인합니다.</h2>
        </div>
        <form
          className="search-box"
          onSubmit={(event) => {
            event.preventDefault();
            void runSearch();
          }}
        >
          <input value={query} onChange={(event) => setQuery(event.target.value)} aria-label="데모 질문" />
          <button type="submit">{status === "loading" ? "검색 중" : "검색"}</button>
        </form>

        <div className="result-meta">
          <span>{formatUserName(activePersona.id, activePersona.displayName)}</span>
          <span>{formatDepartmentIds(activePersona.departmentIds)}</span>
          <span>점수 기준 0</span>
        </div>

        {status === "empty" ? (
          <div className="empty-state">현재 사용자 권한에서 검색된 문서가 없습니다.</div>
        ) : (
          retrieval.map((result) => (
            <button
              key={result.chunk_id}
              type="button"
              className={result.chunk_id === selectedResult?.chunk_id ? "result-row is-selected" : "result-row"}
              onClick={() => setSelectedChunkId(result.chunk_id)}
            >
              <span className="rank">{result.rank}</span>
              <div>
                <strong>{formatDocumentTitle(result.title)}</strong>
                <p>{result.text}</p>
                <span className="access-badge">
                  {formatVisibility(result.visibility)} / 접근 사유: {formatAccessReason(result.access_reason)}
                </span>
              </div>
              <span className="score">{result.score.toFixed(2)}</span>
            </button>
          ))
        )}
      </div>
      <aside className="detail-panel">
        <span className="panel-label">근거 기반 답변</span>
        {answer?.answer ? (
          <div className="answer-box">
            <p>{answer.answer}</p>
            <dl className="evidence-list compact">
              <div>
                <dt>제공자</dt>
                <dd>{formatProvider(answer.provider)}</dd>
              </div>
              <div>
                <dt>토큰 수</dt>
                <dd>{answer.token_count}</dd>
              </div>
              <div>
                <dt>예상 비용</dt>
                <dd>${answer.estimated_cost_usd.toFixed(2)}</dd>
              </div>
              <div>
                <dt>인용</dt>
                <dd>{answer.citations.length}</dd>
              </div>
            </dl>
          </div>
        ) : (
          <div className="answer-box">
            <p>{answer?.refusal_reason ? formatRefusalReason(answer.refusal_reason) : "검색을 실행하면 인용 기반 답변이 표시됩니다."}</p>
            <span className="access-badge">거절 사유: {formatRefusalReason(answer?.refusal_reason)}</span>
          </div>
        )}
        <div className="citation-list">
          {answer?.citations.map((citation) => (
            <div key={citation.chunk_id} className="citation-item">
              <strong>{formatDocumentTitle(citation.title)}</strong>
              <span>{citation.score.toFixed(2)}</span>
            </div>
          ))}
        </div>

        <span className="panel-label">근거</span>
        <h3>{selectedResult ? formatDocumentTitle(selectedResult.title) : "권한 내 검색 근거"}</h3>
        {selectedResult ? (
          <>
            <p>{selectedResult.text}</p>
            <dl className="evidence-list">
              <div>
                <dt>출처</dt>
                <dd>{formatSourceUri(selectedResult.source_uri)}</dd>
              </div>
              <div>
                <dt>공개 범위</dt>
                <dd>{formatVisibility(selectedResult.visibility)}</dd>
              </div>
              <div>
                <dt>부서</dt>
                <dd>{formatDepartmentIds(selectedResult.department_ids)}</dd>
              </div>
              <div>
                <dt>접근 사유</dt>
                <dd>{formatAccessReason(selectedResult.access_reason)}</dd>
              </div>
            </dl>
          </>
        ) : (
          <p>검색 결과를 선택하면 출처, 청크, 점수, 접근 사유를 확인할 수 있습니다.</p>
        )}
      </aside>
    </section>
  );
}

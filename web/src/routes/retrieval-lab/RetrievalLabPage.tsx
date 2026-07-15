import { useEffect, useMemo, useState } from "react";

import { loadRetrieval, type RetrievalResult } from "../../api/client";
import type { PageProps } from "../../components/layout/AppShell";
import {
  formatAccessReason,
  formatDepartmentIds,
  formatDocumentTitle,
  formatSourceUri,
  formatUserName,
  formatVisibility,
} from "../../utils/display";

const DEFAULT_LAB_QUERY = "보안 사고 증거 보존";

export function RetrievalLabPage({ workspaceId, activePersona }: PageProps) {
  // 실험 화면은 query/topK/scoreThreshold 상태를 분리해 한 번에 변경해도 조회 로직은 runLabRetrieval에서만 합쳐 처리한다.
  const [query, setQuery] = useState(DEFAULT_LAB_QUERY);
  const [topK, setTopK] = useState(5);
  const [scoreThreshold, setScoreThreshold] = useState(0);
  const [results, setResults] = useState<RetrievalResult[]>([]);
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "empty">("idle");

  // 실험값은 네트워크 호출 전 clamp로 정합화해 서버/UI의 파라미터 범위를 일치시킨다.
  async function runLabRetrieval(nextQuery = query) {
    setStatus("loading");
    const safeTopK = clampTopK(topK);
    const safeScoreThreshold = clampScoreThreshold(scoreThreshold);
    setTopK(safeTopK);
    setScoreThreshold(safeScoreThreshold);
    const response = await loadRetrieval({
      workspaceId,
      persona: activePersona,
      query: nextQuery,
      topK: safeTopK,
      scoreThreshold: safeScoreThreshold,
    });
    setResults(response.results);
    setSelectedChunkId(response.results[0]?.chunk_id ?? null);
    setStatus(response.results.length ? "ready" : "empty");
  }

  useEffect(() => {
    void runLabRetrieval(DEFAULT_LAB_QUERY);
  }, [activePersona.id, workspaceId]);

  const selectedResult = useMemo(
    () => results.find((result) => result.chunk_id === selectedChunkId) ?? results[0],
    [results, selectedChunkId],
  );

  return (
    <section className="screen-grid retrieval-lab-screen">
      <div className="primary-panel">
        <div className="section-heading">
          <span>검색 실험실</span>
          <h2>top-k, 점수 기준, 사용자별 검색 결과를 비교합니다.</h2>
        </div>
        <form
          className="search-box lab-query-form"
          onSubmit={(event) => {
            event.preventDefault();
            void runLabRetrieval();
          }}
        >
          <input value={query} onChange={(event) => setQuery(event.target.value)} aria-label="실험 쿼리" />
          <button type="submit">{status === "loading" ? "실행 중" : "실행"}</button>
        </form>
        <div className="lab-controls">
          <label>
            top-k
            <input
              min="1"
              max="10"
              type="number"
              value={topK}
              onChange={(event) => setTopK(clampTopK(Number(event.target.value)))}
            />
          </label>
          <label>
            점수 기준
            <input
              className="thresholdControl"
              min="-1"
              max="1"
              step="0.05"
              type="range"
              value={scoreThreshold}
              onChange={(event) => setScoreThreshold(clampScoreThreshold(Number(event.target.value)))}
            />
            <output>{scoreThreshold.toFixed(2)}</output>
          </label>
        </div>

        <div className="result-meta">
          <span>{formatUserName(activePersona.id, activePersona.displayName)}</span>
          <span>{formatDepartmentIds(activePersona.departmentIds)}</span>
          <span>top_k {topK}</span>
          <span>점수 기준 {scoreThreshold.toFixed(2)}</span>
        </div>

        {status === "empty" ? (
          <div className="empty-state">현재 설정에서 검색된 chunk가 없습니다.</div>
        ) : (
          results.map((result) => (
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
        <span className="panel-label">검색 디버그</span>
        <h3>{selectedResult ? formatDocumentTitle(selectedResult.title) : "검색 결과를 선택하세요"}</h3>
        {selectedResult ? (
          <dl className="evidence-list">
            <div>
              <dt>청크</dt>
              <dd>{selectedResult.chunk_id}</dd>
            </div>
            <div>
              <dt>문서</dt>
              <dd>{selectedResult.document_id}</dd>
            </div>
            <div>
              <dt>점수</dt>
              <dd>{selectedResult.score.toFixed(6)}</dd>
            </div>
            <div>
              <dt>접근 사유</dt>
              <dd>{formatAccessReason(selectedResult.access_reason)}</dd>
            </div>
            <div>
              <dt>출처</dt>
              <dd>{formatSourceUri(selectedResult.source_uri)}</dd>
            </div>
            <div>
              <dt>부서</dt>
              <dd>{formatDepartmentIds(selectedResult.department_ids)}</dd>
            </div>
          </dl>
        ) : (
          <p>쿼리, top-k, 점수 기준을 조정하면 검색 결과와 권한 메타데이터가 표시됩니다.</p>
        )}
      </aside>
    </section>
  );
}

function clampTopK(value: number) {
  // top_k는 1~10 범위의 정수만 허용해 의도하지 않은 소수값을 정리한다.
  if (!Number.isFinite(value)) {
    return 5;
  }
  return Math.min(10, Math.max(1, Math.round(value)));
}

function clampScoreThreshold(value: number) {
  // 정규화된 내적 기반 점수 임계값은 [-1,1]로 고정해 서버 검증 범위와 맞춘다.
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.min(1, Math.max(-1, value));
}

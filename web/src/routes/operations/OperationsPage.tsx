import { useEffect, useState } from "react";

import {
  loadEvalRuns,
  loadOperationsSummary,
  loadQueryDetail,
  loadQueryTrend,
  loadRecentQueries,
  loadTopEvidence,
  type EvalRun,
  type MetricsSummary,
  type QueryDetailResponse,
  type QueryTrendPoint,
  type RecentQuery,
  type TopEvidenceItem,
} from "../../api/client";
import type { PageProps } from "../../components/layout/AppShell";
import {
  formatAccessReason,
  formatDocumentIds,
  formatDocumentTitle,
  formatMode,
  formatProvider,
  formatQuery,
  formatUserName,
} from "../../utils/display";

export function OperationsPage({ workspaceId }: PageProps) {
  // 지표 페이지는 여러 API를 병렬로 조회해 한 번의 렌더 사이클에서 화면을 갱신한다.
  const [summary, setSummary] = useState<MetricsSummary | null>(null);
  const [trend, setTrend] = useState<QueryTrendPoint[]>([]);
  const [queries, setQueries] = useState<RecentQuery[]>([]);
  const [selectedQueryId, setSelectedQueryId] = useState<string | null>(null);
  const [queryDetail, setQueryDetail] = useState<QueryDetailResponse | null>(null);
  const [topEvidence, setTopEvidence] = useState<TopEvidenceItem[]>([]);
  const [evalRun, setEvalRun] = useState<EvalRun | null>(null);

  // 운영 지표는 Promise.all로 동시 로딩해 화면 깜빡임을 줄이고 집계 기준을 맞춘다.
  useEffect(() => {
    async function fetchOperations() {
      const [summaryResponse, trendResponse, queriesResponse, topEvidenceResponse, evalRunsResponse] = await Promise.all([
        loadOperationsSummary(workspaceId),
        loadQueryTrend(workspaceId),
        loadRecentQueries(workspaceId),
        loadTopEvidence(workspaceId),
        loadEvalRuns(workspaceId),
      ]);
      setSummary(summaryResponse);
      setTrend(trendResponse.points);
      setQueries(queriesResponse.queries);
      setSelectedQueryId((current) =>
        current && queriesResponse.queries.some((query) => query.id === current)
          ? current
          : queriesResponse.queries[0]?.id ?? null,
      );
      setTopEvidence(topEvidenceResponse.items);
      setEvalRun(evalRunsResponse.runs[0] ?? null);
    }

    void fetchOperations();
  }, [workspaceId]);

  useEffect(() => {
    let active = true;
    if (!selectedQueryId) {
      setQueryDetail(null);
      return () => {
        active = false;
      };
    }
    const queryId = selectedQueryId;

    async function fetchQueryDetail() {
      const response = await loadQueryDetail(workspaceId, queryId);
      if (active) {
        setQueryDetail(response);
      }
    }

    void fetchQueryDetail();
    return () => {
      active = false;
    };
  }, [selectedQueryId, workspaceId]);

  const metrics = summary ?? {
    workspace_id: workspaceId,
    searches: 0,
    p95_latency_ms: 0,
    estimated_cost_usd: 0,
    retrieval_hit_rate: 0,
    zero_result_rate: 0,
    provider: "fake",
  };
  const screenshotMode =
    typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("focus") : null;
  // screenshot 모드에서는 상세/요약 탭이 화면 축약되어 캡처 대상만 보이게 분기된다.
  const screenshotFocus = screenshotMode === "query-detail";
  const screenshotSummary = screenshotMode === "mobile-summary";

  return (
    <section
      className={[
        "page-section",
        screenshotFocus ? "screenshot-focus-detail" : "",
        screenshotSummary ? "screenshot-focus-summary" : "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="section-heading">
        <span>운영 지표</span>
        <h2>쿼리 로그, 지연 시간, 비용 추정, 검색 지표를 확인합니다.</h2>
      </div>
      <div className="metric-grid">
        <div className="metric-card">
          <span>검색 수</span>
          <strong>{metrics.searches}</strong>
        </div>
        <div className="metric-card">
          <span>p95 지연 시간</span>
          <strong>{metrics.p95_latency_ms}ms</strong>
        </div>
        <div className="metric-card">
          <span>예상 비용</span>
          <strong>${metrics.estimated_cost_usd.toFixed(2)}</strong>
        </div>
        <div className="metric-card">
          <span>검색 적중률</span>
          <strong>{formatPercent(metrics.retrieval_hit_rate)}</strong>
        </div>
      </div>

      <div className="result-meta">
        <span>{metrics.workspace_id}</span>
        <span>{formatProvider(metrics.provider)}</span>
        <span>무결과율 {formatPercent(metrics.zero_result_rate)}</span>
      </div>

      <div className="operations-console">
        <div className="operations-main">
          <div className="section-heading table-section-heading">
            <span>쿼리 추세</span>
            <h2>일별 검색과 답변량</h2>
          </div>
          <div className="data-table trend-table">
            <div className="table-row table-head">
              <span>날짜</span>
              <span>검색</span>
              <span>답변</span>
              <span>무결과</span>
              <span>평균 지연</span>
            </div>
            {trend.map((point) => (
              <div key={point.date} className="table-row">
                <span>
                  <strong>{point.date}</strong>
                  <small>쿼리 추세</small>
                </span>
                <span>{point.retrieval_count}</span>
                <span>{point.answer_count}</span>
                <span>{point.zero_result_count}</span>
                <span>{point.avg_latency_ms}ms</span>
              </div>
            ))}
          </div>

          <div className="section-heading table-section-heading">
            <span>최근 쿼리</span>
            <h2>검색과 답변 쿼리 행</h2>
          </div>
          <div className="data-table query-table">
            <div className="table-row table-head">
              <span>쿼리</span>
              <span>사용자</span>
              <span>지연</span>
              <span>결과</span>
              <span>최고 점수</span>
            </div>
            {queries.map((query) => (
              <button
                key={query.id}
                type="button"
                className={`table-row query-row ${selectedQueryId === query.id ? "is-selected" : ""}`}
                onClick={() => setSelectedQueryId(query.id)}
              >
                <span>
                  <strong>{formatQuery(query.query)}</strong>
                  <small>{formatMode(query.mode)}</small>
                </span>
                <span>{formatUserName(query.user_id)}</span>
                <span>{query.latency_ms}ms</span>
                <span>{query.retrieved_count}</span>
                <span>{query.top_score.toFixed(2)}</span>
              </button>
            ))}
          </div>
        </div>

        <aside className="operations-detail-panel query-detail">
          <div className="section-heading">
            <span>쿼리 상세</span>
            <h2>선택한 쿼리의 근거와 인용 스냅샷</h2>
          </div>
          {queryDetail ? (
            <>
              <div className="result-meta">
                <span>{queryDetail.query.id}</span>
                <span>{formatMode(queryDetail.query.mode)}</span>
                <span>{formatUserName(queryDetail.query.user_id)}</span>
                <span>{queryDetail.query.latency_ms}ms</span>
              </div>
              {queryDetail.answer ? (
                <div className="answer-box">
                  <strong>저장된 답변</strong>
                  <p>{queryDetail.answer.answer ?? queryDetail.answer.refusal_reason}</p>
                  <small>
                    {formatProvider(queryDetail.answer.provider)} / {queryDetail.answer.token_count} 토큰 / $
                    {queryDetail.answer.estimated_cost_usd.toFixed(2)}
                  </small>
                </div>
              ) : null}
              <div className="detail-list-title">저장된 근거</div>
              <div className="detail-list">
                {queryDetail.retrieval_results.map((item) => (
                  <div key={`${item.chunk_id}-${item.rank}`} className="detail-list-row">
                    <span>#{item.rank}</span>
                    <strong>{formatDocumentTitle(item.title)}</strong>
                    <small>
                      {formatAccessReason(item.access_reason)} / {item.score.toFixed(2)}
                    </small>
                  </div>
                ))}
                {queryDetail.retrieval_results.length === 0 ? (
                  <div className="empty-state">이 쿼리에 저장된 검색 스냅샷이 없습니다.</div>
                ) : null}
              </div>
              <div className="detail-list-title detail-list-title-spaced">인용 스냅샷</div>
              <div className="detail-list">
                {queryDetail.citations.map((item) => (
                  <div key={`${item.chunk_id}-${item.rank}`} className="detail-list-row">
                    <span>#{item.rank}</span>
                    <strong>{formatDocumentTitle(item.title)}</strong>
                    <small>{item.quote}</small>
                  </div>
                ))}
                {queryDetail.citations.length === 0 ? (
                  <div className="empty-state">이 쿼리에 저장된 인용 스냅샷이 없습니다.</div>
                ) : null}
              </div>
            </>
          ) : (
            <div className="empty-state">저장된 근거를 보려면 쿼리 행을 선택하세요.</div>
          )}
        </aside>
      </div>

      <div className="section-heading table-section-heading">
        <span>주요 근거 문서</span>
        <h2>검색 결과와 답변 인용</h2>
      </div>
      <div className="data-table evidence-table">
        <div className="table-row table-head">
          <span>문서</span>
          <span>검색</span>
          <span>인용</span>
          <span>평균 점수</span>
        </div>
        {topEvidence.map((item) => (
          <div key={item.document_id} className="table-row">
            <span>
              <strong>{formatDocumentTitle(item.title)}</strong>
              <small>{item.source_uri ?? item.document_id}</small>
            </span>
            <span>{item.retrieval_count}</span>
            <span>{item.citation_count}</span>
            <span>{item.avg_score.toFixed(2)}</span>
          </div>
        ))}
      </div>

      <div className="section-heading table-section-heading">
        <span>평가 리포트</span>
        <h2>golden-demo 검색과 인용 점검</h2>
      </div>
      <div className="metric-grid eval-summary-grid">
        <div className="metric-card">
          <span>검색 적중</span>
          <strong>{formatPercent(evalRun?.retrieval_hit_rate ?? 0)}</strong>
        </div>
        <div className="metric-card">
          <span>인용 커버리지</span>
          <strong>{formatPercent(evalRun?.citation_coverage ?? 0)}</strong>
        </div>
        <div className="metric-card">
          <span>케이스</span>
          <strong>{evalRun?.case_count ?? 0}</strong>
        </div>
        <div className="metric-card">
          <span>제공자</span>
          <strong>{formatProvider(evalRun?.provider ?? "fake")}</strong>
        </div>
      </div>
      <div className="data-table eval-table">
        <div className="table-row table-head">
          <span>케이스</span>
          <span>사용자</span>
          <span>기대 문서</span>
          <span>검색</span>
          <span>인용</span>
        </div>
        {evalRun?.cases.map((item) => (
          <div key={item.case_id} className="table-row">
            <span>
              <strong>{item.case_id}</strong>
              <small>{formatQuery(item.question)}</small>
            </span>
            <span>{formatUserName(item.user_id)}</span>
            <span>{formatDocumentIds(item.expected_document_ids)}</span>
            <span>{item.retrieval_hit ? "적중" : "누락"}</span>
            <span>{item.citation_covered ? "충족" : "부족"}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function formatPercent(value: number) {
  // 운영 지표는 0~1 범위의 비율을 퍼센트 문자열로 통일해 표시한다.
  return `${Math.round(value * 100)}%`;
}

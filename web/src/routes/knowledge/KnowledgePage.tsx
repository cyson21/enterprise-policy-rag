import { useEffect, useMemo, useState } from "react";

import {
  loadDocumentDetail,
  loadDocuments,
  type DocumentDetailResponse,
  type DocumentSummary,
} from "../../api/client";
import type { PageProps } from "../../components/layout/AppShell";
import {
  formatDepartmentIds,
  formatDocumentTitle,
  formatIndexingStatus,
  formatSourceUri,
  formatUserName,
  formatVisibility,
} from "../../utils/display";

export function KnowledgePage({ workspaceId }: PageProps) {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [detail, setDetail] = useState<DocumentDetailResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "empty">("loading");

  useEffect(() => {
    async function fetchDocuments() {
      setStatus("loading");
      const response = await loadDocuments(workspaceId);
      setDocuments(response.documents);
      setSelectedDocumentId((current) => {
        if (current && response.documents.some((document) => document.id === current)) {
          return current;
        }
        return response.documents[0]?.id ?? null;
      });
      setStatus(response.documents.length ? "ready" : "empty");
    }

    void fetchDocuments();
  }, [workspaceId]);

  useEffect(() => {
    async function fetchDetail() {
      if (!selectedDocumentId) {
        setDetail(null);
        return;
      }
      const response = await loadDocumentDetail(workspaceId, selectedDocumentId);
      setDetail(response);
    }

    void fetchDetail();
  }, [selectedDocumentId, workspaceId]);

  const selectedDocument = useMemo(
    () => documents.find((document) => document.id === selectedDocumentId) ?? detail?.document ?? documents[0],
    [detail?.document, documents, selectedDocumentId],
  );

  return (
    <section className="screen-grid knowledge-screen">
      <div className="primary-panel">
        <div className="section-heading">
          <span>지식 라이브러리</span>
          <h2>문서, 청크, 공개 범위, 부서 상태를 실제 API 데이터로 확인합니다.</h2>
        </div>
        <div className="result-meta">
          <span>{workspaceId}</span>
          <span>{documents.length}개 문서</span>
          <span>{documents.reduce((sum, document) => sum + document.chunk_count, 0)}개 청크</span>
        </div>

        <div className="data-table document-table">
          <div className="table-row table-head">
            <span>문서</span>
            <span>공개 범위</span>
            <span>인덱싱 상태</span>
            <span>부서</span>
            <span>청크</span>
          </div>

          {status === "empty" ? (
            <div className="empty-state">등록된 문서가 없습니다.</div>
          ) : (
            documents.map((document) => (
              <button
                key={document.id}
                type="button"
                className={document.id === selectedDocument?.id ? "table-row document-row is-selected" : "table-row document-row"}
                onClick={() => setSelectedDocumentId(document.id)}
              >
                <span>
                  <strong>{formatDocumentTitle(document.title)}</strong>
                  <small>{formatSourceUri(document.source_uri)}</small>
                </span>
                <span>{formatVisibility(document.visibility)}</span>
                <span>{formatIndexingStatus(document.indexing_status)}</span>
                <span>{formatDepartmentIds(document.department_ids)}</span>
                <span>{document.chunk_count}</span>
              </button>
            ))
          )}
        </div>
      </div>

      <aside className="detail-panel">
        <span className="panel-label">문서 상세</span>
        <h3>{selectedDocument ? formatDocumentTitle(selectedDocument.title) : "문서를 선택하세요"}</h3>
        {detail ? (
          <>
            <dl className="evidence-list">
              <div>
                <dt>인덱싱 상태</dt>
                <dd>{formatIndexingStatus(detail.document.indexing_status)}</dd>
              </div>
              <div>
                <dt>소유자</dt>
                <dd>{formatUserName(detail.document.owner_user_id)}</dd>
              </div>
              <div>
                <dt>콘텐츠 유형</dt>
                <dd>{detail.document.content_type}</dd>
              </div>
              <div>
                <dt>출처</dt>
                <dd>{formatSourceUri(detail.document.source_uri)}</dd>
              </div>
            </dl>

            <div className="chunk-list" aria-label="문서 청크">
              {detail.chunks.map((chunk) => (
                <article key={chunk.id} className="chunk-preview">
                  <div>
                    <strong>청크 {chunk.chunk_index + 1}</strong>
                    <span>임베딩 차원 {chunk.embedding_dimensions}</span>
                  </div>
                  <p>{chunk.text}</p>
                </article>
              ))}
            </div>
          </>
        ) : (
          <p>{status === "loading" ? "문서 목록을 불러오는 중입니다." : "상세로 볼 문서를 선택하세요."}</p>
        )}
      </aside>
    </section>
  );
}

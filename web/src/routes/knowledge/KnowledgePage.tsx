import { useEffect, useMemo, useState } from "react";
import { RefreshCw, Save, Trash2 } from "lucide-react";

import {
  deleteAdminDocument,
  loadAdminAuditLogs,
  loadDocumentDetail,
  loadDocuments,
  updateAdminDocument,
  type AdminAuditLog,
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

export function KnowledgePage({ workspaceId, activePersona }: PageProps) {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [detail, setDetail] = useState<DocumentDetailResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "empty">("loading");
  const [adminTitle, setAdminTitle] = useState("");
  const [adminContent, setAdminContent] = useState("");
  const [adminVisibility, setAdminVisibility] = useState<DocumentSummary["visibility"]>("public");
  const [adminDepartments, setAdminDepartments] = useState("");
  const [adminLogs, setAdminLogs] = useState<AdminAuditLog[]>([]);
  const [adminStatus, setAdminStatus] = useState("관리 작업 대기 중");
  const [adminBusy, setAdminBusy] = useState(false);
  const isAdmin = activePersona.role === "admin";

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

  useEffect(() => {
    if (!detail) {
      setAdminTitle("");
      setAdminContent("");
      setAdminVisibility("public");
      setAdminDepartments("");
      return;
    }

    setAdminTitle(detail.document.title);
    setAdminContent(detail.chunks.map((chunk) => chunk.text).join("\n\n"));
    setAdminVisibility(detail.document.visibility);
    setAdminDepartments(detail.document.department_ids.join(", "));
  }, [detail]);

  useEffect(() => {
    if (!isAdmin) {
      setAdminLogs([]);
      setAdminStatus("관리 작업은 admin role에서만 활성화됩니다.");
      return;
    }

    void refreshAuditLogs();
  }, [activePersona.id, isAdmin]);

  const selectedDocument = useMemo(
    () => documents.find((document) => document.id === selectedDocumentId) ?? detail?.document ?? documents[0],
    [detail?.document, documents, selectedDocumentId],
  );

  async function refreshAuditLogs(nextStatus?: string) {
    if (!isAdmin) {
      return;
    }

    try {
      const response = await loadAdminAuditLogs(activePersona);
      setAdminLogs(response.logs);
      setAdminStatus(nextStatus ?? (response.logs.length ? "감사 로그를 불러왔습니다." : "감사 로그가 없습니다."));
    } catch (error) {
      setAdminStatus(error instanceof Error ? error.message : "감사 로그를 불러오지 못했습니다.");
    }
  }

  async function handleAdminUpdate() {
    if (!isAdmin || !detail || adminBusy) {
      return;
    }

    const title = adminTitle.trim();
    const content = adminContent.trim();
    if (!title || !content) {
      setAdminStatus("문서명과 본문을 입력하세요.");
      return;
    }

    setAdminBusy(true);
    setAdminStatus("문서를 업데이트하는 중입니다.");
    try {
      const response = await updateAdminDocument({
        documentId: detail.document.id,
        persona: activePersona,
        payload: {
          title,
          content,
          content_type: detail.document.content_type,
          department_ids: splitDepartments(adminDepartments),
          visibility: adminVisibility,
        },
      });
      setDocuments((current) =>
        current.map((document) => (document.id === response.document.id ? response.document : document)),
      );
      setDetail((current) =>
        current
          ? {
              ...current,
              document: response.document,
              chunks: current.chunks.length
                ? current.chunks.map((chunk, index) => ({
                    ...chunk,
                    text: index === 0 ? content : chunk.text,
                    embedding_dimensions: chunk.embedding_dimensions,
                  }))
                : [
                    {
                      id: `${response.document.id}-chunk-1`,
                      document_id: response.document.id,
                      workspace_id: response.document.workspace_id,
                      chunk_index: 0,
                      text: content,
                      embedding_dimensions: 32,
                    },
                  ],
            }
          : current,
      );
      await refreshAuditLogs(`문서 업데이트 완료: ${response.chunk_count}개 청크`);
    } catch (error) {
      setAdminStatus(error instanceof Error ? error.message : "문서 업데이트에 실패했습니다.");
    } finally {
      setAdminBusy(false);
    }
  }

  async function handleAdminDelete() {
    if (!isAdmin || !detail || adminBusy) {
      return;
    }

    setAdminBusy(true);
    setAdminStatus("문서를 삭제하는 중입니다.");
    try {
      const deletedId = detail.document.id;
      await deleteAdminDocument({ documentId: deletedId, persona: activePersona });
      const remainingDocuments = documents.filter((document) => document.id !== deletedId);
      setDocuments(remainingDocuments);
      setSelectedDocumentId(remainingDocuments[0]?.id ?? null);
      setDetail(null);
      await refreshAuditLogs("문서 삭제 완료");
    } catch (error) {
      setAdminStatus(error instanceof Error ? error.message : "문서 삭제에 실패했습니다.");
    } finally {
      setAdminBusy(false);
    }
  }

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

            <section className="admin-controls" aria-label="관리 작업">
              <div className="admin-heading">
                <div>
                  <span className="panel-label">관리 작업</span>
                  <h4>{isAdmin ? "문서 운영 제어" : "읽기 전용"}</h4>
                </div>
              </div>

              {isAdmin ? (
                <>
                  <label>
                    문서명
                    <input value={adminTitle} onChange={(event) => setAdminTitle(event.target.value)} />
                  </label>
                  <label>
                    공개 범위
                    <select
                      value={adminVisibility}
                      onChange={(event) => setAdminVisibility(event.target.value as DocumentSummary["visibility"])}
                    >
                      <option value="public">public</option>
                      <option value="department">department</option>
                      <option value="private">private</option>
                    </select>
                  </label>
                  <label>
                    부서
                    <input
                      value={adminDepartments}
                      onChange={(event) => setAdminDepartments(event.target.value)}
                      placeholder="security, platform"
                    />
                  </label>
                  <label>
                    본문
                    <textarea value={adminContent} onChange={(event) => setAdminContent(event.target.value)} />
                  </label>
                  <div className="admin-actions">
                    <button type="button" onClick={() => void handleAdminUpdate()} disabled={adminBusy}>
                      <Save size={15} aria-hidden="true" />
                      문서 업데이트
                    </button>
                    <button
                      type="button"
                      className="danger"
                      onClick={() => void handleAdminDelete()}
                      disabled={adminBusy}
                    >
                      <Trash2 size={15} aria-hidden="true" />
                      문서 삭제
                    </button>
                  </div>
                </>
              ) : (
                <p>관리 작업은 admin role에서만 활성화됩니다.</p>
              )}

              <div className="admin-audit">
                <div className="admin-audit-head">
                  <h4>감사 로그</h4>
                  {isAdmin ? (
                    <button type="button" onClick={() => void refreshAuditLogs()} disabled={adminBusy}>
                      <RefreshCw size={15} aria-hidden="true" />
                      새로고침
                    </button>
                  ) : null}
                </div>
                <p className="admin-status">{adminStatus}</p>
                {adminLogs.length ? (
                  <ul>
                    {adminLogs.slice(0, 3).map((log) => (
                      <li key={log.id}>
                        <strong>{formatAdminAction(log.action)}</strong>
                        <span>{formatUserName(log.actor_user_id)}</span>
                        <small>{auditDocumentTitle(log)}</small>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            </section>
          </>
        ) : (
          <p>{status === "loading" ? "문서 목록을 불러오는 중입니다." : "상세로 볼 문서를 선택하세요."}</p>
        )}
      </aside>
    </section>
  );
}

function splitDepartments(value: string) {
  return Array.from(
    new Set(
      value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    ),
  ).sort();
}

function formatAdminAction(action: string) {
  if (action === "document.updated") {
    return "문서 업데이트";
  }
  if (action === "document.deleted") {
    return "문서 삭제";
  }
  return action;
}

function auditDocumentTitle(log: AdminAuditLog) {
  const title = log.details.title;
  if (typeof title === "string" && title.trim()) {
    return formatDocumentTitle(title);
  }
  return log.document_id ?? "문서 ID 없음";
}

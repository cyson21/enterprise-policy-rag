"""문서 저장소 경계 모듈.

도메인 서비스는 인터페이스를 통해 repository를 호출하고,
구현체는 메모리/DB 영속 방식만 교체한다.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

from app.chunking import TextChunk
from app.models import (
    AdminAuditLogCreate,
    DocumentCreate,
    IndexingStatus,
    StoredAdminAuditLog,
    StoredChunk,
    StoredDocument,
    Visibility,
)

try:
    import psycopg
    from psycopg.rows import dict_row
except ModuleNotFoundError:
    psycopg = None
    dict_row = None


class PolicyRepository(Protocol):
    def add_document(
        self,
        document: DocumentCreate,
        chunks: Sequence[TextChunk],
        embeddings: Sequence[list[float]],
    ) -> StoredDocument:
        """Persist one document and its chunks."""

    def list_chunks(self, workspace_id: str) -> list[StoredChunk]:
        """Return retrieval-ready chunks for one workspace."""

    def search_candidate_chunks(
        self,
        workspace_id: str,
        query_embedding: list[float],
        *,
        owner_user_id: str,
        department_ids: Sequence[str],
        limit: int,
    ) -> list[StoredChunk]:
        """Return permission-filtered retrieval candidates ordered by vector similarity."""

    def list_documents(self, workspace_id: str) -> list[StoredDocument]:
        """Return documents for one workspace."""

    def get_document(self, workspace_id: str, document_id: str) -> StoredDocument | None:
        """Return one document if it belongs to the workspace."""

    def list_document_chunks(self, workspace_id: str, document_id: str) -> list[StoredChunk]:
        """Return chunks for one document if it belongs to the workspace."""

    def update_document(
        self,
        document_id: str,
        document: DocumentCreate,
        chunks: Sequence[TextChunk],
        embeddings: Sequence[list[float]],
    ) -> StoredDocument | None:
        """Replace document metadata and chunks if it belongs to the workspace."""

    def delete_document(self, workspace_id: str, document_id: str) -> StoredDocument | None:
        """Delete one document and its chunks if it belongs to the workspace."""

    def add_admin_audit_log(self, log: AdminAuditLogCreate) -> StoredAdminAuditLog:
        """Append an admin audit log entry."""

    def list_admin_audit_logs(self, workspace_id: str, limit: int | None = None) -> list[StoredAdminAuditLog]:
        """Return recent admin audit log entries."""


class InMemoryPolicyRepository:
    """테스트/데모에서 쓰는 인메모리 저장소 구현체."""

    def __init__(self) -> None:
        self._document_sequence = 0
        self._chunk_sequence = 0
        self._audit_log_sequence = 0
        self._documents: dict[str, StoredDocument] = {}
        self._chunks: dict[str, StoredChunk] = {}
        self._audit_logs: list[StoredAdminAuditLog] = []

    def add_document(
        self,
        document: DocumentCreate,
        chunks: Sequence[TextChunk],
        embeddings: Sequence[list[float]],
    ) -> StoredDocument:
        # 문서와 임베딩 개수가 다르면 저장 상태를 만들지 못하게 해 검색 품질을 깨지 않는다.
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")

        self._document_sequence += 1
        document_id = f"doc_{self._document_sequence}"
        stored = StoredDocument(
            id=document_id,
            workspace_id=document.workspace_id,
            title=document.title,
            source_uri=document.source_uri,
            content_type=document.content_type,
            owner_user_id=document.owner_user_id,
            department_ids=document.department_ids,
            visibility=document.visibility,
            indexing_status=IndexingStatus.READY,
        )
        self._documents[document_id] = stored

        for chunk, embedding in zip(chunks, embeddings):
            self._chunk_sequence += 1
            chunk_id = f"chunk_{self._chunk_sequence}"
            self._chunks[chunk_id] = StoredChunk(
                id=chunk_id,
                document_id=document_id,
                workspace_id=stored.workspace_id,
                title=stored.title,
                source_uri=stored.source_uri,
                owner_user_id=stored.owner_user_id,
                department_ids=stored.department_ids,
                visibility=stored.visibility,
                chunk_index=chunk.index,
                text=chunk.text,
                embedding=embedding,
            )

        return stored

    def list_chunks(self, workspace_id: str) -> list[StoredChunk]:
        # 검색 경로에서 workspace 경계를 먼저 적용해 cross-workspace 노출을 원천 차단한다.
        return [chunk for chunk in self._chunks.values() if chunk.workspace_id == workspace_id]

    def search_candidate_chunks(
        self,
        workspace_id: str,
        query_embedding: list[float],
        *,
        owner_user_id: str,
        department_ids: Sequence[str],
        limit: int,
    ) -> list[StoredChunk]:
        departments = set(department_ids)
        candidates = [
            chunk
            for chunk in self.list_chunks(workspace_id)
            if (
                chunk.owner_user_id == owner_user_id
                or chunk.visibility == Visibility.PUBLIC
                or (chunk.visibility == Visibility.DEPARTMENT and departments.intersection(chunk.department_ids))
            )
        ]
        candidates.sort(
            key=lambda chunk: (
                -_similarity(query_embedding, chunk.embedding),
                chunk.document_id,
                chunk.chunk_index,
                chunk.id,
            )
        )
        return candidates[: max(0, limit)]

    def list_documents(self, workspace_id: str) -> list[StoredDocument]:
        # 문서 목록도 workspace_id 기준으로만 노출해 관리자 UI가 서로 다른 조직 상태를 섞어보지 않게 한다.
        return [document for document in self._documents.values() if document.workspace_id == workspace_id]

    def get_document(self, workspace_id: str, document_id: str) -> StoredDocument | None:
        document = self._documents.get(document_id)
        if document is None or document.workspace_id != workspace_id:
            return None
        return document

    def list_document_chunks(self, workspace_id: str, document_id: str) -> list[StoredChunk]:
        # 문서 단위로 청크를 조회할 때 doc_id와 workspace_id를 모두 검사해 참조 경계를 유지한다.
        return [
            chunk
            for chunk in self._chunks.values()
            if chunk.workspace_id == workspace_id and chunk.document_id == document_id
        ]

    def update_document(
        self,
        document_id: str,
        document: DocumentCreate,
        chunks: Sequence[TextChunk],
        embeddings: Sequence[list[float]],
    ) -> StoredDocument | None:
        # 기존 문서를 대체할 때는 기존 청크를 지우고 동일 인덱스 순서로 재생성해 추후 접근 제어 계산이 일관되게 돌아간다.
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        existing = self.get_document(workspace_id=document.workspace_id, document_id=document_id)
        if existing is None:
            return None

        stored = StoredDocument(
            id=document_id,
            workspace_id=document.workspace_id,
            title=document.title,
            source_uri=document.source_uri,
            content_type=document.content_type,
            owner_user_id=document.owner_user_id,
            department_ids=document.department_ids,
            visibility=document.visibility,
            indexing_status=IndexingStatus.READY,
        )
        self._documents[document_id] = stored
        self._chunks = {
            chunk_id: chunk
            for chunk_id, chunk in self._chunks.items()
            if not (chunk.workspace_id == document.workspace_id and chunk.document_id == document_id)
        }

        for chunk, embedding in zip(chunks, embeddings):
            self._chunk_sequence += 1
            chunk_id = f"chunk_{self._chunk_sequence}"
            self._chunks[chunk_id] = StoredChunk(
                id=chunk_id,
                document_id=document_id,
                workspace_id=stored.workspace_id,
                title=stored.title,
                source_uri=stored.source_uri,
                owner_user_id=stored.owner_user_id,
                department_ids=stored.department_ids,
                visibility=stored.visibility,
                chunk_index=chunk.index,
                text=chunk.text,
                embedding=embedding,
            )
        return stored

    def delete_document(self, workspace_id: str, document_id: str) -> StoredDocument | None:
        # 문서 삭제 시 청크도 같이 제거해 조회 경로에서 고아 청크를 만들지 않는다.
        existing = self.get_document(workspace_id=workspace_id, document_id=document_id)
        if existing is None:
            return None
        del self._documents[document_id]
        self._chunks = {
            chunk_id: chunk
            for chunk_id, chunk in self._chunks.items()
            if not (chunk.workspace_id == workspace_id and chunk.document_id == document_id)
        }
        return existing

    def add_admin_audit_log(self, log: AdminAuditLogCreate) -> StoredAdminAuditLog:
        self._audit_log_sequence += 1
        stored = StoredAdminAuditLog(
            id=f"audit_{self._audit_log_sequence}",
            workspace_id=log.workspace_id,
            actor_user_id=log.actor_user_id,
            action=log.action,
            document_id=log.document_id,
            details=log.details,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._audit_logs.append(stored)
        return stored

    def list_admin_audit_logs(self, workspace_id: str, limit: int | None = None) -> list[StoredAdminAuditLog]:
        logs = [log for log in reversed(self._audit_logs) if log.workspace_id == workspace_id]
        return logs[:limit] if limit is not None else logs


class PostgresPolicyRepository:
    """PostgreSQL + pgvector repository for the retrieval core."""

    def __init__(self, dsn: str | None = None, connection: Any | None = None) -> None:
        if connection is None:
            if psycopg is None:
                raise RuntimeError("psycopg is required to use PostgresPolicyRepository")
            connection = psycopg.connect(dsn)
        self._connection = connection

    def add_document(
        self,
        document: DocumentCreate,
        chunks: Sequence[TextChunk],
        embeddings: Sequence[list[float]],
    ) -> StoredDocument:
        # DB 경로는 문서 본문과 벡터를 같은 흐름으로 넣어 검색 인덱스 일관성을 보장한다.
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")

        document_id = f"doc_{uuid4().hex}"
        stored = StoredDocument(
            id=document_id,
            workspace_id=document.workspace_id,
            title=document.title,
            source_uri=document.source_uri,
            content_type=document.content_type,
            owner_user_id=document.owner_user_id,
            department_ids=document.department_ids,
            visibility=document.visibility,
            indexing_status=IndexingStatus.READY,
        )

        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO workspaces (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (document.workspace_id, document.workspace_id),
            )
            cursor.execute(
                """
                INSERT INTO documents (
                    id, workspace_id, title, source_uri, content_type,
                    owner_user_id, department_ids, visibility, indexing_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    stored.id,
                    stored.workspace_id,
                    stored.title,
                    stored.source_uri,
                    stored.content_type,
                    stored.owner_user_id,
                    stored.department_ids,
                    stored.visibility.value,
                    stored.indexing_status.value,
                ),
            )

            for chunk, embedding in zip(chunks, embeddings):
                cursor.execute(
                    """
                    INSERT INTO document_chunks (
                        id, document_id, workspace_id, chunk_index, text, embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        f"chunk_{uuid4().hex}",
                        stored.id,
                        stored.workspace_id,
                        chunk.index,
                        chunk.text,
                        _vector_literal(embedding),
                    ),
                )
        self._connection.commit()
        return stored

    def list_chunks(self, workspace_id: str) -> list[StoredChunk]:
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.id,
                    c.document_id,
                    c.workspace_id,
                    d.title,
                    d.source_uri,
                    d.owner_user_id,
                    d.department_ids,
                    d.visibility,
                    d.indexing_status,
                    c.chunk_index,
                    c.text,
                    c.embedding
                FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.workspace_id = %s
                ORDER BY c.document_id, c.chunk_index, c.id
                """,
                (workspace_id,),
            )
            return [_chunk_from_row(row) for row in cursor.fetchall()]

    def search_candidate_chunks(
        self,
        workspace_id: str,
        query_embedding: list[float],
        *,
        owner_user_id: str,
        department_ids: Sequence[str],
        limit: int,
    ) -> list[StoredChunk]:
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.id,
                    c.document_id,
                    c.workspace_id,
                    d.title,
                    d.source_uri,
                    d.owner_user_id,
                    d.department_ids,
                    d.visibility,
                    d.indexing_status,
                    c.chunk_index,
                    c.text,
                    c.embedding
                FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.workspace_id = %s
                  AND (
                    d.owner_user_id = %s
                    OR d.visibility = 'public'
                    OR (d.visibility = 'department' AND d.department_ids && %s::text[])
                  )
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    workspace_id,
                    owner_user_id,
                    list(department_ids),
                    _vector_literal(query_embedding),
                    max(0, limit),
                ),
            )
            return [_chunk_from_row(row) for row in cursor.fetchall()]

    def list_documents(self, workspace_id: str) -> list[StoredDocument]:
        # 문서 조회 쿼리에서 chunk_count를 집계해 별도 count API 없이 summary를 즉시 구성한다.
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.workspace_id,
                    d.title,
                    d.source_uri,
                    d.content_type,
                    d.owner_user_id,
                    d.department_ids,
                    d.visibility,
                    d.indexing_status,
                    COUNT(c.id) AS chunk_count
                FROM documents d
                LEFT JOIN document_chunks c ON c.document_id = d.id
                WHERE d.workspace_id = %s
                GROUP BY d.id
                ORDER BY d.id
                """,
                (workspace_id,),
            )
            return [_document_from_row(row) for row in cursor.fetchall()]

    def get_document(self, workspace_id: str, document_id: str) -> StoredDocument | None:
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    workspace_id,
                    title,
                    source_uri,
                    content_type,
                    owner_user_id,
                    department_ids,
                    visibility,
                    indexing_status
                FROM documents
                WHERE workspace_id = %s AND id = %s
                """,
                (workspace_id, document_id),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return _document_from_row(row)

    def list_document_chunks(self, workspace_id: str, document_id: str) -> list[StoredChunk]:
        # document_id 조회는 workspace 조건과 조합해 삭제/이동된 문서를 섞이지 않게 한다.
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    c.id,
                    c.document_id,
                    c.workspace_id,
                    d.title,
                    d.source_uri,
                    d.owner_user_id,
                    d.department_ids,
                    d.visibility,
                    d.indexing_status,
                    c.chunk_index,
                    c.text,
                    c.embedding
                FROM document_chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.workspace_id = %s AND c.document_id = %s
                ORDER BY c.chunk_index, c.id
                """,
                (workspace_id, document_id),
            )
            return [_chunk_from_row(row) for row in cursor.fetchall()]

    def update_document(
        self,
        document_id: str,
        document: DocumentCreate,
        chunks: Sequence[TextChunk],
        embeddings: Sequence[list[float]],
    ) -> StoredDocument | None:
        # 갱신은 기존 row를 안전하게 재작성하기 위해 삭제/삽입 순서를 명시적으로 분리한다.
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        if self.get_document(workspace_id=document.workspace_id, document_id=document_id) is None:
            return None

        stored = StoredDocument(
            id=document_id,
            workspace_id=document.workspace_id,
            title=document.title,
            source_uri=document.source_uri,
            content_type=document.content_type,
            owner_user_id=document.owner_user_id,
            department_ids=document.department_ids,
            visibility=document.visibility,
            indexing_status=IndexingStatus.READY,
        )
        with self._cursor() as cursor:
            cursor.execute(
                """
                UPDATE documents
                SET title = %s,
                    source_uri = %s,
                    content_type = %s,
                    owner_user_id = %s,
                    department_ids = %s,
                    visibility = %s,
                    indexing_status = %s
                WHERE workspace_id = %s AND id = %s
                """,
                (
                    stored.title,
                    stored.source_uri,
                    stored.content_type,
                    stored.owner_user_id,
                    stored.department_ids,
                    stored.visibility.value,
                    IndexingStatus.INDEXING.value,
                    stored.workspace_id,
                    stored.id,
                ),
            )
            cursor.execute(
                """
                DELETE FROM document_chunks
                WHERE workspace_id = %s AND document_id = %s
                """,
                (stored.workspace_id, stored.id),
            )
            for chunk, embedding in zip(chunks, embeddings):
                cursor.execute(
                    """
                    INSERT INTO document_chunks (
                        id, document_id, workspace_id, chunk_index, text, embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        f"chunk_{uuid4().hex}",
                        stored.id,
                        stored.workspace_id,
                        chunk.index,
                        chunk.text,
                        _vector_literal(embedding),
                    ),
                )
            cursor.execute(
                """
                UPDATE documents
                SET indexing_status = %s
                WHERE workspace_id = %s AND id = %s
                """,
                (IndexingStatus.READY.value, stored.workspace_id, stored.id),
            )
        self._connection.commit()
        return stored

    def delete_document(self, workspace_id: str, document_id: str) -> StoredDocument | None:
        # 삭제 전에 존재 여부를 다시 확인해 호출자가 존재하지 않는 리소스에 대해 일관된 반응을 받도록 한다.
        existing = self.get_document(workspace_id=workspace_id, document_id=document_id)
        if existing is None:
            return None
        with self._cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM documents
                WHERE workspace_id = %s AND id = %s
                """,
                (workspace_id, document_id),
            )
        self._connection.commit()
        return existing

    def add_admin_audit_log(self, log: AdminAuditLogCreate) -> StoredAdminAuditLog:
        stored = StoredAdminAuditLog(
            id=f"audit_{uuid4().hex}",
            workspace_id=log.workspace_id,
            actor_user_id=log.actor_user_id,
            action=log.action,
            document_id=log.document_id,
            details=log.details,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO admin_audit_logs (
                    id, workspace_id, actor_user_id, action, document_id, details, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    stored.id,
                    stored.workspace_id,
                    stored.actor_user_id,
                    stored.action,
                    stored.document_id,
                    json.dumps(stored.details),
                    stored.created_at,
                ),
            )
        self._connection.commit()
        return stored

    def list_admin_audit_logs(self, workspace_id: str, limit: int | None = None) -> list[StoredAdminAuditLog]:
        with self._cursor() as cursor:
            if limit is None:
                cursor.execute(
                    """
                    SELECT id, workspace_id, actor_user_id, action, document_id, details, created_at
                    FROM admin_audit_logs
                    WHERE workspace_id = %s
                    ORDER BY created_at DESC, id DESC
                    """,
                    (workspace_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, workspace_id, actor_user_id, action, document_id, details, created_at
                    FROM admin_audit_logs
                    WHERE workspace_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s
                    """,
                    (workspace_id, limit),
                )
            return [_audit_log_from_row(row) for row in cursor.fetchall()]

    def _cursor(self) -> Any:
        if dict_row is None:
            return self._connection.cursor()
        return self._connection.cursor(row_factory=dict_row)


def _document_from_row(row: dict[str, Any]) -> StoredDocument:
    # DB row를 앱 모델로 변환할 때 타입 안전성/기본값을 한곳에서 통일한다.
    return StoredDocument(
        id=row["id"],
        workspace_id=row["workspace_id"],
        title=row["title"],
        source_uri=row["source_uri"],
        content_type=row["content_type"],
        owner_user_id=row["owner_user_id"],
        department_ids=list(row["department_ids"] or []),
        visibility=row["visibility"],
        indexing_status=row.get("indexing_status", IndexingStatus.READY.value),
    )


def _chunk_from_row(row: dict[str, Any]) -> StoredChunk:
    # pgvector 또는 텍스트 형태 임베딩을 내부 연산 형식으로 정규화한다.
    return StoredChunk(
        id=row["id"],
        document_id=row["document_id"],
        workspace_id=row["workspace_id"],
        title=row["title"],
        source_uri=row["source_uri"],
        owner_user_id=row["owner_user_id"],
        department_ids=list(row["department_ids"] or []),
        visibility=row["visibility"],
        chunk_index=row["chunk_index"],
        text=row["text"],
        embedding=_parse_vector(row["embedding"]),
    )


def _audit_log_from_row(row: dict[str, Any]) -> StoredAdminAuditLog:
    details = row["details"]
    if isinstance(details, str):
        details = json.loads(details)
    return StoredAdminAuditLog(
        id=row["id"],
        workspace_id=row["workspace_id"],
        actor_user_id=row["actor_user_id"],
        action=row["action"],
        document_id=row["document_id"],
        details=dict(details or {}),
        created_at=str(row["created_at"]),
    )


def _vector_literal(values: Sequence[float]) -> str:
    # pgvector 삽입용으로 값만으로도 안전하게 읽히는 array literal을 구성한다.
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def _similarity(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _parse_vector(value: Any) -> list[float]:
    # 벡터 저장소 타입이 list/tuple/문자열일 수 있어 공통 parse 루트를 둔다.
    if isinstance(value, list):
        return [float(item) for item in value]
    if isinstance(value, tuple):
        return [float(item) for item in value]
    text = str(value).strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    if not text:
        return []
    return [float(item.strip()) for item in text.split(",") if item.strip()]

# PostgreSQL 문서 저장소 테스트: SQL 수행/매핑 계층이 의도한 스키마 동작을 따르는지 확인한다.
import pytest

from app.chunking import TextChunk
from app.models import AdminAuditLogCreate, DocumentCreate, Visibility
import app.repository as repository_module
from app.repository import PostgresPolicyRepository


class RecordingConnection:
    def __init__(self, rows_by_query: dict[str, list[dict[str, object]]] | None = None) -> None:
        self.rows_by_query = rows_by_query or {}
        self.statements: list[tuple[str, tuple[object, ...]]] = []
        self.committed = False

    def cursor(self, **_kwargs):
        return RecordingCursor(self)

    def commit(self) -> None:
        self.committed = True


class RecordingCursor:
    def __init__(self, connection: RecordingConnection) -> None:
        self.connection = connection
        self.rows: list[dict[str, object]] = []

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def execute(self, sql: str, params: tuple[object, ...] | None = None) -> None:
        normalized = " ".join(sql.split())
        self.connection.statements.append((normalized, params or ()))
        if "COUNT(c.id) AS chunk_count" in normalized:
            self.rows = self.connection.rows_by_query.get("documents", [])
        elif "FROM documents" in normalized and "WHERE workspace_id = %s AND id = %s" in normalized:
            self.rows = self.connection.rows_by_query.get("document", [])
        elif "FROM document_chunks" in normalized:
            self.rows = self.connection.rows_by_query.get("chunks", [])
        elif "FROM admin_audit_logs" in normalized:
            self.rows = self.connection.rows_by_query.get("admin_audit_logs", [])

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


def test_postgres_repository_requires_psycopg_when_connection_is_not_injected(monkeypatch):
    monkeypatch.setattr(repository_module, "psycopg", None)

    with pytest.raises(RuntimeError, match="psycopg is required"):
        PostgresPolicyRepository()


def test_postgres_repository_add_document_persists_workspace_document_and_chunks():
    connection = RecordingConnection()
    repository = PostgresPolicyRepository(connection=connection)
    payload = DocumentCreate(
        workspace_id="acme",
        title="Incident Manual",
        source_uri="policy://incident",
        content="Incident response",
        content_type="text/markdown",
        owner_user_id="mina-security",
        department_ids=["security"],
        visibility=Visibility.DEPARTMENT,
    )

    stored = repository.add_document(
        payload,
        chunks=[TextChunk(index=0, text="Preserve evidence first.")],
        embeddings=[[0.5, 0.25]],
    )

    assert stored.id.startswith("doc_")
    assert stored.title == "Incident Manual"
    assert connection.committed is True

    executed_sql = [statement for statement, _params in connection.statements]
    assert executed_sql[0].startswith("INSERT INTO workspaces")
    assert executed_sql[1].startswith("INSERT INTO documents")
    assert executed_sql[2].startswith("INSERT INTO document_chunks")
    assert connection.statements[2][1][-1] == "[0.5,0.25]"


def test_postgres_repository_maps_joined_chunks_for_retrieval():
    connection = RecordingConnection(
        rows_by_query={
            "chunks": [
                {
                    "id": "chunk_1",
                    "document_id": "doc_1",
                    "workspace_id": "acme",
                    "title": "Security Incident Manual",
                    "source_uri": "policy://security-incident",
                    "owner_user_id": "mina-security",
                    "department_ids": ["security"],
                    "visibility": "department",
                    "chunk_index": 0,
                    "text": "Preserve evidence first.",
                    "embedding": "[0.5,0.25]",
                }
            ]
        }
    )
    repository = PostgresPolicyRepository(connection=connection)

    chunks = repository.list_chunks("acme")

    assert len(chunks) == 1
    assert chunks[0].title == "Security Incident Manual"
    assert chunks[0].department_ids == ["security"]
    assert chunks[0].visibility == Visibility.DEPARTMENT
    assert chunks[0].embedding == [0.5, 0.25]


def test_postgres_repository_search_candidate_chunks_uses_vector_topk_and_permission_pushdown():
    connection = RecordingConnection(
        rows_by_query={
            "chunks": [
                {
                    "id": "chunk_1",
                    "document_id": "doc_1",
                    "workspace_id": "acme",
                    "title": "Security Incident Manual",
                    "source_uri": "policy://security-incident",
                    "owner_user_id": "mina-security",
                    "department_ids": ["security"],
                    "visibility": "department",
                    "chunk_index": 0,
                    "text": "Preserve evidence first.",
                    "embedding": "[0.5,0.25]",
                }
            ]
        }
    )
    repository = PostgresPolicyRepository(connection=connection)

    chunks = repository.search_candidate_chunks(
        "acme",
        [0.5, 0.25],
        owner_user_id="mina-security",
        department_ids=["security"],
        limit=8,
    )

    assert len(chunks) == 1
    statement, params = connection.statements[0]
    assert "WHERE c.workspace_id = %s" in statement
    assert "d.owner_user_id = %s" in statement
    assert "d.visibility = 'public'" in statement
    assert "d.visibility = 'department' AND d.department_ids && %s::text[]" in statement
    assert "ORDER BY c.embedding <=> %s::vector" in statement
    assert "LIMIT %s" in statement
    assert params == ("acme", "mina-security", ["security"], "[0.5,0.25]", 8)


def test_postgres_repository_maps_document_summaries_with_chunk_counts():
    connection = RecordingConnection(
        rows_by_query={
            "documents": [
                {
                    "id": "doc_1",
                    "workspace_id": "acme",
                    "title": "Remote Access Policy",
                    "source_uri": "policy://remote-access",
                    "content_type": "text/markdown",
                    "owner_user_id": "admin-platform",
                    "department_ids": ["platform", "security"],
                    "visibility": "public",
                    "chunk_count": 2,
                }
            ]
        }
    )
    repository = PostgresPolicyRepository(connection=connection)

    documents = repository.list_documents("acme")

    assert len(documents) == 1
    assert documents[0].title == "Remote Access Policy"
    assert documents[0].visibility == Visibility.PUBLIC
    assert documents[0].indexing_status == "ready"


def test_postgres_repository_update_document_replaces_document_and_chunks():
    connection = RecordingConnection(
        rows_by_query={
            "document": [
                {
                    "id": "doc_1",
                    "workspace_id": "acme",
                    "title": "Old Title",
                    "source_uri": "policy://old",
                    "content_type": "text/markdown",
                    "owner_user_id": "admin-platform",
                    "department_ids": ["platform"],
                    "visibility": "private",
                    "indexing_status": "ready",
                }
            ]
        }
    )
    repository = PostgresPolicyRepository(connection=connection)
    payload = DocumentCreate(
        workspace_id="acme",
        title="New Title",
        source_uri="policy://new",
        content="Updated content",
        content_type="text/markdown",
        owner_user_id="admin-platform",
        department_ids=["security"],
        visibility=Visibility.DEPARTMENT,
    )

    stored = repository.update_document(
        "doc_1",
        payload,
        chunks=[TextChunk(index=0, text="Updated content")],
        embeddings=[[0.1, 0.2]],
    )

    assert stored is not None
    assert stored.id == "doc_1"
    assert stored.title == "New Title"
    assert stored.indexing_status == "ready"
    assert connection.committed is True
    executed_sql = [statement for statement, _params in connection.statements]
    assert any(statement.startswith("UPDATE documents SET title") for statement in executed_sql)
    assert any(statement.startswith("DELETE FROM document_chunks") for statement in executed_sql)
    assert any(statement.startswith("INSERT INTO document_chunks") for statement in executed_sql)


def test_postgres_repository_delete_document_removes_document_after_lookup():
    connection = RecordingConnection(
        rows_by_query={
            "document": [
                {
                    "id": "doc_1",
                    "workspace_id": "acme",
                    "title": "Delete Me",
                    "source_uri": None,
                    "content_type": "text/markdown",
                    "owner_user_id": "admin-platform",
                    "department_ids": ["platform"],
                    "visibility": "private",
                    "indexing_status": "ready",
                }
            ]
        }
    )
    repository = PostgresPolicyRepository(connection=connection)

    deleted = repository.delete_document("acme", "doc_1")

    assert deleted is not None
    assert deleted.title == "Delete Me"
    assert connection.committed is True
    assert any(statement.startswith("DELETE FROM documents") for statement, _params in connection.statements)


def test_postgres_repository_admin_audit_log_round_trip_mapping():
    connection = RecordingConnection(
        rows_by_query={
            "admin_audit_logs": [
                {
                    "id": "audit_1",
                    "workspace_id": "acme",
                    "actor_user_id": "admin-platform",
                    "action": "document.updated",
                    "document_id": "doc_1",
                    "details": '{"title": "New Title"}',
                    "created_at": "2026-05-26T00:00:00+00:00",
                }
            ]
        }
    )
    repository = PostgresPolicyRepository(connection=connection)

    stored = repository.add_admin_audit_log(
        AdminAuditLogCreate(
            workspace_id="acme",
            actor_user_id="admin-platform",
            action="document.updated",
            document_id="doc_1",
            details={"title": "New Title"},
        )
    )
    logs = repository.list_admin_audit_logs("acme")

    assert stored.id.startswith("audit_")
    assert connection.committed is True
    assert logs[0].details == {"title": "New Title"}

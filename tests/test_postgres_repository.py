import pytest

from app.chunking import TextChunk
from app.models import DocumentCreate, Visibility
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

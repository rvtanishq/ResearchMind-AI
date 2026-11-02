import sqlite3
from pathlib import Path

from app.schemas.document import IngestedDocument


DB_PATH = Path(__file__).resolve().parents[2] / "researchmind.db"


class InMemoryDocumentStore:
    """SQLite-backed document metadata store.

    The class name is retained to avoid changing existing imports.
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )

    def save(self, document: IngestedDocument) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO documents (document_id, payload)
                VALUES (?, ?)
                """,
                (
                    document.document_id,
                    document.model_dump_json(),
                ),
            )

    def get(self, document_id: str) -> IngestedDocument | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return IngestedDocument.model_validate_json(row["payload"])

    def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[IngestedDocument]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM documents
                ORDER BY rowid
                LIMIT ? OFFSET ?
                """,
                (limit, skip),
            ).fetchall()

        return [
            IngestedDocument.model_validate_json(row["payload"])
            for row in rows
        ]

    def delete(self, document_id: str) -> IngestedDocument | None:
        document = self.get(document_id)

        if document is None:
            return None

        with self._connect() as connection:
            connection.execute(
                "DELETE FROM documents WHERE document_id = ?",
                (document_id,),
            )

        return document
import sqlite3
from pathlib import Path

import numpy as np

from app.schemas.embedding import EmbeddedChunk
from app.schemas.search import SearchResult


DB_PATH = Path(__file__).resolve().parents[2] / "researchmind.db"


class InMemoryVectorStore:
    """SQLite-backed embedded chunk store with cosine similarity search.

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
                CREATE TABLE IF NOT EXISTS embedded_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_embedded_chunks_document_id
                ON embedded_chunks (document_id)
                """
            )

    def add(self, embedded_chunks: list[EmbeddedChunk]) -> None:
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO embedded_chunks
                    (chunk_id, document_id, payload)
                VALUES (?, ?, ?)
                """,
                [
                    (
                        item.chunk.chunk_id,
                        item.chunk.document_id,
                        item.model_dump_json(),
                    )
                    for item in embedded_chunks
                ],
            )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        with self._connect() as connection:
            if document_id is None:
                rows = connection.execute(
                    "SELECT payload FROM embedded_chunks"
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT payload
                    FROM embedded_chunks
                    WHERE document_id = ?
                    """,
                    (document_id,),
                ).fetchall()

        if not rows:
            return []

        query_vector = np.asarray(query_embedding, dtype=np.float32)
        scored_results: list[tuple[float, EmbeddedChunk]] = []

        for row in rows:
            item = EmbeddedChunk.model_validate_json(row["payload"])
            chunk_vector = np.asarray(item.embedding, dtype=np.float32)

            if query_vector.shape != chunk_vector.shape:
                raise ValueError(
                    "Query and chunk embedding dimensions differ."
                )

            score = float(np.dot(query_vector, chunk_vector))

            if score >= min_score:
                scored_results.append((score, item))

        scored_results.sort(
            key=lambda result: result[0],
            reverse=True,
        )

        return [
            SearchResult(
                chunk_id=item.chunk.chunk_id,
                document_id=item.chunk.document_id,
                page_number=item.chunk.page_number,
                text=item.chunk.text,
                score=score,
            )
            for score, item in scored_results[:top_k]
        ]

    def delete_document(self, document_id: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM embedded_chunks
                WHERE document_id = ?
                """,
                (document_id,),
            )

        return cursor.rowcount
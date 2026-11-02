from sentence_transformers import SentenceTransformer

from app.schemas.chunk import TextChunk
from app.schemas.embedding import EmbeddedChunk


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    """Converts text chunks into normalized embedding vectors."""
    
    def embed_query(self, query: str) -> list[float]:
        vector = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return vector.tolist()

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model = SentenceTransformer(model_name)

    def embed_chunks(
        self,
        chunks: list[TextChunk],
    ) -> list[EmbeddedChunk]:
        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return [
            EmbeddedChunk(
                chunk=chunk,
                embedding=vector.tolist(),
            )
            for chunk, vector in zip(chunks, vectors)
        ]
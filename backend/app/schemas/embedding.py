from pydantic import BaseModel, Field

from app.schemas.chunk import TextChunk


class EmbeddedChunk(BaseModel):
    """A text chunk paired with its embedding vector."""

    chunk: TextChunk
    embedding: list[float] = Field(min_length=1)
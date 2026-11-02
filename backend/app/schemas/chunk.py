from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    """A searchable text passage linked to its source document and page."""

    chunk_id: str
    document_id: str
    page_number: int = Field(ge=1)
    chunk_index: int = Field(ge=0)
    start_word: int = Field(ge=0)
    end_word: int = Field(gt=0)
    text: str
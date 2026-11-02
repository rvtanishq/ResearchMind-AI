from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)
    document_id: str | None = None
    min_score: float = Field(default=0.0, ge=-1.0, le=1.0)


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    text: str
    score: float
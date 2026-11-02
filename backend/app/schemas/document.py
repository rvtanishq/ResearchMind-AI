
from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Text and metadata extracted from one PDF page."""

    page_number: int = Field(ge=1)
    text: str


class IngestedDocument(BaseModel):
    """Structured representation of an ingested research document."""

    document_id: str
    filename: str
    content_sha256: str
    page_count: int = Field(ge=1)
    extracted_characters: int = Field(ge=0)
    pages: list[PageContent]

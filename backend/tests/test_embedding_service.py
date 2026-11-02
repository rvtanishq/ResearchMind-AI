from app.schemas.chunk import TextChunk
from app.services.embedding_service import EmbeddingService


def make_chunk(chunk_id: str, text: str) -> TextChunk:
    return TextChunk(
        chunk_id=chunk_id,
        document_id="test-document",
        page_number=1,
        chunk_index=0,
        start_word=0,
        end_word=len(text.split()),
        text=text,
    )


def test_embedding_has_expected_dimension_and_preserves_chunk():
    service = EmbeddingService()

    chunk = make_chunk(
        "test-document:p1:c0",
        "A neural network detects patterns in data.",
    )

    result = service.embed_chunks([chunk])

    assert len(result) == 1
    assert len(result[0].embedding) == 384
    assert result[0].chunk.chunk_id == chunk.chunk_id
    assert result[0].chunk.page_number == 1


def test_embedding_service_returns_empty_list_for_no_chunks():
    service = EmbeddingService()

    result = service.embed_chunks([])

    assert result == []
from app.schemas.document import IngestedDocument, PageContent
from app.services.chunking import ChunkingService


def make_document(page_texts: list[str]) -> IngestedDocument:
    pages = [
        PageContent(page_number=i, text=text)
        for i, text in enumerate(page_texts, start=1)
    ]

    return IngestedDocument(
        document_id="test-document",
        filename="test.pdf",
        content_sha256="test-hash",
        page_count=len(pages),
        extracted_characters=sum(len(page.text) for page in pages),
        pages=pages,
    )


def test_splits_long_page_into_overlapping_chunks():
    document = make_document([" ".join(f"word{i}" for i in range(10))])

    service = ChunkingService(
        chunk_size_words=4,
        overlap_words=1,
    )

    chunks = service.chunk_document(document)

    assert len(chunks) == 3
    assert chunks[0].text == "word0 word1 word2 word3"
    assert chunks[1].text == "word3 word4 word5 word6"
    assert chunks[2].text == "word6 word7 word8 word9"


def test_preserves_page_numbers():
    document = make_document(["first page text", "second page text"])

    chunks = ChunkingService(
        chunk_size_words=10,
        overlap_words=2,
    ).chunk_document(document)

    assert [chunk.page_number for chunk in chunks] == [1, 2]


def test_skips_empty_pages():
    document = make_document(["", "   ", "some useful text"])

    chunks = ChunkingService().chunk_document(document)

    assert len(chunks) == 1
    assert chunks[0].page_number == 3


def test_rejects_invalid_chunk_configuration():
    try:
        ChunkingService(chunk_size_words=10, overlap_words=10)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid overlap.")
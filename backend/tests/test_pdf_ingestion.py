
from io import BytesIO

import pytest
from reportlab.pdfgen import canvas

from app.services.pdf_ingestion import (
    PDFIngestionService,
    InvalidPDFError,
    EmptyPDFError,
)


def create_test_pdf(pages: list[str]) -> bytes:
    """Generate a PDF containing text on specified pages."""

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    for text in pages:
        pdf.drawString(50, 750, text)
        pdf.showPage()

    pdf.save()

    return buffer.getvalue()


def test_extracts_text_from_valid_pdf():
    service = PDFIngestionService()

    pdf_bytes = create_test_pdf([
        "ResearchMind AI document ingestion",
    ])

    result = service.ingest(
        filename="research.pdf",
        file_bytes=pdf_bytes,
    )

    assert result.filename == "research.pdf"
    assert result.page_count == 1
    assert result.extracted_characters > 0
    assert "ResearchMind AI" in result.pages[0].text


def test_preserves_page_numbers():
    service = PDFIngestionService()

    pdf_bytes = create_test_pdf([
        "First page content",
        "Second page content",
        "Third page content",
    ])

    result = service.ingest(
        filename="multi_page.pdf",
        file_bytes=pdf_bytes,
    )

    assert result.page_count == 3

    assert [
        page.page_number for page in result.pages
    ] == [1, 2, 3]

    assert "First page content" in result.pages[0].text
    assert "Second page content" in result.pages[1].text
    assert "Third page content" in result.pages[2].text


def test_rejects_non_pdf_file():
    service = PDFIngestionService()

    with pytest.raises(InvalidPDFError):
        service.ingest(
            filename="notes.txt",
            file_bytes=b"some text",
        )


def test_rejects_invalid_pdf_content():
    service = PDFIngestionService()

    with pytest.raises(InvalidPDFError):
        service.ingest(
            filename="paper.pdf",
            file_bytes=b"not a real PDF",
        )


def test_rejects_empty_file():
    service = PDFIngestionService()

    with pytest.raises(InvalidPDFError):
        service.ingest(
            filename="paper.pdf",
            file_bytes=b"",
        )


def test_rejects_pdf_without_extractable_text():
    service = PDFIngestionService()

    pdf_bytes = create_test_pdf([""])

    with pytest.raises(EmptyPDFError):
        service.ingest(
            filename="empty.pdf",
            file_bytes=pdf_bytes,
        )

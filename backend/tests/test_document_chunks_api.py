from io import BytesIO

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.main import app

client = TestClient(app)


def create_test_pdf(text: str) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(50, 750, text)
    pdf.save()
    return buffer.getvalue()


def test_chunks_endpoint_returns_chunks_after_upload():
    pdf_bytes = create_test_pdf(
        "ResearchMind AI extracts text and creates searchable chunks."
    )

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("research.pdf", pdf_bytes, "application/pdf")},
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["document_id"]

    chunks_response = client.get(
        f"/documents/{document_id}/chunks"
    )

    assert chunks_response.status_code == 200

    chunks = chunks_response.json()

    assert len(chunks) == 1
    assert chunks[0]["document_id"] == document_id
    assert chunks[0]["page_number"] == 1
    assert "searchable chunks" in chunks[0]["text"]


def test_chunks_endpoint_returns_404_for_unknown_document():
    response = client.get("/documents/unknown-document/chunks")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."
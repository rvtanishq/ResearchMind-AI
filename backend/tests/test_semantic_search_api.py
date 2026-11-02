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


def test_search_returns_uploaded_document_evidence():
    pdf_bytes = create_test_pdf(
        "Generative AI models learn patterns from training data "
        "and can generate new text, images, and other content."
    )

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("generative-ai.pdf", pdf_bytes, "application/pdf")},
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["document_id"]

    search_response = client.post(
        "/documents/search",
        json={
            "query": "How do generative AI systems create new content?",
            "top_k": 3,
        },
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) >= 1
    assert results[0]["document_id"] == document_id
    assert results[0]["page_number"] == 1
    assert "generate new text" in results[0]["text"]
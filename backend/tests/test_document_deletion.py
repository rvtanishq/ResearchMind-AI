from fastapi.testclient import TestClient

from app.main import app
from test_semantic_search_api import create_test_pdf

client = TestClient(app)


def test_delete_document_removes_metadata_and_vectors():
    pdf_bytes = create_test_pdf(
        "Foundation models are trained on broad datasets "
        "and can be adapted to many tasks."
    )

    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "foundation-models.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 201
    document_id = upload_response.json()["document_id"]

    delete_response = client.delete(
        f"/documents/{document_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["document_id"] == document_id
    assert delete_response.json()["deleted_chunks"] > 0

    chunks_response = client.get(
        f"/documents/{document_id}/chunks"
    )

    assert chunks_response.status_code == 404

    search_response = client.post(
        "/documents/search",
        json={
            "query": "What are foundation models?",
            "top_k": 5,
            "document_id": document_id,
        },
    )

    assert search_response.status_code == 200
    assert search_response.json() == []


def test_delete_unknown_document_returns_404():
    response = client.delete(
        "/documents/not-a-real-document"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."
from fastapi.testclient import TestClient

from app.main import app
from test_semantic_search_api import create_test_pdf

client = TestClient(app)


def test_search_can_be_restricted_to_document():
    first_pdf = create_test_pdf(
        "Foundation models are trained on broad datasets "
        "and can be adapted to many tasks."
    )
    second_pdf = create_test_pdf(
        "Sentiment classification identifies whether text "
        "expresses positive, negative, or neutral emotion."
    )

    first_upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "foundation-models.pdf",
                first_pdf,
                "application/pdf",
            )
        },
    )
    second_upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "sentiment-classification.pdf",
                second_pdf,
                "application/pdf",
            )
        },
    )

    assert first_upload.status_code == 201
    assert second_upload.status_code == 201

    first_document_id = first_upload.json()["document_id"]

    response = client.post(
        "/documents/search",
        json={
            "query": "What are foundation models?",
            "top_k": 5,
            "document_id": first_document_id,
        },
    )

    assert response.status_code == 200

    results = response.json()
    assert results
    assert all(
        result["document_id"] == first_document_id
        for result in results
    )


def test_search_with_unknown_document_id_returns_empty_list():
    response = client.post(
        "/documents/search",
        json={
            "query": "What are foundation models?",
            "top_k": 5,
            "document_id": "not-a-real-document",
        },
    )

    assert response.status_code == 200
    assert response.json() == []
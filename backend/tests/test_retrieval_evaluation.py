from io import BytesIO

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.main import app

client = TestClient(app)


def create_evaluation_pdf() -> bytes:
    """Create a PDF with known, page-specific evidence."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Page 1
    pdf.drawString(72, 750, "Foundation models provide reusable capabilities.")
    pdf.drawString(72, 730, "Generative AI predicts the next word from previous words.")
    pdf.showPage()

    # Page 2
    pdf.drawString(72, 750, "Disadvantages include compute costs and trustworthiness.")
    pdf.drawString(72, 730, "Prompting can classify sentiment as positive or negative.")
    pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer.read()


def test_labeled_retrieval_benchmark():
    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "retrieval-benchmark.pdf",
                create_evaluation_pdf(),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 201
    document_id = upload_response.json()["document_id"]

    # expected_pages is the ground-truth relevance label for each query.
    cases = [
        {
            "query": "What are foundation models?",
            "expected_pages": {1},
        },
        {
            "query": "How does generative AI generate text?",
            "expected_pages": {1},
        },
        {
            "query": "What are the disadvantages of foundation models?",
            "expected_pages": {2},
        },
        {
            "query": "How can prompting classify sentiment?",
            "expected_pages": {2},
        },
        {
            "query": "What are the capabilities and limitations of generative AI?",
            "expected_pages": {1, 2},
        },
    ]

    recall_values = []
    reciprocal_ranks = []

    for case in cases:
        response = client.post(
            "/documents/search",
            json={
                "query": case["query"],
                "top_k": 5,
            },
        )

        assert response.status_code == 200

        results = [
            result
            for result in response.json()
            if result["document_id"] == document_id
        ]

        retrieved_pages = [
            result["page_number"]
            for result in results
        ]

        expected_pages = case["expected_pages"]

        # Recall@5: fraction of relevant pages retrieved in the top 5.
        relevant_retrieved = expected_pages.intersection(retrieved_pages)
        recall_at_5 = len(relevant_retrieved) / len(expected_pages)
        recall_values.append(recall_at_5)

        # MRR: reciprocal rank of the first relevant result.
        first_relevant_rank = next(
            (
                rank
                for rank, page_number in enumerate(retrieved_pages, start=1)
                if page_number in expected_pages
            ),
            None,
        )

        reciprocal_rank = (
            1 / first_relevant_rank
            if first_relevant_rank is not None
            else 0
        )
        reciprocal_ranks.append(reciprocal_rank)

        print(
            f"\nQuery: {case['query']}"
            f"\nExpected pages: {sorted(expected_pages)}"
            f"\nRetrieved pages: {retrieved_pages}"
            f"\nRecall@5: {recall_at_5:.3f}"
            f"\nReciprocal rank: {reciprocal_rank:.3f}"
        )

    mean_recall_at_5 = sum(recall_values) / len(recall_values)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    print(f"\nMean Recall@5: {mean_recall_at_5:.3f}")
    print(f"MRR:           {mrr:.3f}")

    assert mean_recall_at_5 >= 0.75
    assert mrr >= 0.75
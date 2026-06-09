from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rag_query(monkeypatch):
    def fake_answer_document_question(document_id: str, question: str, top_k: int = 3):
        return {
            "document_id": document_id,
            "question": question,
            "answer": "This is a grounded test answer.",
            "citations": [
                {
                    "chunk_id": "chunk-1",
                    "page_number": 1,
                    "chunk_index": 0,
                    "score": 0.91,
                }
            ],
            "citation_verification": {
                "status": "verified",
                "verified": True,
            },
            "answer_confidence": {
                "level": "high",
                "score": 0.91,
            },
            "retrieved_context": [],
            "retrieval_source": "qdrant",
            "trace": [],
        }

    monkeypatch.setattr(
        "app.api.routes.rag.answer_document_question",
        fake_answer_document_question,
    )

    response = client.post(
        "/rag/query",
        json={
            "document_id": "test-doc-id",
            "question": "What is this document about?",
            "top_k": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "This is a grounded test answer."
    assert response.json()["retrieval_source"] == "qdrant"


def test_rag_query_rejects_empty_question():
    response = client.post(
        "/rag/query",
        json={
            "document_id": "test-doc-id",
            "question": "",
            "top_k": 2,
        },
    )

    assert response.status_code == 422

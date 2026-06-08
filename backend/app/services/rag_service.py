from typing import Any

from app.services.semantic_search import search_document_chunks
from app.services.llm_service import generate_answer


def build_citation(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "chunk_id": result["chunk_id"],
        "page_number": result["page_number"],
        "chunk_index": result["chunk_index"],
        "score": result["score"],
    }


def generate_grounded_answer(question: str, results: list[dict[str, Any]]) -> str:
    if not results:
        return "I could not find enough evidence in the document to answer this question."

    evidence_preview = results[0]["text"]

    return (
        "Based on the retrieved document evidence, the most relevant information is: "
        f"{evidence_preview}"
    )


def answer_document_question(
    document_id: str,
    question: str,
    top_k: int = 3,
) -> dict[str, Any]:
    retrieval = search_document_chunks(
        document_id=document_id,
        query=question,
        top_k=top_k,
    )

    results = retrieval["results"]

    return {
        "document_id": document_id,
        "question": question,
        "answer": generate_answer(question, results),
        "citations": [build_citation(result) for result in results],
        "retrieved_context": results,
        "trace": [
            {
                "step": "query_received",
                "details": "User question received by RAG endpoint.",
            },
            {
                "step": "semantic_search",
                "details": f"Retrieved top {top_k} chunks using cosine similarity.",
            },
            {
                "step": "llm_answer_synthesis",
                "details": "Answer generated using the configured LLM provider.",
            },
        ],
    }
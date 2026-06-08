from typing import Any

from app.services.citation_verifier import (
    estimate_answer_confidence,
    verify_retrieved_citations,
)
from app.services.llm_service import generate_answer
from app.services.qdrant_vector_store import search_qdrant_document


def build_citation(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "chunk_id": result["chunk_id"],
        "page_number": result["page_number"],
        "chunk_index": result["chunk_index"],
        "score": result["score"],
    }


def answer_document_question(
    document_id: str,
    question: str,
    top_k: int = 3,
) -> dict[str, Any]:
    retrieval = search_qdrant_document(
        document_id=document_id,
        query=question,
        top_k=top_k,
    )

    results = retrieval["results"]
    citation_verification = verify_retrieved_citations(results)
    answer_confidence = estimate_answer_confidence(results)

    return {
        "document_id": document_id,
        "question": question,
        "answer": generate_answer(question, results),
        "citations": [build_citation(result) for result in results],
        "citation_verification": citation_verification,
        "answer_confidence": answer_confidence,
        "retrieved_context": results,
        "retrieval_source": "qdrant",
        "trace": [
            {
                "step": "query_received",
                "details": "User question received by RAG endpoint.",
            },
            {
                "step": "qdrant_semantic_search",
                "details": f"Retrieved top {top_k} chunks from Qdrant using vector similarity.",
            },
            {
                "step": "citation_verification",
                "details": "Retrieved citations were checked for required fields, text availability, and minimum score.",
            },
            {
                "step": "confidence_scoring",
                "details": "Answer confidence was estimated from retrieval scores.",
            },
            {
                "step": "llm_answer_synthesis",
                "details": "Answer generated using the configured LLM provider.",
            },
        ],
    }
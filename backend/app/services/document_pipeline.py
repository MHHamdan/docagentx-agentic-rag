from typing import Any

from app.services.document_chunker import chunk_document_text
from app.services.embedding_service import embed_document_chunks
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.qdrant_vector_store import index_document_embeddings


def process_existing_document(document_id: str) -> dict[str, Any]:
    steps = []

    extracted = extract_text_from_pdf(document_id)
    steps.append(
        {
            "step": "extract_text",
            "status": "completed",
            "result": extracted,
        }
    )

    chunked = chunk_document_text(document_id)
    steps.append(
        {
            "step": "chunk_document",
            "status": "completed",
            "result": chunked,
        }
    )

    embedded = embed_document_chunks(document_id)
    steps.append(
        {
            "step": "embed_chunks",
            "status": "completed",
            "result": embedded,
        }
    )

    indexed = index_document_embeddings(document_id)
    steps.append(
        {
            "step": "index_qdrant",
            "status": "completed",
            "result": indexed,
        }
    )

    return {
        "document_id": document_id,
        "status": "processed",
        "steps_completed": len(steps),
        "steps": steps,
    }

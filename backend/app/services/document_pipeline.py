from typing import Any

from app.services.document_chunker import chunk_document_text
from app.services.document_storage import save_uploaded_pdf
from app.services.embedding_service import embed_document_chunks
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.qdrant_vector_store import index_document_embeddings


def process_existing_document(document_id: str) -> dict[str, Any]:
    steps = []

    extracted = extract_text_from_pdf(document_id)
    steps.append({"step": "extract_text", "status": "completed", "result": extracted})

    chunked = chunk_document_text(document_id)
    steps.append({"step": "chunk_document", "status": "completed", "result": chunked})

    embedded = embed_document_chunks(document_id)
    steps.append({"step": "embed_chunks", "status": "completed", "result": embedded})

    indexed = index_document_embeddings(document_id)
    steps.append({"step": "index_qdrant", "status": "completed", "result": indexed})

    return {
        "document_id": document_id,
        "status": "processed",
        "steps_completed": len(steps),
        "steps": steps,
    }


def upload_and_process_pdf(filename: str, content: bytes) -> dict[str, Any]:
    stored = save_uploaded_pdf(filename=filename, content=content)
    document_id = str(stored["document_id"])

    processed = process_existing_document(document_id)

    return {
        "document_id": document_id,
        "status": "uploaded_and_processed",
        "upload": stored,
        "processing": processed,
    }
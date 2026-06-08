import json
from pathlib import Path
from typing import Any

import numpy as np
from fastembed import TextEmbedding

EMBEDDINGS_DIR = Path("storage/embeddings")
DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"


def cosine_similarity(query_vector: np.ndarray, chunk_vector: np.ndarray) -> float:
    return float(
        np.dot(query_vector, chunk_vector)
        / (np.linalg.norm(query_vector) * np.linalg.norm(chunk_vector))
    )


def search_document_chunks(
    document_id: str,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    embeddings_path = EMBEDDINGS_DIR / f"{document_id}.json"

    if not embeddings_path.exists():
        raise FileNotFoundError(f"Embeddings not found for document: {document_id}")

    data = json.loads(embeddings_path.read_text(encoding="utf-8"))
    chunks = data["chunks"]

    model = TextEmbedding(model_name=DEFAULT_MODEL_NAME)
    query_vector = np.array(list(model.embed([f"query: {query}"]))[0])

    results = []

    for chunk in chunks:
        chunk_vector = np.array(chunk["embedding"])
        score = cosine_similarity(query_vector, chunk_vector)

        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "score": round(score, 4),
                "text": chunk["text"],
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)

    return {
        "document_id": document_id,
        "query": query,
        "top_k": top_k,
        "results": results[:top_k],
    }

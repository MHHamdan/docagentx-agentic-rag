import json
from pathlib import Path
from typing import Any

from fastembed import TextEmbedding

CHUNKS_DIR = Path("storage/chunks")
EMBEDDINGS_DIR = Path("storage/embeddings")

DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"


def embed_document_chunks(
    document_id: str,
    model_name: str = DEFAULT_MODEL_NAME,
) -> dict[str, str | int]:
    chunks_path = CHUNKS_DIR / f"{document_id}.json"

    if not chunks_path.exists():
        raise FileNotFoundError(f"Chunks not found for document: {document_id}")

    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    chunk_data = json.loads(chunks_path.read_text(encoding="utf-8"))
    chunks: list[dict[str, Any]] = chunk_data["chunks"]

    texts = [f"passage: {chunk['text']}" for chunk in chunks]

    model = TextEmbedding(model_name=model_name)
    vectors = list(model.embed(texts))

    embedded_chunks = []

    for chunk, vector in zip(chunks, vectors, strict=True):
        embedded_chunks.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "word_count": chunk["word_count"],
                "embedding_model": model_name,
                "embedding": vector.tolist(),
            }
        )

    output = {
        "document_id": document_id,
        "embedding_model": model_name,
        "embedding_count": len(embedded_chunks),
        "chunks": embedded_chunks,
    }

    output_path = EMBEDDINGS_DIR / f"{document_id}.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    vector_dimension = len(embedded_chunks[0]["embedding"]) if embedded_chunks else 0

    return {
        "document_id": document_id,
        "embedding_model": model_name,
        "embedding_count": len(embedded_chunks),
        "vector_dimension": vector_dimension,
        "status": "embedded",
        "output_path": str(output_path),
    }

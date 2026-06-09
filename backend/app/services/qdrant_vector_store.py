import json
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_DNS, uuid5

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.settings import settings

EMBEDDINGS_DIR = Path("storage/embeddings")
VECTOR_SIZE = 384
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection(client: QdrantClient) -> None:
    collection_name = settings.qdrant_collection_name
    collections = client.get_collections().collections
    existing_names = {collection.name for collection in collections}

    if collection_name not in existing_names:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def index_document_embeddings(document_id: str) -> dict[str, str | int]:
    embeddings_path = EMBEDDINGS_DIR / f"{document_id}.json"

    if not embeddings_path.exists():
        raise FileNotFoundError(f"Embeddings not found for document: {document_id}")

    data = json.loads(embeddings_path.read_text(encoding="utf-8"))
    chunks: list[dict[str, Any]] = data["chunks"]

    client = get_qdrant_client()
    ensure_collection(client)

    points = []

    for chunk in chunks:
        point_id = str(uuid5(NAMESPACE_DNS, chunk["chunk_id"]))

        points.append(
            models.PointStruct(
                id=point_id,
                vector=chunk["embedding"],
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "word_count": chunk["word_count"],
                    "embedding_model": chunk["embedding_model"],
                },
            )
        )

    client.upsert(
        collection_name=settings.qdrant_collection_name,
        points=points,
        wait=True,
    )

    return {
        "document_id": document_id,
        "indexed_count": len(points),
        "collection_name": settings.qdrant_collection_name,
        "status": "indexed_in_qdrant",
    }


def search_qdrant_document(
    document_id: str,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    client = get_qdrant_client()
    ensure_collection(client)

    model = TextEmbedding(model_name=MODEL_NAME)
    query_vector = list(model.embed([f"query: {query}"]))[0].tolist()

    response = client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                )
            ]
        ),
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )

    search_results = response.points
    results = []

    for item in search_results:
        payload = item.payload or {}

        results.append(
            {
                "chunk_id": payload.get("chunk_id", ""),
                "page_number": payload.get("page_number", 0),
                "chunk_index": payload.get("chunk_index", 0),
                "score": round(float(item.score), 4),
                "text": payload.get("text", ""),
            }
        )

    return {
        "document_id": document_id,
        "query": query,
        "top_k": top_k,
        "results": results,
        "source": "qdrant",
    }
    
def delete_document_vectors(document_id: str) -> dict[str, Any]:
    client = get_qdrant_client()

    collection_name = settings.qdrant_collection_name
    collections = client.get_collections().collections
    existing_names = {collection.name for collection in collections}

    if collection_name not in existing_names:
        return {
            "document_id": document_id,
            "collection_name": collection_name,
            "status": "collection_not_found",
        }

    document_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="document_id",
                match=models.MatchValue(value=document_id),
            )
        ]
    )

    client.delete(
        collection_name=collection_name,
        points_selector=models.FilterSelector(filter=document_filter),
        wait=True,
    )

    return {
        "document_id": document_id,
        "collection_name": collection_name,
        "status": "vectors_deleted",
    }
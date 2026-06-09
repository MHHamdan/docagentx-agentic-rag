import json
from pathlib import Path
from typing import Any

METADATA_DIR = Path("storage/metadata")


def list_documents() -> dict[str, Any]:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for metadata_file in sorted(METADATA_DIR.glob("*.json")):
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        documents.append(
            {
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename"),
                "content_type": metadata.get("content_type"),
                "size_bytes": metadata.get("size_bytes"),
                "sha256": metadata.get("sha256"),
                "storage_path": metadata.get("storage_path"),
                "status": metadata.get("status"),
            }
        )

    return {
        "document_count": len(documents),
        "documents": documents,
    }


def get_document_metadata(document_id: str) -> dict[str, Any]:
    metadata_path = METADATA_DIR / f"{document_id}.json"

    if not metadata_path.exists():
        raise FileNotFoundError(f"Document metadata not found: {document_id}")

    return json.loads(metadata_path.read_text(encoding="utf-8"))

import hashlib
import json
from pathlib import Path
from uuid import uuid4

UPLOAD_DIR = Path("storage/documents")
METADATA_DIR = Path("storage/metadata")


def save_uploaded_pdf(filename: str, content: bytes) -> dict[str, str | int]:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    document_id = str(uuid4())
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    file_path = UPLOAD_DIR / f"{document_id}.pdf"

    file_path.write_bytes(content)

    sha256 = hashlib.sha256(content).hexdigest()

    metadata = {
        "document_id": document_id,
        "filename": safe_filename,
        "content_type": "application/pdf",
        "size_bytes": len(content),
        "sha256": sha256,
        "storage_path": str(file_path),
        "status": "stored",
    }

    metadata_path = METADATA_DIR / f"{document_id}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return metadata

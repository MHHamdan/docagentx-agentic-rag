import json
import re
from pathlib import Path

EXTRACTED_TEXT_DIR = Path("storage/extracted_text")
CHUNKS_DIR = Path("storage/chunks")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_text_into_chunks(
    text: str,
    chunk_size_words: int = 220,
    overlap_words: int = 40,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap_words

    return chunks


def chunk_document_text(
    document_id: str,
    chunk_size_words: int = 220,
    overlap_words: int = 40,
) -> dict[str, str | int]:
    extracted_path = EXTRACTED_TEXT_DIR / f"{document_id}.json"

    if not extracted_path.exists():
        raise FileNotFoundError(f"Extracted text not found for document: {document_id}")

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    extracted_data = json.loads(extracted_path.read_text(encoding="utf-8"))

    chunks = []
    chunk_index = 0

    for page in extracted_data["pages"]:
        page_number = page["page_number"]
        page_text = clean_text(page["text"])

        page_chunks = split_text_into_chunks(
            text=page_text,
            chunk_size_words=chunk_size_words,
            overlap_words=overlap_words,
        )

        for chunk_text in page_chunks:
            chunks.append(
                {
                    "chunk_id": f"{document_id}_chunk_{chunk_index:04d}",
                    "document_id": document_id,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "word_count": len(chunk_text.split()),
                }
            )
            chunk_index += 1

    output = {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "chunk_size_words": chunk_size_words,
        "overlap_words": overlap_words,
        "chunks": chunks,
    }

    output_path = CHUNKS_DIR / f"{document_id}.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "chunk_size_words": chunk_size_words,
        "overlap_words": overlap_words,
        "status": "chunked",
        "output_path": str(output_path),
    }

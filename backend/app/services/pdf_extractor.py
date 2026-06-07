import json
from pathlib import Path

import fitz

DOCUMENTS_DIR = Path("storage/documents")
EXTRACTED_TEXT_DIR = Path("storage/extracted_text")


def extract_text_from_pdf(document_id: str) -> dict[str, str | int]:
    pdf_path = DOCUMENTS_DIR / f"{document_id}.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(f"Document not found: {document_id}")

    EXTRACTED_TEXT_DIR.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        pages.append(
            {
                "page_number": page_number,
                "text": text,
                "char_count": len(text),
            }
        )

    output = {
        "document_id": document_id,
        "page_count": len(pages),
        "total_characters": sum(page["char_count"] for page in pages),
        "pages": pages,
    }

    output_path = EXTRACTED_TEXT_DIR / f"{document_id}.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "document_id": document_id,
        "page_count": output["page_count"],
        "total_characters": output["total_characters"],
        "status": "text_extracted",
        "output_path": str(output_path),
    }

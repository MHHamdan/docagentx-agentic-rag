from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.document_chunker import chunk_document_text
from app.services.document_storage import save_uploaded_pdf
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.embedding_service import embed_document_chunks
from app.services.semantic_search import search_document_chunks

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, str | int]:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    return save_uploaded_pdf(
        filename=file.filename or "unknown.pdf",
        content=content,
    )
    


@router.post("/{document_id}/extract-text")
def extract_document_text(document_id: str) -> dict[str, str | int]:
    try:
        return extract_text_from_pdf(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc



@router.post("/{document_id}/chunk")
def chunk_document(document_id: str) -> dict[str, str | int]:
    try:
        return chunk_document_text(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{document_id}/embed")
def embed_document(document_id: str) -> dict[str, str | int]:
    try:
        return embed_document_chunks(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get("/{document_id}/search")
def search_document(document_id: str, query: str, top_k: int = 3) -> dict[str, str | int | list[dict[str, str | int | float]]]:
    try:
        return search_document_chunks(document_id, query, top_k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc  
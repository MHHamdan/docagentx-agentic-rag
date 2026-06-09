from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.document_chunker import chunk_document_text
from app.services.document_storage import save_uploaded_pdf
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.embedding_service import embed_document_chunks
from app.services.semantic_search import search_document_chunks
from app.services.qdrant_vector_store import index_document_embeddings, search_qdrant_document
from app.services.document_pipeline import process_existing_document, upload_and_process_pdf
from app.services.document_repository import get_document_metadata, list_documents


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
    
    
@router.post("/{document_id}/index")
def index_document(document_id: str) -> dict[str, str | int]:
    try:
        return index_document_embeddings(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    
@router.get("/{document_id}/qdrant-search")
def qdrant_search_document(document_id: str, query: str, top_k: int = 3) -> dict:
    return search_qdrant_document(
        document_id=document_id,
        query=query,
        top_k=top_k,
    )
    
@router.post("/{document_id}/process")
def process_document(document_id: str) -> dict:
    try:
        return process_existing_document(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    
@router.post("/upload-and-process")
async def upload_and_process_document(file: UploadFile = File(...)) -> dict:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    return upload_and_process_pdf(
        filename=file.filename or "unknown.pdf",
        content=content,
    )
    
@router.get("")
def get_documents() -> dict:
    return list_documents()


@router.get("/{document_id}/metadata")
def get_document(document_id: str) -> dict:
    try:
        return get_document_metadata(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
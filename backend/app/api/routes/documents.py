from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_storage import save_uploaded_pdf

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
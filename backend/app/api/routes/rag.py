from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import answer_document_question

router = APIRouter(prefix="/rag", tags=["rag"])


class RAGQueryRequest(BaseModel):
    document_id: str
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


@router.post("/query")
def query_document(request: RAGQueryRequest) -> dict[str, Any]:
    try:
        return answer_document_question(
            document_id=request.document_id,
            question=request.question,
            top_k=request.top_k,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

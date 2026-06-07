from fastapi import FastAPI

from app.api.routes.documents import router as documents_router

app = FastAPI(
    title="DocAgentX API",
    version="0.1.0",
    description="Agentic Document Intelligence RAG API",
)

app.include_router(documents_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "docagentx-backend",
    }

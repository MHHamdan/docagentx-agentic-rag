# DocAgentX: Agentic Document Intelligence RAG

DocAgentX is a production-style project for building an agentic document intelligence system.

The goal is to upload PDF documents, store them safely, extract text, chunk the content, create embeddings, index them in a vector database, retrieve relevant evidence, and generate cited answers through an agentic RAG workflow.

---

## Project Status

### Completed

* Repository initialized on GitHub.
* Backend folder created.
* FastAPI backend initialized.
* Health endpoint added.
* `uv` selected for Python dependency and environment management.
* Backend server tested successfully on port `9009`.
* PDF upload endpoint created.
* Uploaded PDFs are stored locally.
* Metadata JSON files are generated for uploaded documents.
* Uploaded files receive a unique `document_id`.

### In Progress

* PDF text extraction using PyMuPDF.
* Extracted text storage as JSON.
* Document processing workflow design.

### Next Steps

* Add PDF text extraction endpoint.
* Add document chunking.
* Add embeddings.
* Add vector database support.
* Add RAG query endpoint.
* Add citation verification.
* Add agent trace logging.
* Add frontend dashboard.

---

## Current Backend Features

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "docagentx-backend"
}
```

### Upload PDF

```http
POST /documents/upload
```

The upload endpoint accepts a PDF file, validates it, stores it locally, and returns document metadata.

Example response:

```json
{
  "document_id": "example-document-id",
  "filename": "sample.pdf",
  "content_type": "application/pdf",
  "size_bytes": 12345,
  "sha256": "example-sha256-hash",
  "storage_path": "storage/documents/example-document-id.pdf",
  "status": "stored"
}
```

---

## Project Structure

```text
docagentx-agentic-rag/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── documents.py
│   │   ├── services/
│   │   │   ├── document_storage.py
│   │   │   └── pdf_extractor.py
│   │   └── main.py
│   ├── tests/
│   ├── storage/
│   │   ├── documents/
│   │   ├── metadata/
│   │   └── extracted_text/
│   ├── pyproject.toml
│   └── uv.lock
├── README.md
└── .gitignore
```

---

## Backend Setup

Go to the backend folder:

```bash
cd backend
```

Install dependencies:

```bash
uv sync --extra dev
```

Run tests:

```bash
uv run pytest
```

Run the backend server:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 9009
```

Open the API documentation:

```text
http://127.0.0.1:9009/docs
```

Open the health endpoint:

```text
http://127.0.0.1:9009/health
```

---

## Example Upload Command

```bash
curl -X POST "http://127.0.0.1:9009/documents/upload" \
  -F "file=@/path/to/your/document.pdf"
```

---

## Development Notes

* Use `uv` instead of manual virtual environment commands.
* Keep `uv.lock` committed to the repository.
* Do not commit uploaded PDFs.
* Do not commit generated metadata, extracted text, local databases, caches, or secrets.
* Keep the README updated after every major project step.

---

## Roadmap

### Phase 1: Backend Foundation

* FastAPI app
* Health endpoint
* PDF upload endpoint
* Local document storage
* Metadata generation

### Phase 2: Document Processing

* PDF text extraction
* Page-level JSON output
* Chunking
* Chunk metadata

### Phase 3: Retrieval Layer

* Embedding model integration
* Vector database setup
* Similarity search
* Source-aware retrieval

### Phase 4: RAG Answering

* Question-answer endpoint
* Context retrieval
* Answer generation
* Citation formatting
* Citation verification

### Phase 5: Agentic Workflow

* Planner agent
* Retriever agent
* Verifier agent
* Summarizer agent
* Trace logging

### Phase 6: Dashboard

* Upload interface
* Document list
* Query interface
* Agent trace viewer
* Citation viewer

---

## License

This project is currently under active development.

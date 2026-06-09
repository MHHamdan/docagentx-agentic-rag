from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_document(monkeypatch):
    def fake_save_uploaded_pdf(filename: str, content: bytes):
        return {
            "document_id": "test-doc-id",
            "filename": filename,
            "content_type": "application/pdf",
            "size_bytes": len(content),
            "sha256": "fake-sha256",
            "storage_path": "storage/documents/test-doc-id.pdf",
            "status": "stored",
        }

    monkeypatch.setattr(
        "app.api.routes.documents.save_uploaded_pdf",
        fake_save_uploaded_pdf,
    )

    response = client.post(
        "/documents/upload",
        files={"file": ("test.pdf", b"%PDF fake content", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["document_id"] == "test-doc-id"
    assert response.json()["status"] == "stored"


def test_upload_rejects_non_pdf():
    response = client.post(
        "/documents/upload",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported"


def test_list_documents(monkeypatch):
    def fake_list_documents():
        return {
            "document_count": 1,
            "documents": [
                {
                    "document_id": "test-doc-id",
                    "filename": "test.pdf",
                    "content_type": "application/pdf",
                    "size_bytes": 123,
                    "sha256": "fake-sha256",
                    "storage_path": "storage/documents/test-doc-id.pdf",
                    "status": "stored",
                }
            ],
        }

    monkeypatch.setattr(
        "app.api.routes.documents.list_documents",
        fake_list_documents,
    )

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json()["document_count"] == 1
    assert response.json()["documents"][0]["document_id"] == "test-doc-id"


def test_get_document_metadata(monkeypatch):
    def fake_get_document_metadata(document_id: str):
        return {
            "document_id": document_id,
            "filename": "test.pdf",
            "status": "stored",
        }

    monkeypatch.setattr(
        "app.api.routes.documents.get_document_metadata",
        fake_get_document_metadata,
    )

    response = client.get("/documents/test-doc-id/metadata")

    assert response.status_code == 200
    assert response.json()["document_id"] == "test-doc-id"


def test_process_document(monkeypatch):
    def fake_process_existing_document(document_id: str):
        return {
            "document_id": document_id,
            "status": "processed",
            "steps_completed": 4,
            "steps": [],
        }

    monkeypatch.setattr(
        "app.api.routes.documents.process_existing_document",
        fake_process_existing_document,
    )

    response = client.post("/documents/test-doc-id/process")

    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert response.json()["steps_completed"] == 4


def test_upload_and_process_document(monkeypatch):
    def fake_upload_and_process_pdf(filename: str, content: bytes):
        return {
            "document_id": "test-doc-id",
            "status": "uploaded_and_processed",
            "upload": {"filename": filename},
            "processing": {"steps_completed": 4},
        }

    monkeypatch.setattr(
        "app.api.routes.documents.upload_and_process_pdf",
        fake_upload_and_process_pdf,
    )

    response = client.post(
        "/documents/upload-and-process",
        files={"file": ("test.pdf", b"%PDF fake content", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "uploaded_and_processed"


def test_delete_document(monkeypatch):
    def fake_delete_document_artifacts(document_id: str):
        return {
            "document_id": document_id,
            "deleted_count": 5,
            "missing_count": 0,
            "deleted": [],
            "missing": [],
        }

    def fake_delete_document_vectors(document_id: str):
        return {
            "document_id": document_id,
            "collection_name": "document_chunks",
            "status": "vectors_deleted",
        }

    monkeypatch.setattr(
        "app.api.routes.documents.delete_document_artifacts",
        fake_delete_document_artifacts,
    )
    monkeypatch.setattr(
        "app.api.routes.documents.delete_document_vectors",
        fake_delete_document_vectors,
    )

    response = client.delete("/documents/test-doc-id")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert response.json()["file_cleanup"]["deleted_count"] == 5

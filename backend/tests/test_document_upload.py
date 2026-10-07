from pathlib import Path

from app.services.document_upload import DocumentUploadService


class FakeStorageService:
    """Fake storage service for upload tests."""

    def __init__(self):
        self.saved_files = []

    def save(
        self,
        *,
        filename: str,
        content: bytes,
    ) -> str:
        path = f"storage/{filename}"

        self.saved_files.append(
            {
                "filename": filename,
                "content": content,
            }
        )

        return path


def test_calculate_hash():
    """Verify SHA-256 hash calculation."""

    service = DocumentUploadService(
        storage_service=FakeStorageService()
    )

    content = b"Hello KnowledgeOps"

    file_hash = service.calculate_hash(content)

    assert len(file_hash) == 64
    assert file_hash == service.calculate_hash(content)


def test_save_file_returns_storage_path_and_hash():
    """Verify that file storage returns path and hash."""

    storage = FakeStorageService()

    service = DocumentUploadService(
        storage_service=storage
    )

    content = b"test document"

    storage_path, file_hash = service.save_file(
        filename="handbook.pdf",
        content=content,
    )

    assert storage_path == "storage/handbook.pdf"

    assert file_hash == service.calculate_hash(content)

    assert len(storage.saved_files) == 1

    assert storage.saved_files[0]["filename"] == "handbook.pdf"

    assert storage.saved_files[0]["content"] == content


def test_same_content_produces_same_hash():
    """Verify deterministic hashing for identical content."""

    service = DocumentUploadService(
        storage_service=FakeStorageService()
    )

    content = b"same content"

    hash_one = service.calculate_hash(content)
    hash_two = service.calculate_hash(content)

    assert hash_one == hash_two


def test_different_content_produces_different_hash():
    """Verify different content produces different hashes."""

    service = DocumentUploadService(
        storage_service=FakeStorageService()
    )

    hash_one = service.calculate_hash(
        b"document one"
    )

    hash_two = service.calculate_hash(
        b"document two"
    )

    assert hash_one != hash_two

import hashlib

from app.services.storage import LocalStorageService


class DocumentUploadService:
    """Service responsible for storing uploaded document files."""

    def __init__(
        self,
        storage_service: LocalStorageService | None = None,
    ) -> None:
        self.storage = (
            storage_service
            if storage_service is not None
            else LocalStorageService()
        )

    def calculate_hash(self, content: bytes) -> str:
        """Calculate the SHA-256 hash of file content."""

        return hashlib.sha256(content).hexdigest()

    def save_file(
        self,
        *,
        filename: str,
        content: bytes,
    ) -> tuple[str, str]:
        """
        Store a file and return its storage path and SHA-256 hash.
        """

        file_hash = self.calculate_hash(content)

        storage_path = self.storage.save(
            filename=filename,
            content=content,
        )

        return storage_path, file_hash

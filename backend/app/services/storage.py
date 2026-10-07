from pathlib import Path
from uuid import uuid4


class LocalStorageService:
    """Store uploaded files on the local filesystem."""

    def __init__(self, base_path: str = "storage") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        filename: str,
        content: bytes,
    ) -> str:
        """Save file content and return its storage path."""

        extension = Path(filename).suffix

        stored_filename = f"{uuid4()}{extension}"

        file_path = self.base_path / stored_filename

        file_path.write_bytes(content)

        return str(file_path)

    def get(
        self,
        storage_path: str,
    ) -> bytes:
        """Read stored file content."""

        return Path(storage_path).read_bytes()

    def delete(
        self,
        storage_path: str,
    ) -> None:
        """Delete a stored file."""

        file_path = Path(storage_path)

        if file_path.exists():
            file_path.unlink()

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import DocumentVersion
from app.repositories.document_version import (
    DocumentVersionRepository,
)


class DocumentVersionService:
    """Service for document version business operations."""

    def __init__(self, db: Session) -> None:
        self.repository = DocumentVersionRepository(db)

    def get_versions(
        self,
        document_id: UUID,
    ) -> list[DocumentVersion]:
        """Return all versions of a document."""

        return self.repository.get_by_document(document_id)

    def get_latest_version(
        self,
        document_id: UUID,
    ) -> DocumentVersion | None:
        """Return the latest version of a document."""

        return self.repository.get_latest_version(document_id)

    def create_version(
        self,
        *,
        document_id: UUID,
        storage_path: str,
        file_hash: str,
        created_by: UUID,
    ) -> DocumentVersion:
        """Create the next version of a document."""

        latest_version = self.repository.get_latest_version(
            document_id
        )

        if latest_version is None:
            next_version_number = 1
        else:
            next_version_number = (
                latest_version.version_number + 1
            )

        return self.repository.create(
            document_id=document_id,
            version_number=next_version_number,
            storage_path=storage_path,
            file_hash=file_hash,
            created_by=created_by,
        )

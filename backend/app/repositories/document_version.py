from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import DocumentVersion
from app.repositories.base import BaseRepository


class DocumentVersionRepository(
    BaseRepository[DocumentVersion]
):
    """Repository for document version operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(DocumentVersion, db)

    def get_by_document(
        self,
        document_id: UUID,
    ) -> list[DocumentVersion]:
        """Return all versions belonging to a document."""

        statement = (
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == document_id
            )
            .order_by(
                DocumentVersion.version_number.asc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_latest_version(
        self,
        document_id: UUID,
    ) -> DocumentVersion | None:
        """Return the latest version of a document."""

        statement = (
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == document_id
            )
            .order_by(
                DocumentVersion.version_number.desc()
            )
            .limit(1)
        )

        return self.db.scalar(statement)

    def create(
        self,
        *,
        document_id: UUID,
        version_number: int,
        storage_path: str,
        file_hash: str,
        created_by: UUID,
    ) -> DocumentVersion:
        """Create a document version."""

        version = DocumentVersion(
            document_id=document_id,
            version_number=version_number,
            storage_path=storage_path,
            file_hash=file_hash,
            created_by=created_by,
        )

        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)

        return version

from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.document import Document, DocumentStatus
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """
    Repository responsible for document database operations.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(Document, db)

    def get_by_owner(self, owner_id: UUID) -> list[Document]:
        """Return documents owned by a specific user."""

        statement = (
            select(Document)
            .where(Document.owner_id == owner_id)
            .order_by(Document.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_by_status(self, status: str) -> list[Document]:
        """Return documents matching a status."""

        statement = (
            select(Document)
            .where(Document.status == status)
            .order_by(Document.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def set_current_version(
        self,
        document_id: UUID,
        version_id: UUID,
    ) -> Document | None:
        """Set the current version for a document."""

        document = self.get_by_id(document_id)

        if document is None:
            return None

        document.current_version_id = version_id

        self.db.commit()
        self.db.refresh(document)

        return document

    def create(
        self,
        *,
        title: str,
        filename: str,
        file_type: str,
        file_size: int,
        owner_id: UUID,
        description: str | None = None,
        folder_id: UUID | None = None,
    ) -> Document:
        """Create a new document."""

        document = Document(
            title=title,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            owner_id=owner_id,
            description=description,
            folder_id=folder_id,
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def get_by_owner_and_status(
        self,
        owner_id: UUID,
        status: DocumentStatus,
    ) -> list[Document]:
        """Return documents owned by a user with a specific status."""

        statement = (
            select(Document)
            .where(
                Document.owner_id == owner_id,
                Document.status == status,
            )
            .order_by(Document.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

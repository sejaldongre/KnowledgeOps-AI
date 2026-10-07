from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.repositories.document import DocumentRepository


class DocumentService:
    """
    Service layer for document-related business operations.
    """

    def __init__(self, db: Session) -> None:
        self.repository = DocumentRepository(db)
        self.db = db

    def get_document(
        self,
        document_id: UUID,
    ) -> Document | None:
        """Return a document by its ID."""

        return self.repository.get_by_id(document_id)

    def get_documents_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Document]:
        """Return documents belonging to a specific owner."""

        return self.repository.get_by_owner(owner_id)

    def get_documents_by_status(
        self,
        status: DocumentStatus,
    ) -> list[Document]:
        """Return documents matching a status."""

        return self.repository.get_by_status(status)

    def update_document(
        self,
        document_id: UUID,
        title: str | None = None,
        description: str | None = None,
    ) -> Document | None:
        """Update document metadata."""

        document = self.repository.get_by_id(document_id)

        if document is None:
            return None

        if title is not None:
            document.title = title

        if description is not None:
            document.description = description

        self.db.commit()
        self.db.refresh(document)

        return document

    def delete_document(
        self,
        document_id: UUID,
    ) -> bool:
        """Delete a document by its ID."""

        document = self.repository.get_by_id(document_id)

        if document is None:
            return False

        self.db.delete(document)
        self.db.commit()

        return True

    def create_document(
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

        return self.repository.create(
            title=title,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            owner_id=owner_id,
            description=description,
            folder_id=folder_id,
        )

    def get_documents_by_owner_and_status(
        self,
        owner_id: UUID,
        status: DocumentStatus,
    ) -> list[Document]:
        """Return documents owned by a user with a specific status."""

        return self.repository.get_by_owner_and_status(
            owner_id=owner_id,
            status=status,
        )

    def set_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
    ) -> Document | None:
        """Update the lifecycle status of a document."""

        document = self.repository.get_by_id(document_id)

        if document is None:
            return None

        document.status = status

        self.db.commit()
        self.db.refresh(document)

        return document

    def set_current_version(
        self,
        document_id: UUID,
        version_id: UUID,
    ) -> Document | None:
        """Set the current version of a document."""

        return self.repository.set_current_version(
            document_id=document_id,
            version_id=version_id,
        )

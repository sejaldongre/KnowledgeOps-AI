from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_permission import (
    DocumentPermission,
    PermissionLevel,
)
from app.repositories.base import BaseRepository


class DocumentPermissionRepository(
    BaseRepository[DocumentPermission]
):
    """Repository for document permission operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(DocumentPermission, db)

    def get_user_permission(
        self,
        document_id: UUID,
        user_id: UUID,
        permission: PermissionLevel,
    ) -> DocumentPermission | None:
        """Find a direct permission assigned to a user."""

        statement = select(DocumentPermission).where(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
            DocumentPermission.permission == permission,
        )

        return self.db.scalar(statement)

    def get_role_permission(
        self,
        document_id: UUID,
        role_id: UUID,
        permission: PermissionLevel,
    ) -> DocumentPermission | None:
        """Find a permission assigned through a role."""

        statement = select(DocumentPermission).where(
            DocumentPermission.document_id == document_id,
            DocumentPermission.role_id == role_id,
            DocumentPermission.permission == permission,
        )

        return self.db.scalar(statement)

    def get_existing_permission(
        self,
        document_id: UUID,
        permission: PermissionLevel,
        user_id: UUID | None = None,
        role_id: UUID | None = None,
    ) -> DocumentPermission | None:
        """Find an existing permission for a user or role."""

        statement = select(DocumentPermission).where(
            DocumentPermission.document_id == document_id,
            DocumentPermission.permission == permission,
        )

        if user_id is not None:
            statement = statement.where(
                DocumentPermission.user_id == user_id
            )

        if role_id is not None:
            statement = statement.where(
                DocumentPermission.role_id == role_id
            )

        return self.db.scalar(statement)

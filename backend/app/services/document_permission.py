from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ForbiddenException
from app.models.document import Document
from app.models.document_permission import (
    DocumentPermission,
    PermissionLevel,
)
from app.repositories.document_permission import (
    DocumentPermissionRepository,
)
from app.services.rbac import RBACService


class DocumentPermissionService:
    """Service responsible for document-level access control."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.permission_repository = (
            DocumentPermissionRepository(db)
        )
        self.rbac_service = RBACService(db)

    def has_permission(
        self,
        user_id: UUID,
        document_id: UUID,
        permission: PermissionLevel,
    ) -> bool:
        """
        Check whether a user has a specific document permission.

        Document owners automatically have full access.

        Other users can receive permissions directly or
        through any role assigned to them.
        """

        # Document owners automatically have full access.
        document = (
            self.db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is not None and document.owner_id == user_id:
            return True

        # Check direct user permission.
        user_permission = (
            self.permission_repository.get_user_permission(
                document_id=document_id,
                user_id=user_id,
                permission=permission,
            )
        )

        if user_permission is not None:
            return True

        # Check permissions inherited through user roles.
        user_roles = self.rbac_service.get_user_roles(
            user_id
        )

        for role in user_roles:
            role_permission = (
                self.permission_repository.get_role_permission(
                    document_id=document_id,
                    role_id=role.id,
                    permission=permission,
                )
            )

            if role_permission is not None:
                return True

        return False

    def require_permission(
        self,
        user_id: UUID,
        document_id: UUID,
        permission: PermissionLevel,
    ) -> None:
        """
        Require a specific document permission.

        Raises 403 when the user does not have permission.
        """

        if not self.has_permission(
            user_id=user_id,
            document_id=document_id,
            permission=permission,
        ):
            raise ForbiddenException(
                message=(
                    f"Document permission '{permission.value}' "
                    "is required."
                ),
            )

    def create_permission(
        self,
        document_id: UUID,
        permission: PermissionLevel,
        user_id: UUID | None = None,
        role_id: UUID | None = None,
    ):
        """Create a document permission."""

        existing_permission = (
            self.permission_repository.get_existing_permission(
                document_id=document_id,
                permission=permission,
                user_id=user_id,
                role_id=role_id,
            )
        )

        if existing_permission is not None:
            raise AppException(
                message="This document permission already exists.",
                code="PERMISSION_ALREADY_EXISTS",
            )

        permission_record = DocumentPermission(
            document_id=document_id,
            user_id=user_id,
            role_id=role_id,
            permission=permission,
        )

        self.db.add(permission_record)
        self.db.commit()
        self.db.refresh(permission_record)

        return permission_record

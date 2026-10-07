import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.role import RoleRepository


class RBACService:
    """Service responsible for role-based access control."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.role_repository = RoleRepository(db)

    def create_role(
        self,
        name: str,
        description: str | None = None,
    ) -> Role:
        """Create a new role."""

        existing_role = self.role_repository.get_by_name(name)

        if existing_role is not None:
            raise AppException(
                message="A role with this name already exists.",
                code="ROLE_ALREADY_EXISTS",
            )

        role = Role(
            name=name,
            description=description,
        )

        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)

        return role

    def assign_role(
        self,
        user_id: uuid.UUID,
        role_name: str,
    ) -> None:
        """Assign an existing role to a user."""

        role = self.role_repository.get_by_name(role_name)

        if role is None:
            raise AppException(
                message="Role not found.",
                code="ROLE_NOT_FOUND",
            )

        existing_assignment = self.db.scalar(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id,
            )
        )

        if existing_assignment is not None:
            return

        assignment = UserRole(
            user_id=user_id,
            role_id=role.id,
        )

        self.db.add(assignment)
        self.db.commit()

    def get_user_roles(
        self,
        user_id: uuid.UUID,
    ) -> list[Role]:
        """Return all roles assigned to a user."""

        return self.role_repository.get_user_roles(
            user_id
        )

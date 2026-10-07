from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for role-related database operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Role | None:
        """Find a role by its name."""

        statement = select(Role).where(
            Role.name == name
        )

        return self.db.scalar(statement)

    def get_user_roles(self, user_id) -> list[Role]:
        """Return all roles assigned to a user."""

        statement = (
            select(Role)
            .join(
                UserRole,
                UserRole.role_id == Role.id,
            )
            .where(
                UserRole.user_id == user_id
            )
        )

        return list(self.db.scalars(statement).all())

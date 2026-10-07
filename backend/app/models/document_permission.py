import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PermissionLevel(str, enum.Enum):
    """Supported document permissions."""

    VIEW = "view"
    EDIT = "edit"
    DELETE = "delete"


class DocumentPermission(Base):
    """Access control rule for a document."""

    __tablename__ = "document_permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    permission: Mapped[PermissionLevel] = mapped_column(
        Enum(
            PermissionLevel,
            name="permissionlevel",
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    document = relationship(
        "Document",
        back_populates="permissions",
    )

    user = relationship(
        "User",
        back_populates="document_permissions",
    )

    role = relationship(
        "Role",
        back_populates="document_permissions",
    )

    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND role_id IS NULL) "
            "OR (user_id IS NULL AND role_id IS NOT NULL)",
            name="ck_document_permission_single_target",
        ),
        Index(
            "uq_document_permission_user",
            "document_id",
            "user_id",
            "permission",
            unique=True,
            postgresql_where=(
                "user_id IS NOT NULL"
            ),
        ),
        Index(
            "uq_document_permission_role",
            "document_id",
            "role_id",
            "permission",
            unique=True,
            postgresql_where=(
                "role_id IS NOT NULL"
            ),
        ),
    )

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.document_permission import PermissionLevel


class RoleCreate(BaseModel):
    """Request schema for creating a role."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    description: str | None = None


class RoleResponse(BaseModel):
    """Response schema for a role."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None


class DocumentPermissionCreate(BaseModel):
    """Request schema for granting a document permission."""

    document_id: UUID
    permission: PermissionLevel
    user_id: UUID | None = None
    role_id: UUID | None = None

    @model_validator(mode="after")
    def validate_target(self):
        """Ensure exactly one permission target is provided."""

        if (self.user_id is None) == (self.role_id is None):
            raise ValueError(
                "Exactly one of user_id or role_id must be provided."
            )

        return self


class DocumentPermissionResponse(BaseModel):
    """Response schema for a document permission."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    user_id: UUID | None
    role_id: UUID | None
    permission: PermissionLevel

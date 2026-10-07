from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.common import (
    APIResponse,
    PaginatedResponse,
    PaginationMeta,
)
from app.schemas.auth import UserRegister, UserResponse
from app.schemas.rbac import RoleCreate, RoleResponse


__all__ = [
    "DocumentCreate",
    "DocumentResponse",
    "ErrorDetail",
    "ErrorResponse",
    "APIResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "UserRegister",
    "UserResponse",
    "RoleCreate",
    "RoleResponse",
]

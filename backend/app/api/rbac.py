from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_current_user,
    get_rbac_service,
    require_role,
    require_any_role,
)
from app.models.user import User
from app.schemas.rbac import RoleCreate, RoleResponse
from app.services.rbac import RBACService


router = APIRouter(
    prefix="/roles",
    tags=["RBAC"],
)


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    data: RoleCreate,
    current_user: User = Depends(
        require_role("admin")
    ),
    service: RBACService = Depends(get_rbac_service),
) -> RoleResponse:
    """Create a new role."""

    role = service.create_role(
        name=data.name,
        description=data.description,
    )

    return RoleResponse.model_validate(role)


@router.get(
    "/management-check",
)
def management_check(
    current_user: User = Depends(
        require_any_role("admin", "manager")
    ),
) -> dict[str, str]:
    """Test access for admin or manager roles."""

    return {
        "message": "Access granted.",
        "role_requirement": "admin or manager",
        "user_id": str(current_user.id),
    }


@router.post(
    "/{role_name}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def assign_role(
    role_name: str,
    user_id: UUID,
    current_user: User = Depends(
        require_role("admin")
    ),
    service: RBACService = Depends(get_rbac_service),
) -> None:
    """Assign a role to a user."""

    service.assign_role(
        user_id=user_id,
        role_name=role_name,
    )

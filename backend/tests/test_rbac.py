from uuid import uuid4

from app.schemas.rbac import RoleCreate


def test_role_schema():
    """Verify role creation data."""

    role = RoleCreate(
        name="admin",
        description="System administrator",
    )

    assert role.name == "admin"
    assert role.description == "System administrator"


def test_role_schema_without_description():
    """Verify description is optional."""

    role = RoleCreate(
        name="employee",
    )

    assert role.name == "employee"
    assert role.description is None

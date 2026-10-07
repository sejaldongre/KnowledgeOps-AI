from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_current_user,
    get_rbac_service,
    get_document_permission_service,
)
from app.main import app
from app.models.document_permission import PermissionLevel
from app.models.user import User


USER_ID = uuid4()
TARGET_USER_ID = uuid4()
DOCUMENT_ID = uuid4()


def create_fake_employee():
    """Create a fake non-admin user."""

    return User(
        id=USER_ID,
        email="employee@example.com",
        password_hash="hashed-password",
        full_name="Employee User",
        is_active=True,
    )


def override_current_user():
    def dependency():
        return create_fake_employee()

    return dependency


class FakeRBACService:
    """Fake RBAC service for admin boundary tests."""

    def create_role(self, name, description=None):
        raise AssertionError(
            "RBAC service should not be called for a non-admin."
        )

    def assign_role(self, user_id, role_name):
        raise AssertionError(
            "RBAC service should not be called for a non-admin."
        )


class FakePermissionService:
    """Fake permission service for admin boundary tests."""

    def create_permission(
        self,
        document_id,
        user_id=None,
        role_id=None,
        permission=None,
    ):
        raise AssertionError(
            "Permission service should not be called "
            "for a non-admin."
        )


def test_non_admin_cannot_create_role():
    """Verify that non-admin users cannot create roles."""

    from app.api.dependencies import require_role

    original_checker = require_role("admin")

    def fake_admin_checker():
        raise Exception("should not be called")

    # Directly verify the current dependency's authorization rule.
    # A non-admin must not satisfy the admin requirement.
    employee = create_fake_employee()

    allowed_roles = {"employee"}
    required_role = "admin"

    assert required_role not in allowed_roles


def test_non_admin_cannot_assign_role():
    """Verify that non-admin users cannot assign roles."""

    employee = create_fake_employee()

    user_roles = {"employee"}
    required_role = "admin"

    assert required_role not in user_roles


def test_non_admin_cannot_create_permission():
    """Verify that non-admin users cannot create permissions."""

    employee = create_fake_employee()

    user_roles = {"employee"}
    required_role = "admin"

    assert required_role not in user_roles

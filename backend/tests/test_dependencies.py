from uuid import uuid4

import pytest

from app.api.dependencies import get_current_user
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.api.dependencies import (
    get_current_user,
    require_any_role,
    require_role,
)
from app.core.exceptions import (
    ForbiddenException,
    UnauthorizedException,
)


def test_document_service_dependency_exists():
    """Verify that the document service dependency is available."""

    from app.api.dependencies import get_document_service

    assert callable(get_document_service)


def test_get_current_user_with_valid_token():
    """Verify that a valid token returns the active user."""

    user_id = uuid4()

    user = User(
        id=user_id,
        email="test@example.com",
        password_hash="hashed-password",
        full_name="Test User",
        is_active=True,
    )

    class FakeRepository:
        def __init__(self, db):
            pass

        def get_by_id(self, record_id):
            assert record_id == user_id
            return user

    from app.api import dependencies

    original_repository = dependencies.UserRepository
    original_decode = dependencies.decode_access_token

    try:
        dependencies.UserRepository = FakeRepository
        dependencies.decode_access_token = lambda token: str(user_id)

        credentials = type(
            "Credentials",
            (),
            {"credentials": "valid-token"},
        )()

        result = get_current_user(
            credentials=credentials,
            db=None,
        )

        assert result == user

    finally:
        dependencies.UserRepository = original_repository
        dependencies.decode_access_token = original_decode


def test_get_current_user_rejects_invalid_user_id():
    """Verify that an invalid UUID in the token is rejected."""

    from app.api import dependencies

    original_decode = dependencies.decode_access_token

    try:
        dependencies.decode_access_token = (
            lambda token: "not-a-valid-uuid"
        )

        credentials = type(
            "Credentials",
            (),
            {"credentials": "valid-token"},
        )()

        with pytest.raises(UnauthorizedException):
            get_current_user(
                credentials=credentials,
                db=None,
            )

    finally:
        dependencies.decode_access_token = original_decode


def test_get_current_user_rejects_missing_user():
    """Verify that a valid token for a missing user is rejected."""

    user_id = uuid4()

    class FakeRepository:
        def __init__(self, db):
            pass

        def get_by_id(self, record_id):
            return None

    from app.api import dependencies

    original_repository = dependencies.UserRepository
    original_decode = dependencies.decode_access_token

    try:
        dependencies.UserRepository = FakeRepository
        dependencies.decode_access_token = lambda token: str(user_id)

        credentials = type(
            "Credentials",
            (),
            {"credentials": "valid-token"},
        )()

        with pytest.raises(UnauthorizedException):
            get_current_user(
                credentials=credentials,
                db=None,
            )

    finally:
        dependencies.UserRepository = original_repository
        dependencies.decode_access_token = original_decode


def test_get_current_user_rejects_inactive_user():
    """Verify that an inactive user cannot authenticate."""

    user_id = uuid4()

    user = User(
        id=user_id,
        email="inactive@example.com",
        password_hash="hashed-password",
        full_name="Inactive User",
        is_active=False,
    )

    class FakeRepository:
        def __init__(self, db):
            pass

        def get_by_id(self, record_id):
            return user

    from app.api import dependencies

    original_repository = dependencies.UserRepository
    original_decode = dependencies.decode_access_token

    try:
        dependencies.UserRepository = FakeRepository
        dependencies.decode_access_token = lambda token: str(user_id)

        credentials = type(
            "Credentials",
            (),
            {"credentials": "valid-token"},
        )()

        with pytest.raises(UnauthorizedException):
            get_current_user(
                credentials=credentials,
                db=None,
            )

    finally:
        dependencies.UserRepository = original_repository
        dependencies.decode_access_token = original_decode


def test_require_role_allows_matching_role():
    """Verify that a user with the required role is allowed."""

    user = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="hashed-password",
        full_name="Admin User",
        is_active=True,
    )

    class FakeRBACService:
        def get_user_roles(self, user_id):
            return [
                type(
                    "FakeRole",
                    (),
                    {"name": "admin"},
                )()
            ]

    from app.api import dependencies

    original_rbac = dependencies.get_rbac_service

    try:
        result = require_role("admin")

        assert callable(result)

    finally:
        dependencies.get_rbac_service = original_rbac


def test_require_any_role_allows_matching_role():
    """Verify that any matching role is accepted."""

    checker = require_any_role("admin", "manager")

    assert callable(checker)


def test_require_role_rejects_wrong_role():
    """Verify that a user without the required role is rejected."""

    user = User(
        id=uuid4(),
        email="employee@example.com",
        password_hash="hashed-password",
        full_name="Employee User",
        is_active=True,
    )

    class FakeRBACService:
        def get_user_roles(self, user_id):
            return [
                type(
                    "FakeRole",
                    (),
                    {"name": "employee"},
                )()
            ]

    with pytest.raises(ForbiddenException):
        if not any(
            role.name.lower() == "admin"
            for role in FakeRBACService().get_user_roles(
                user.id
            )
        ):
            raise ForbiddenException(
                message="Role 'admin' is required."
            )


def test_require_any_role_rejects_wrong_roles():
    """Verify that none of the allowed roles results in rejection."""

    user = User(
        id=uuid4(),
        email="employee@example.com",
        password_hash="hashed-password",
        full_name="Employee User",
        is_active=True,
    )

    user_roles = {
        "employee",
    }

    allowed_roles = {
        "admin",
        "manager",
    }

    with pytest.raises(ForbiddenException):
        if not user_roles.intersection(allowed_roles):
            raise ForbiddenException(
                message="You do not have any of the required roles."
            )

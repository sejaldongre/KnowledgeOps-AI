from uuid import uuid4

import pytest

from app.core.exceptions import ForbiddenException
from app.models.document_permission import PermissionLevel
from app.services.document_permission import DocumentPermissionService


def test_direct_user_permission_allows_access():
    """A direct user permission should allow access."""

    service = DocumentPermissionService.__new__(
        DocumentPermissionService
    )

    user_id = uuid4()
    document_id = uuid4()

    service.permission_repository = type(
        "FakePermissionRepository",
        (),
        {
            "get_user_permission": lambda self, **kwargs: object(),
            "get_role_permission": lambda self, **kwargs: None,
        },
    )()

    service.rbac_service = type(
        "FakeRBACService",
        (),
        {
            "get_user_roles": lambda self, user_id: [],
        },
    )()

    assert service.has_permission(
        user_id=user_id,
        document_id=document_id,
        permission=PermissionLevel.VIEW,
    )


def test_role_permission_allows_access():
    """A permission inherited through a role should allow access."""

    service = DocumentPermissionService.__new__(
        DocumentPermissionService
    )

    user_id = uuid4()
    document_id = uuid4()
    role_id = uuid4()

    role = type("FakeRole", (), {"id": role_id})()

    service.permission_repository = type(
        "FakePermissionRepository",
        (),
        {
            "get_user_permission": lambda self, **kwargs: None,
            "get_role_permission": lambda self, **kwargs: object(),
        },
    )()

    service.rbac_service = type(
        "FakeRBACService",
        (),
        {
            "get_user_roles": lambda self, user_id: [role],
        },
    )()

    assert service.has_permission(
        user_id=user_id,
        document_id=document_id,
        permission=PermissionLevel.VIEW,
    )


def test_missing_permission_returns_false():
    """A user without direct or role permission should be denied."""

    service = DocumentPermissionService.__new__(
        DocumentPermissionService
    )

    user_id = uuid4()
    document_id = uuid4()

    service.permission_repository = type(
        "FakePermissionRepository",
        (),
        {
            "get_user_permission": lambda self, **kwargs: None,
            "get_role_permission": lambda self, **kwargs: None,
        },
    )()

    service.rbac_service = type(
        "FakeRBACService",
        (),
        {
            "get_user_roles": lambda self, user_id: [],
        },
    )()

    assert not service.has_permission(
        user_id=user_id,
        document_id=document_id,
        permission=PermissionLevel.VIEW,
    )


def test_require_permission_raises_forbidden():
    """require_permission should raise 403 when permission is missing."""

    service = DocumentPermissionService.__new__(
        DocumentPermissionService
    )

    service.permission_repository = type(
        "FakePermissionRepository",
        (),
        {
            "get_user_permission": lambda self, **kwargs: None,
            "get_role_permission": lambda self, **kwargs: None,
        },
    )()

    service.rbac_service = type(
        "FakeRBACService",
        (),
        {
            "get_user_roles": lambda self, user_id: [],
        },
    )()

    with pytest.raises(ForbiddenException):
        service.require_permission(
            user_id=uuid4(),
            document_id=uuid4(),
            permission=PermissionLevel.EDIT,
        )


def test_view_permission_does_not_grant_edit():
    """VIEW permission must not grant EDIT access."""

    service = DocumentPermissionService.__new__(
        DocumentPermissionService
    )

    service.permission_repository = type(
        "FakePermissionRepository",
        (),
        {
            "get_user_permission": (
                lambda self, **kwargs:
                object()
                if kwargs["permission"] == PermissionLevel.VIEW
                else None
            ),
            "get_role_permission": lambda self, **kwargs: None,
        },
    )()

    service.rbac_service = type(
        "FakeRBACService",
        (),
        {
            "get_user_roles": lambda self, user_id: [],
        },
    )()

    assert not service.has_permission(
        user_id=uuid4(),
        document_id=uuid4(),
        permission=PermissionLevel.EDIT,
    )


def test_view_permission_does_not_grant_delete():
    """VIEW permission must not grant DELETE access."""

    service = DocumentPermissionService.__new__(
        DocumentPermissionService
    )

    service.permission_repository = type(
        "FakePermissionRepository",
        (),
        {
            "get_user_permission": (
                lambda self, **kwargs:
                object()
                if kwargs["permission"] == PermissionLevel.VIEW
                else None
            ),
            "get_role_permission": lambda self, **kwargs: None,
        },
    )()

    service.rbac_service = type(
        "FakeRBACService",
        (),
        {
            "get_user_roles": lambda self, user_id: [],
        },
    )()

    assert not service.has_permission(
        user_id=uuid4(),
        document_id=uuid4(),
        permission=PermissionLevel.DELETE,
    )


def test_edit_permission_does_not_grant_delete():
    """EDIT permission must not grant DELETE access."""

    service = DocumentPermissionService.__new__(
        DocumentPermissionService
    )

    service.permission_repository = type(
        "FakePermissionRepository",
        (),
        {
            "get_user_permission": (
                lambda self, **kwargs:
                object()
                if kwargs["permission"] == PermissionLevel.EDIT
                else None
            ),
            "get_role_permission": lambda self, **kwargs: None,
        },
    )()

    service.rbac_service = type(
        "FakeRBACService",
        (),
        {
            "get_user_roles": lambda self, user_id: [],
        },
    )()

    assert not service.has_permission(
        user_id=uuid4(),
        document_id=uuid4(),
        permission=PermissionLevel.DELETE,
    )

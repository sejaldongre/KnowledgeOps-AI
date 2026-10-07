"""add unique document permission indexes

Revision ID: 068a6fac5024
Revises: 56e63263c566
Create Date: 2026-08-11 01:27:06.254694
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "068a6fac5024"
down_revision: Union[str, Sequence[str], None] = "56e63263c566"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique indexes for document permissions."""

    op.create_index(
        "uq_document_permission_user",
        "document_permissions",
        ["document_id", "user_id", "permission"],
        unique=True,
        postgresql_where=(
            "user_id IS NOT NULL"
        ),
    )

    op.create_index(
        "uq_document_permission_role",
        "document_permissions",
        ["document_id", "role_id", "permission"],
        unique=True,
        postgresql_where=(
            "role_id IS NOT NULL"
        ),
    )


def downgrade() -> None:
    """Remove unique document permission indexes."""

    op.drop_index(
        "uq_document_permission_role",
        table_name="document_permissions",
    )

    op.drop_index(
        "uq_document_permission_user",
        table_name="document_permissions",
    )

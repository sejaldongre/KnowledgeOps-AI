from app.models import Base


EXPECTED_TABLES = {
    "users",
    "roles",
    "user_roles",
    "documents",
    "document_versions",
    "folders",
    "tags",
    "document_tags",
    "document_permissions",
    "conversations",
    "messages",
    "audit_logs",
}


def test_expected_tables_are_registered():
    """Ensure all expected SQLAlchemy models are registered."""
    actual_tables = set(Base.metadata.tables.keys())

    assert EXPECTED_TABLES.issubset(actual_tables)

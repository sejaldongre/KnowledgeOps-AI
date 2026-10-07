from sqlalchemy import text

from app.infrastructure.database import engine


def test_database_connection():
    """Verify that the application can connect to PostgreSQL."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        assert result.scalar() == 1

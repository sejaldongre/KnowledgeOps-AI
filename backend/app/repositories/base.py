from typing import Generic, TypeVar
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing common database operations.
    """

    def __init__(self, model: type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get_by_id(self, record_id: int | UUID,) -> ModelType | None:
        """Return a record by its primary key."""

        statement = select(self.model).where(
            self.model.id == record_id
        )

        return self.db.scalar(statement)

    def get_all(self) -> list[ModelType]:
        """Return all records for the model."""

        statement = select(self.model)

        return list(self.db.scalars(statement).all())

    def delete(self, record: ModelType) -> None:
        """Delete a record from the database."""

        self.db.delete(record)

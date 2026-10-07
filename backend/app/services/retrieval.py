from dataclasses import dataclass
from uuid import UUID

from app.models.document_permission import PermissionLevel
from app.services.document_permission import (
    DocumentPermissionService,
)
from app.services.vector_store import ChromaVectorStore


@dataclass
class RetrievalResult:
    """Represent a retrieved document chunk."""

    chunk_id: str
    document_id: UUID
    document_version_id: UUID
    chunk_index: int
    text: str
    distance: float | None = None


class RetrievalService:
    """Retrieve permission-aware document chunks."""

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        permission_service: DocumentPermissionService,
    ) -> None:
        self.vector_store = vector_store
        self.permission_service = permission_service

    def search(
        self,
        *,
        query: str,
        user_id: UUID,
        limit: int = 5,
    ) -> list[RetrievalResult]:
        """Search for chunks the user is allowed to view."""

        if not query.strip():
            return []

        if limit <= 0:
            return []

        # Retrieve extra candidates because some results
        # may be removed by the document permission check.
        candidate_limit = min(limit * 3, 50)

        results = self.vector_store.search(
            query=query,
            limit=candidate_limit,
        )

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved: list[RetrievalResult] = []

        for index, chunk_id in enumerate(ids):
            metadata = metadatas[index]

            document_id = UUID(
                metadata["document_id"]
            )

            has_view_permission = (
                self.permission_service.has_permission(
                    user_id=user_id,
                    document_id=document_id,
                    permission=PermissionLevel.VIEW,
                )
            )

            if not has_view_permission:
                continue

            document_version_id = UUID(
                metadata["document_version_id"]
            )

            chunk_index = int(
                metadata["chunk_index"]
            )

            distance = None

            if distances and index < len(distances):
                distance = distances[index]

            retrieved.append(
                RetrievalResult(
                    chunk_id=str(chunk_id),
                    document_id=document_id,
                    document_version_id=(
                        document_version_id
                    ),
                    chunk_index=chunk_index,
                    text=documents[index],
                    distance=distance,
                )
            )

            if len(retrieved) >= limit:
                break

        return retrieved

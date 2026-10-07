import chromadb
from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions import (
    DefaultEmbeddingFunction,
)


class ChromaVectorStore:
    """Store and search document chunks using ChromaDB."""

    def __init__(
        self,
        path: str = "chroma_data",
        collection_name: str = "document_chunks",
        embedding_function: EmbeddingFunction | None = None,
    ) -> None:
        self.path = path
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=path
        )

        if embedding_function is None:
            embedding_function = DefaultEmbeddingFunction()

        self.embedding_function = embedding_function

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function,
            )
        )

    def add(
        self,
        *,
        chunk_id: str,
        document_id: str,
        document_version_id: str,
        chunk_index: int,
        text: str,
    ) -> None:
        """Store a document chunk and generate its embedding."""

        self.collection.upsert(
            ids=[chunk_id],
            documents=[text],
            metadatas=[
                {
                    "document_id": document_id,
                    "document_version_id": document_version_id,
                    "chunk_index": chunk_index,
                }
            ],
        )

    def search(
        self,
        *,
        query: str,
        limit: int = 5,
    ) -> dict:
        """Search for chunks semantically similar to a query."""

        return self.collection.query(
            query_texts=[query],
            n_results=limit,
        )

    def delete(
        self,
        chunk_id: str,
    ) -> None:
        """Delete a chunk from the vector store."""

        self.collection.delete(
            ids=[chunk_id]
        )

    def clear(self) -> None:
        """Remove all vectors from the collection."""

        self.client.delete_collection(
            name=self.collection_name
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )
        )

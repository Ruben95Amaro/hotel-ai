
from pathlib import Path

import chromadb

from app.services.embedding_service import EmbeddingService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / "chroma_db"


class RAGService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name="hotel_documents"
        )

    def add_chunks(self, chunks: list[str]) -> None:
        existing_ids = self.collection.get()["ids"]

        if existing_ids:
            self.collection.delete(ids=existing_ids)

        for index, chunk in enumerate(chunks):
            embedding = self.embedding_service.generate_embedding(chunk)

            self.collection.add(
                ids=[f"chunk_{index}"],
                documents=[chunk],
                embeddings=[embedding],
            )

    def search(self, query: str, limit: int = 3) -> list[dict]:
        if self.collection.count() == 0:
            return []

        embedding = self.embedding_service.generate_embedding(query)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(limit, self.collection.count()),
            include=["documents", "distances"],
        )

        documents = results["documents"][0] or []
        distances = results["distances"][0] or []

        return [
            {"document": document, "distance": distance}
            for document, distance in zip(documents, distances)
        ]

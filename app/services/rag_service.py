from pathlib import Path
import chromadb

from app.services.embedding_service import EmbeddingService
from app.settings.config import get_settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / "chroma_db"


class RAGService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self.embedding_service = EmbeddingService()

        if self._settings.testing:
            # Use in-memory client for testing
            self.client = chromadb.Client()
        else:
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_PATH)
            )

        self.collection = self.client.get_or_create_collection(
            name=self._settings.chroma_collection
        )

    async def add_chunks(self, chunks: list[str]) -> None:
        existing_ids = self.collection.get()["ids"]

        if existing_ids:
            self.collection.delete(ids=existing_ids)

        for index, chunk in enumerate(chunks):
            embedding = await self.embedding_service.generate_embedding(chunk)

            self.collection.add(
                ids=[f"chunk_{index}"],
                documents=[chunk],
                embeddings=[embedding],
            )

    async def search(self, query: str, limit: int | None = None) -> list[dict]:
        if self.collection.count() == 0:
            return []

        if limit is None:
            limit = self._settings.rag_search_limit

        embedding = await self.embedding_service.generate_embedding(query)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(limit, self.collection.count()),
            include=["documents", "distances"],
        )

        documents = results["documents"][0] or []
        distances = results["distances"][0] or []

        search_results = [
            {"document": document, "distance": distance}
            for document, distance in zip(documents, distances)
        ]
        
        # Debug: print search results
        print(f"[RAG DEBUG] query='{query}', limit={limit}, results={len(search_results)}")
        for r in search_results:
            print(f"[RAG DEBUG]   distance={r['distance']:.4f}, doc='{r['document'][:80]}'")
        
        return search_results

    def search_sync(self, query: str, limit: int | None = None) -> list[dict]:
        """Synchronous search for startup ingestion."""
        if self.collection.count() == 0:
            return []

        if limit is None:
            limit = self._settings.rag_search_limit

        embedding = self.embedding_service.generate_embedding_sync(query)

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
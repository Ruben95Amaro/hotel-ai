import chromadb

from app.services.embedding_service import EmbeddingService


class RAGService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="hotel_documents"
        )

    def add_chunks(self, chunks: list[str]) -> None:
        for index, chunk in enumerate(chunks):
            embedding = self.embedding_service.generate_embedding(chunk)

            self.collection.add(
                ids=[f"chunk_{index}"],
                documents=[chunk],
                embeddings=[embedding],
            )

    def search(
        self,
        query: str,
        limit: int = 3,
    ) -> list[str]:
        embedding = self.embedding_service.generate_embedding(query)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=limit,
        )

        return results["documents"][0]
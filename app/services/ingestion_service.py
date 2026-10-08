from app.services.document_service import DocumentService
from app.services.rag_service import RAGService


class IngestionService:
    def __init__(
        self,
        document_service: DocumentService,
        rag_service: RAGService,
    ) -> None:
        self.document_service = document_service
        self.rag_service = rag_service

    def ingest_document(self, file_path: str) -> None:
        text = self.document_service.load_document(
            file_path
        )

        chunks = self.document_service.split_into_chunks(
            text
        )

        self.rag_service.add_chunks(chunks)
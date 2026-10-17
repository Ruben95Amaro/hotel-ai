
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService


class ChatService:
    FALLBACK_RESPONSE = (
        "I don't have enough information to answer that question."
    )

    def __init__(
        self,
        llm_service: LLMService,
        rag_service: RAGService,
    ) -> None:
        self.llm_service = llm_service
        self.rag_service = rag_service

    @staticmethod
    def _get_documents(results: list[dict]) -> list[str]:
        return [
            result["document"]
            for result in results
            if result.get("document")
        ]

    @staticmethod
    def _find_check_in_time(documents: list[str]) -> str | None:
        for document in documents:
            for line in document.splitlines():
                normalized = line.strip().lower()

                if normalized.startswith("check-in starts at"):
                    return line.strip()

        return None

    def generate_response(self, message: str) -> str:
        results = self.rag_service.search(query=message, limit=3)
        documents = self._get_documents(results)

        question = message.lower()

        asks_about_check_in = (
            "check-in" in question
            or "check in" in question
            or "checkin" in question
        )

        if asks_about_check_in:
            check_in_time = self._find_check_in_time(documents)

            if check_in_time:
                return check_in_time

            # Search the relevant section directly if the first
            # semantic search did not return the check-in information.
            results = self.rag_service.search(
                query="Check-in and Check-out",
                limit=5,
            )
            documents = self._get_documents(results)

            check_in_time = self._find_check_in_time(documents)

            if check_in_time:
                return check_in_time

        if not documents:
            return self.FALLBACK_RESPONSE

        context = "\n\n".join(documents)

        prompt = f"""
You are the assistant for the Grand Ocean Hotel in Lisbon.

Answer the user's question using only the hotel context below.
Do not invent facts or ask which hotel the user means.
If the context does not contain the answer, respond exactly:
"{self.FALLBACK_RESPONSE}"

Hotel context:
{context}

User question:
{message}

Answer:
"""

        response = self.llm_service.generate_response(prompt)
        return response.strip() or self.FALLBACK_RESPONSE

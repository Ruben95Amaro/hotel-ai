from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.agent.tools.registry import ToolRegistry
from app.agent.agent_service import AgentService
from app.memory.factory import get_memory_store
from app.memory.models import Conversation
from app.settings.config import settings


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
        self._distance_threshold = settings.rag_distance_threshold
        
        # Initialize agent components
        self._tool_registry = ToolRegistry(rag_service)
        self._memory_store = get_memory_store()
        self._agent_service = AgentService(llm_service, self._tool_registry, self._memory_store)

    @staticmethod
    def _get_documents(results: list[dict]) -> list[str]:
        return [
            result["document"]
            for result in results
            if result.get("document")
        ]

    def _filter_relevant_results(self, results: list[dict]) -> list[dict]:
        """Filter results by distance threshold."""
        return [
            result for result in results
            if result.get("distance", 1.0) <= self._distance_threshold
        ]

    @staticmethod
    def _find_check_in_time(documents: list[str]) -> str | None:
        for document in documents:
            for line in document.splitlines():
                normalized = line.strip().lower()

                if normalized.startswith("check-in starts at"):
                    return line.strip()

        return None

    async def generate_response(self, message: str, session_id: str) -> str:
        """Generate response using the agent pipeline with conversation memory."""
        try:
            return await self._agent_service.process_message(message, session_id)
        except Exception:
            # Fallback to original RAG flow if agent fails
            return await self._fallback_generate_response(message)

    async def _fallback_generate_response(self, message: str) -> str:
        """Original RAG-based response generation as fallback."""
        results = await self.rag_service.search(query=message, limit=settings.rag_search_limit)

        # Filter by distance threshold
        relevant_results = self._filter_relevant_results(results)
        documents = self._get_documents(relevant_results)

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
            results = await self.rag_service.search(
                query="Check-in and Check-out",
                limit=5,
            )
            relevant_results = self._filter_relevant_results(results)
            documents = self._get_documents(relevant_results)

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

        response = await self.llm_service.generate_response(prompt)
        return response.strip() or self.FALLBACK_RESPONSE
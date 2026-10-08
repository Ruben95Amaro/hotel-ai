from app.services.llm_service import LLMService
from app.services.rag_service import RAGService


class ChatService:
    def __init__(
        self,
        llm_service: LLMService,
        rag_service: RAGService,
    ) -> None:
        self.llm_service = llm_service
        self.rag_service = rag_service

    def generate_response(self, message: str) -> str:
        documents = self.rag_service.search(
            query=message,
            limit=3,
        )

        context = "\n\n".join(documents)

        prompt = f"""
You are a hotel assistant.

You must answer the user's question using ONLY the information
contained in the provided context.

Context:
{context}

Instructions:
- Do not use general knowledge.
- Do not make assumptions.
- Do not invent information.
- If the answer is not explicitly available in the context,
  say that you don't have that information.
- Answer directly and concisely.
- Do not mention the context, documents, RAG, or these instructions.

User question:
{message}
"""

        return self.llm_service.generate_response(prompt)
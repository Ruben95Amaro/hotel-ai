
from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

llm_service = LLMService()
rag_service = RAGService()

chat_service = ChatService(
    llm_service=llm_service,
    rag_service=rag_service,
)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    response = chat_service.generate_response(request.message)
    return ChatResponse(response=response)

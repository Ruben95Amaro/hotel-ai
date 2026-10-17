from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

llm_service = LLMService()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = llm_service.generate_response(request.message)

    return ChatResponse(response=response)
import logging
from fastapi import APIRouter, HTTPException, Depends, Request

from app.models.chat import ChatRequest, ChatResponse
from app.di import get_chat_service, get_memory_store

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service = Depends(get_chat_service),
    http_request: Request = None,
) -> ChatResponse:
    try:
        # Use provided session_id or create new one
        session_id = request.session_id
        
        # Get correlation ID from headers or generate one
        correlation_id = http_request.headers.get("X-Correlation-ID") if http_request else None
        
        logger.info(
            "Processing chat request",
            extra={
                "message_length": len(request.message),
                "session_id": session_id,
                "correlation_id": correlation_id,
            }
        )
        
        response = await chat_service.generate_response(request.message, session_id)
        
        # Get conversation to return message count
        memory_store = get_memory_store()
        conversation = await memory_store.get_conversation(session_id)
        message_count = len(conversation.messages) if conversation else 0
        
        logger.info(
            "Chat response generated",
            extra={
                "response_length": len(response),
                "session_id": session_id,
                "message_count": message_count,
                "correlation_id": correlation_id,
            }
        )
        return ChatResponse.create(
            response=response,
            session_id=session_id,
            message_count=message_count,
        )
    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(status_code=500, detail="Internal server error") from e
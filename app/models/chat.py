from pydantic import BaseModel, Field
from typing import Optional
import uuid


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None, description="Conversation session ID. If not provided, a new session will be created.")


class ChatResponse(BaseModel):
    response: str
    session_id: str = Field(..., description="Conversation session ID")
    message_count: int = Field(default=0, description="Total messages in this conversation")
    
    @classmethod
    def create(cls, response: str, session_id: str | None = None, message_count: int = 0) -> "ChatResponse":
        if session_id is None:
            session_id = str(uuid.uuid4())
        return cls(response=response, session_id=session_id, message_count=message_count)
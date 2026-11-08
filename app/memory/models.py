from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """A single message in the conversation."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Conversation:
    """A conversation session with history."""
    session_id: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: MessageRole, content: str, metadata: dict | None = None) -> Message:
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.updated_at = datetime.utcnow()
        return msg
    
    def get_recent_messages(self, limit: int) -> list[Message]:
        return self.messages[-limit:] if limit > 0 else self.messages
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        conv = cls(
            session_id=data["session_id"],
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )
        return conv


class MemoryStore(ABC):
    """Abstract base class for conversation memory storage."""
    
    @abstractmethod
    async def get_conversation(self, session_id: str) -> Conversation | None:
        """Retrieve a conversation by session ID."""
        pass
    
    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> None:
        """Save or update a conversation."""
        pass
    
    @abstractmethod
    async def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation. Returns True if existed."""
        pass
    
    @abstractmethod
    async def list_sessions(self, limit: int = 100) -> list[str]:
        """List session IDs."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self, ttl_seconds: int) -> int:
        """Remove conversations older than TTL. Returns count removed."""
        pass
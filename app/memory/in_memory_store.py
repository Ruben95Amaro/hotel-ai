from app.memory.models import MemoryStore, Conversation
import asyncio
from typing import Any
import time


class InMemoryMemoryStore(MemoryStore):
    """In-memory conversation store for development and testing."""
    
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._lock = asyncio.Lock()
    
    async def get_conversation(self, session_id: str) -> Conversation | None:
        async with self._lock:
            return self._conversations.get(session_id)
    
    async def save_conversation(self, conversation: Conversation) -> None:
        async with self._lock:
            self._conversations[conversation.session_id] = conversation
    
    async def delete_conversation(self, session_id: str) -> bool:
        async with self._lock:
            if session_id in self._conversations:
                del self._conversations[session_id]
                return True
            return False
    
    async def list_sessions(self, limit: int = 100) -> list[str]:
        async with self._lock:
            sessions = list(self._conversations.keys())
            return sessions[:limit]
    
    async def cleanup_expired(self, ttl_seconds: int) -> int:
        async with self._lock:
            now = time.time()
            to_delete = []
            for session_id, conv in self._conversations.items():
                # Use updated_at for expiry
                age = now - conv.updated_at.timestamp()
                if age > ttl_seconds:
                    to_delete.append(session_id)
            
            for session_id in to_delete:
                del self._conversations[session_id]
            
            return len(to_delete)
    
    def get_stats(self) -> dict[str, Any]:
        """Get store statistics (for debugging)."""
        return {
            "total_conversations": len(self._conversations),
            "total_messages": sum(len(c.messages) for c in self._conversations.values()),
        }
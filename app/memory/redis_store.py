from app.memory.models import MemoryStore, Conversation
from app.settings.config import get_settings
from typing import Any
import json
import time


class RedisMemoryStore(MemoryStore):
    """Redis-backed conversation store for production."""
    
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = None
        self._prefix = "hotel_ai:conversation:"
    
    async def _get_client(self):
        """Lazy initialization of Redis client."""
        if self._client is None:
            try:
                import redis.asyncio as redis
                self._client = redis.from_url(
                    self._settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except ImportError:
                raise RuntimeError("redis-py not installed. Install with: pip install redis")
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Redis: {e}")
        return self._client
    
    def _key(self, session_id: str) -> str:
        return f"{self._prefix}{session_id}"
    
    async def get_conversation(self, session_id: str) -> Conversation | None:
        client = await self._get_client()
        data = await client.get(self._key(session_id))
        if data:
            return Conversation.from_dict(json.loads(data))
        return None
    
    async def save_conversation(self, conversation: Conversation) -> None:
        client = await self._get_client()
        data = json.dumps(conversation.to_dict())
        # Set TTL based on config (default 24 hours)
        ttl = getattr(self._settings, "conversation_ttl_seconds", 86400)
        await client.setex(self._key(conversation.session_id), ttl, data)
    
    async def delete_conversation(self, session_id: str) -> bool:
        client = await self._get_client()
        result = await client.delete(self._key(session_id))
        return result > 0
    
    async def list_sessions(self, limit: int = 100) -> list[str]:
        client = await self._get_client()
        pattern = f"{self._prefix}*"
        keys = []
        async for key in client.scan_iter(match=pattern, count=limit):
            session_id = key[len(self._prefix):]
            keys.append(session_id)
            if len(keys) >= limit:
                break
        return keys
    
    async def cleanup_expired(self, ttl_seconds: int) -> int:
        # Redis handles TTL automatically via setex
        # This is a no-op for Redis but kept for interface compatibility
        return 0
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
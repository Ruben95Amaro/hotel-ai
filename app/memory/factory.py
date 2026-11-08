from app.memory.models import MemoryStore
from app.memory.in_memory_store import InMemoryMemoryStore
from app.memory.redis_store import RedisMemoryStore
from app.settings.config import get_settings


def create_memory_store() -> MemoryStore:
    """Factory function to create the appropriate memory store based on configuration."""
    settings = get_settings()
    
    if settings.environment == "production" and getattr(settings, "redis_url", None):
        return RedisMemoryStore()
    
    return InMemoryMemoryStore()


# Global instance for dependency injection
_memory_store: MemoryStore | None = None


def get_memory_store() -> MemoryStore:
    """Get the global memory store instance."""
    global _memory_store
    if _memory_store is None:
        _memory_store = create_memory_store()
    return _memory_store


def set_memory_store(store: MemoryStore) -> None:
    """Set the global memory store (for testing)."""
    global _memory_store
    _memory_store = store
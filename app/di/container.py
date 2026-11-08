from dataclasses import dataclass, field
from typing import Optional

from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.agent.tools.registry import ToolRegistry
from app.agent.agent_service import AgentService
from app.services.chat_service import ChatService
from app.memory.factory import MemoryStore, create_memory_store
from app.db.postgres import PostgresDatabaseManager
from app.db.repositories import DatabaseManager, UserRepository, ReservationRepository
from app.settings.config import Settings, get_settings


@dataclass
class AppContainer:
    """Application dependency container."""
    
    settings: Settings = field(default_factory=get_settings)
    
    # Core services (singletons)
    _llm_service: Optional[LLMService] = field(default=None, init=False)
    _rag_service: Optional[RAGService] = field(default=None, init=False)
    _memory_store: Optional[MemoryStore] = field(default=None, init=False)
    _db_manager: Optional[DatabaseManager] = field(default=None, init=False)
    
    # Agent components (singletons)
    _tool_registry: Optional[ToolRegistry] = field(default=None, init=False)
    _agent_service: Optional[AgentService] = field(default=None, init=False)
    
    # Derived services
    _chat_service: Optional[ChatService] = field(default=None, init=False)
    
    @property
    def llm_service(self) -> LLMService:
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service
    
    @property
    def rag_service(self) -> RAGService:
        if self._rag_service is None:
            self._rag_service = RAGService()
        return self._rag_service
    
    @property
    def memory_store(self) -> MemoryStore:
        if self._memory_store is None:
            self._memory_store = create_memory_store()
        return self._memory_store
    
    @property
    def db_manager(self) -> DatabaseManager:
        if self._db_manager is None:
            self._db_manager = PostgresDatabaseManager()
        return self._db_manager
    
    @property
    def user_repository(self) -> UserRepository:
        return self.db_manager.user_repository
    
    @property
    def reservation_repository(self) -> ReservationRepository:
        return self.db_manager.reservation_repository
    
    @property
    def tool_registry(self) -> ToolRegistry:
        if self._tool_registry is None:
            self._tool_registry = ToolRegistry(self.rag_service)
        return self._tool_registry
    
    @property
    def agent_service(self) -> AgentService:
        if self._agent_service is None:
            self._agent_service = AgentService(
                llm_service=self.llm_service,
                tool_registry=self.tool_registry,
                memory_store=self.memory_store,
            )
        return self._agent_service
    
    @property
    def chat_service(self) -> ChatService:
        if self._chat_service is None:
            self._chat_service = ChatService(
                llm_service=self.llm_service,
                rag_service=self.rag_service,
            )
            # Replace the agent service with the one from container
            self._chat_service._agent_service = self.agent_service
            self._chat_service._memory_store = self.memory_store
        return self._chat_service
    
    async def initialize(self) -> None:
        """Initialize database connections."""
        await self.db_manager.initialize()
    
    async def close(self) -> None:
        """Close all resources."""
        # Close database connections
        if self._db_manager:
            await self._db_manager.close()
        # Close Redis connection if using RedisMemoryStore
        if self._memory_store and hasattr(self._memory_store, 'close'):
            await self._memory_store.close()
        self._db_manager = None
        self._memory_store = None
        self._llm_service = None
        self._rag_service = None
        self._tool_registry = None
        self._agent_service = None
        self._chat_service = None


# Global container instance
_container: Optional[AppContainer] = None


def get_container() -> AppContainer:
    """Get or create the global application container."""
    global _container
    if _container is None:
        _container = AppContainer()
    return _container


def set_container(container: AppContainer) -> None:
    """Set the global container (for testing)."""
    global _container
    _container = container


# FastAPI dependency functions
def get_llm_service() -> LLMService:
    return get_container().llm_service


def get_rag_service() -> RAGService:
    return get_container().rag_service


def get_memory_store() -> MemoryStore:
    return get_container().memory_store


def get_db_manager() -> DatabaseManager:
    return get_container().db_manager


def get_user_repository() -> UserRepository:
    return get_container().user_repository


def get_reservation_repository() -> ReservationRepository:
    return get_container().reservation_repository


def get_chat_service() -> ChatService:
    return get_container().chat_service
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    data: Any = None
    error: str | None = None


class Tool(ABC):
    """Base class for all agent tools."""
    
    # Optional: define action enums for tools that have an 'action' parameter
    ACTION_ENUMS: dict[str, list[str]] = {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM function calling."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given arguments."""
        pass
    
    def get_action_enums(self) -> dict[str, list[str]]:
        """Return action enums for this tool."""
        return self.ACTION_ENUMS
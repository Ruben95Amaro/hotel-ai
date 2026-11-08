from app.agent.tools.base import Tool, ToolResult
from app.agent.tools.search_docs import SearchHotelDocsTool
from app.agent.tools.hotel_services import GetHotelServicesTool
from app.agent.tools.availability import CheckAvailabilityTool
from app.agent.tools.escalate import EscalateToHumanTool
from app.agent.tools.booking import BookingManagementTool
from app.agent.tools.special_requests import SpecialRequestsTool
from app.agent.tools.hotel_info import HotelInfoTool
from app.agent.tools.database import (
    RegisterUserTool,
    GetUserTool,
    CreateReservationTool,
    GetReservationTool,
    ListUserReservationsTool,
    CancelReservationTool,
    ModifyReservationTool,
    CheckAvailabilityTool as DBCheckAvailabilityTool,
)
from app.services.rag_service import RAGService


class ToolRegistry:
    """Registry of all available tools."""
    
    def __init__(self, rag_service: RAGService) -> None:
        # Lazy import to avoid circular dependency
        from app.di import get_user_repository, get_reservation_repository
        
        user_repo = get_user_repository()
        reservation_repo = get_reservation_repository()
        
        self._tools: dict[str, Tool] = {
            "search_hotel_docs": SearchHotelDocsTool(rag_service),
            "get_hotel_services": GetHotelServicesTool(),
            "check_availability": CheckAvailabilityTool(),
            "escalate_to_human": EscalateToHumanTool(),
            "booking_management": BookingManagementTool(),
            "special_requests": SpecialRequestsTool(),
            "hotel_info": HotelInfoTool(),
            # Database tools
            "register_user": RegisterUserTool(user_repo),
            "get_user": GetUserTool(user_repo),
            "create_reservation": CreateReservationTool(reservation_repo, user_repo),
            "get_reservation": GetReservationTool(reservation_repo),
            "list_user_reservations": ListUserReservationsTool(reservation_repo),
            "cancel_reservation": CancelReservationTool(reservation_repo),
            "modify_reservation": ModifyReservationTool(reservation_repo),
            "check_availability_db": DBCheckAvailabilityTool(reservation_repo),
        }
    
    def get_tool(self, name: str) -> Tool | None:
        return self._tools.get(name)
    
    def get_all_tools(self) -> list[Tool]:
        return list(self._tools.values())
    
    def get_tool_descriptions(self) -> list[dict]:
        """Get tool descriptions in OpenAI function calling format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": self._get_tool_parameters(tool),
            }
            for tool in self._tools.values()
        ]
    
    def _get_tool_parameters(self, tool: Tool) -> dict:
        """Extract parameter schema from tool's execute method."""
        import inspect
        sig = inspect.signature(tool.execute)
        properties = {}
        required = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == list:
                param_type = "array"
            
            prop = {"type": param_type}
            
            # Add enum for action/category parameters if defined in tool
            action_enums = tool.get_action_enums()
            if name in action_enums:
                prop["enum"] = action_enums[name]
            
            properties[name] = prop
            if param.default == inspect.Parameter.empty:
                required.append(name)
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
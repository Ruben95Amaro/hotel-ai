from dataclasses import dataclass
from typing import Any
import json

from app.services.llm_service import LLMService
from app.agent.tools.registry import ToolRegistry


@dataclass
class ToolCall:
    """Represents a tool call decision."""
    tool_name: str
    arguments: dict[str, Any]
    reasoning: str


class IntentDetector:
    """Uses LLM to detect user intent and select appropriate tool."""
    
    def __init__(self, llm_service: LLMService, tool_registry: ToolRegistry) -> None:
        self._llm_service = llm_service
        self._tool_registry = tool_registry
    
    async def detect_intent(
        self,
        user_message: str,
        conversation_context: str = "No previous conversation.",
    ) -> ToolCall | None:
        """Detect intent and return tool call, or None if no tool needed."""
        tool_descriptions = self._tool_registry.get_tool_descriptions()
        
        prompt = f"""You are an intent detection system for a hotel assistant. 
Analyze the user's message and decide if a tool should be called.

Available tools:
{json.dumps(tool_descriptions, indent=2)}

Conversation context:
{conversation_context}

Current user message: "{user_message}"

Respond with a JSON object in this exact format:
{{
  "tool_name": "tool_name_or_null",
  "arguments": {{}},
  "reasoning": "brief explanation"
}}

Rules:
- If the user asks for general hotel info (rooms, facilities, policies) -> use search_hotel_docs or get_hotel_services
- If the user asks about availability/booking for specific dates -> use check_availability
- If the user asks to speak to a human or has a complex complaint -> use escalate_to_human
- If the user wants to manage a booking (view, cancel, modify) -> use booking_management
- If the user wants to make special requests -> use special_requests
- If the user asks for hotel info (contact, location, directions, attractions) -> use hotel_info
- If the user is just greeting or asking a simple question that doesn't need tools -> return null for tool_name
- Consider conversation context for follow-up questions
- Always provide reasoning
"""
        
        response = await self._llm_service.generate_response(prompt)
        
        # Debug: log the intent detection response
        print(f"[INTENT DEBUG] user='{user_message}'")
        print(f"[INTENT DEBUG] raw_response='{response}'")
        
        try:
            result = json.loads(response.strip())
            tool_name = result.get("tool_name")
            if tool_name is None:
                return None
            
            tool = self._tool_registry.get_tool(tool_name)
            if not tool:
                return None
            
            # Convert string numbers to int for known integer parameters
            arguments = result.get("arguments", {})
            if "limit" in arguments and isinstance(arguments["limit"], str):
                try:
                    arguments["limit"] = int(arguments["limit"])
                except ValueError:
                    pass
            if "guests" in arguments and isinstance(arguments["guests"], str):
                try:
                    arguments["guests"] = int(arguments["guests"])
                except ValueError:
                    pass
            
            tool_call = ToolCall(
                tool_name=tool_name,
                arguments=arguments,
                reasoning=result.get("reasoning", ""),
            )
            print(f"[INTENT DEBUG] tool='{tool_call.tool_name}', args={tool_call.arguments}, reasoning='{tool_call.reasoning}'")
            return tool_call
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: no tool call
            print(f"[INTENT DEBUG] parse error: {e}")
            return None
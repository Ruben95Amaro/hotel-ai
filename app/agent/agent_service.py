from app.agent.tools.base import ToolResult
from app.agent.tools.registry import ToolRegistry
from app.agent.intent_detector import IntentDetector, ToolCall
from app.memory.models import MemoryStore, Conversation, MessageRole
from app.settings.config import get_settings


class ToolExecutor:
    """Executes tools and handles results."""
    
    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry
    
    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call and return result."""
        tool = self._tool_registry.get_tool(tool_call.tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Unknown tool: {tool_call.tool_name}",
            )
        
        try:
            return await tool.execute(**tool_call.arguments)
        except Exception as e:
            return ToolResult(success=False, error=f"Tool execution failed: {e}")


class AgentService:
    """Main agent service that orchestrates intent detection, tool execution, and response generation."""
    
    def __init__(
        self,
        llm_service: "LLMService",
        tool_registry: ToolRegistry,
        memory_store: MemoryStore,
    ) -> None:
        self._llm_service = llm_service
        self._tool_registry = tool_registry
        self._memory_store = memory_store
        self._settings = get_settings()
        self._intent_detector = IntentDetector(llm_service, tool_registry)
        self._tool_executor = ToolExecutor(tool_registry)
    
    @property
    def _hotel_name(self) -> str:
        return self._settings.hotel_name
    
    @property
    def _hotel_location(self) -> str:
        return self._settings.hotel_location

    async def process_message(
        self,
        user_message: str,
        session_id: str,
    ) -> str:
        """Process a user message through the agent pipeline with conversation memory."""
        # Get or create conversation
        conversation = await self._memory_store.get_conversation(session_id)
        if conversation is None:
            conversation = Conversation(session_id=session_id)
        
        # Add user message to history
        conversation.add_message(MessageRole.USER, user_message)
        
        # Build conversation context for intent detection and response generation
        context_messages = conversation.get_recent_messages(
            self._settings.conversation_max_messages
        )
        conversation_context = self._format_conversation_context(context_messages)
        
        # Step 1: Detect intent (with conversation context)
        tool_call = await self._intent_detector.detect_intent(
            user_message, conversation_context
        )
        
        if tool_call is None:
            # No tool needed - generate direct response with context
            response = await self._generate_direct_response(
                user_message, conversation_context
            )
        else:
            # Step 2: Execute tool
            tool_result = await self._tool_executor.execute(tool_call)
            
            # Step 3: Generate response with tool result and context
            response = await self._generate_response_with_tool_result(
                user_message, tool_call, tool_result, conversation_context
            )
        
        # Add assistant response to history
        conversation.add_message(MessageRole.ASSISTANT, response)
        
        # Save conversation
        await self._memory_store.save_conversation(conversation)
        
        return response
    
    def _format_conversation_context(self, messages: list) -> str:
        """Format recent conversation messages for context."""
        if not messages:
            return "No previous conversation."
        
        formatted = []
        for msg in messages:
            role = "User" if msg.role == MessageRole.USER else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

    async def _generate_direct_response(
        self,
        user_message: str,
        conversation_context: str,
    ) -> str:
        """Generate response without using tools, using conversation context."""
        prompt = f"""You are the assistant for {self._hotel_name} in {self._hotel_location}.

Conversation history:
{conversation_context}

Answer the user's question in a helpful, friendly manner.
If you don't know the answer, say so honestly.

User question: {user_message}

Answer:"""
        return await self._llm_service.generate_response(prompt)
    
    async def _generate_response_with_tool_result(
        self,
        user_message: str,
        tool_call: ToolCall,
        tool_result: ToolResult,
        conversation_context: str,
    ) -> str:
        """Generate response incorporating tool execution result and conversation context."""
        if tool_result.success:
            result_text = f"Tool result: {tool_result.data}"
        else:
            result_text = f"Tool error: {tool_result.error}"
        
        prompt = f"""You are the assistant for {self._hotel_name} in {self._hotel_location}.

Conversation history:
{conversation_context}

The user asked: "{user_message}"

You called the tool "{tool_call.tool_name}" with arguments: {tool_call.arguments}
Reasoning: {tool_call.reasoning}

{result_text}

Now provide a helpful, natural response to the user based on this information.
If the tool failed, apologize and offer to help in another way.

Answer:"""
        return await self._llm_service.generate_response(prompt)
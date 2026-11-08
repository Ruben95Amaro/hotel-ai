from app.agent.tools.base import Tool, ToolResult
from app.services.rag_service import RAGService
from app.settings.config import get_settings


class SearchHotelDocsTool(Tool):
    """Tool to search hotel documentation via RAG."""
    
    def __init__(self, rag_service: RAGService) -> None:
        self._rag_service = rag_service
        self._settings = get_settings()
    
    @property
    def name(self) -> str:
        return "search_hotel_docs"
    
    @property
    def description(self) -> str:
        return "Search the hotel's documentation for information about rooms, facilities, policies, check-in/out times, etc."
    
    async def execute(self, query: str, limit: int | None = None) -> ToolResult:
        try:
            print(f"[SEARCH TOOL] query='{query}', threshold={self._settings.rag_distance_threshold}, limit={self._settings.rag_search_limit}")
            results = await self._rag_service.search(
                query=query,
                limit=limit or self._settings.rag_search_limit,
            )
            # Debug: log all distances
            print(f"[SEARCH TOOL] results={len(results)}")
            for r in results:
                print(f"[SEARCH TOOL]   distance={r.get('distance', 'N/A'):.4f}, doc='{r['document'][:80]}'")
            
            # Filter by distance threshold
            relevant = [
                r for r in results
                if r.get("distance", 1.0) <= self._settings.rag_distance_threshold
            ]
            print(f"[SEARCH TOOL] relevant={len(relevant)}")
            if not relevant:
                return ToolResult(
                    success=True,
                    data="I don't have that information in the hotel documentation.",
                )
            documents = [r["document"] for r in relevant]
            return ToolResult(success=True, data="\n\n".join(documents))
        except Exception as e:
            return ToolResult(success=False, error=str(e))
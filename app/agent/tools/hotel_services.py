from app.agent.tools.base import Tool, ToolResult
from app.settings.config import get_settings


class GetHotelServicesTool(Tool):
    """Tool to get structured list of hotel services and facilities."""
    
    ACTION_ENUMS = {
        "category": ["name", "location", "stars", "phone", "email", "rooms", "facilities", "policies"],
    }
    
    def __init__(self) -> None:
        self._settings = get_settings()
    
    @property
    def _hotel_name(self) -> str:
        return self._settings.hotel_name
    
    @property
    def _hotel_location(self) -> str:
        return self._settings.hotel_location
    
    @property
    def _hotel_stars(self) -> int:
        return self._settings.hotel_stars
    
    @property
    def _hotel_phone(self) -> str:
        return self._settings.hotel_phone
    
    @property
    def _hotel_email(self) -> str:
        return self._settings.hotel_email

    @property
    def name(self) -> str:
        return "get_hotel_services"
    
    @property
    def description(self) -> str:
        return "Get a structured list of all hotel services, room types, facilities, and policies."
    
    async def execute(self, category: str | None = None) -> ToolResult:
        try:
            hotel_info = {
                "name": self._hotel_name,
                "location": self._hotel_location,
                "stars": self._hotel_stars,
                "phone": self._hotel_phone,
                "email": self._hotel_email,
                "rooms": [
                    "Standard Room (max 2 guests)",
                    "Deluxe Room (max 2 guests)",
                    "Family Suite (max 4 guests)",
                ],
                "facilities": [
                    "Outdoor swimming pool",
                    "Fitness center",
                    "Restaurant",
                    "Bar",
                    "24-hour reception",
                    "Free Wi-Fi",
                    "Private parking (reservation required)",
                ],
                "policies": {
                    "check_in": "15:00",
                    "check_out": "11:00",
                    "cancellation": "Free cancellation up to 48 hours before arrival",
                    "pets": "Allowed in selected rooms (contact hotel to confirm)",
                }
            }
            
            # Category aliases for user-friendly queries
            category_aliases = {
                "room": "rooms",
                "room types": "rooms",
                "rooms": "rooms",
                "facility": "facilities",
                "facilities": "facilities",
                "amenity": "facilities",
                "amenities": "facilities",
                "policy": "policies",
                "policies": "policies",
            }
            
            if category:
                category = category.lower()
                # Resolve aliases
                category = category_aliases.get(category, category)
                if category in hotel_info:
                    return ToolResult(success=True, data={category: hotel_info[category]})
                return ToolResult(
                    success=False,
                    error=f"Unknown category: {category}. Available: {list(hotel_info.keys())}",
                )
            return ToolResult(success=True, data=hotel_info)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
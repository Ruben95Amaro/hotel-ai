from app.agent.tools.base import Tool, ToolResult
from app.settings.config import get_settings


class SpecialRequestsTool(Tool):
    """Tool to handle special requests and preferences."""
    
    ACTION_ENUMS = {
        "action": ["submit", "list_categories", "get_options"],
    }
    
    def __init__(self) -> None:
        self._settings = get_settings()
    
    @property
    def _hotel_name(self) -> str:
        return self._settings.hotel_name
    
    @property
    def _hotel_location(self) -> str:
        return self._settings.hotel_location
    
    # Predefined special request categories
    REQUEST_CATEGORIES = {
        "room_preference": {
            "description": "Room location or feature preferences",
            "options": [
                "High floor", "Low floor", "Near elevator", "Away from elevator",
                "Sea view", "City view", "Garden view", "Balcony", "Bathtub",
                "Walk-in shower", "Connecting rooms", "Accessible room",
            ],
        },
        "amenities": {
            "description": "Additional amenities or services",
            "options": [
                "Extra pillows", "Extra blankets", "Hypoallergenic bedding",
                "Baby crib", "Baby bathtub", "Bottle warmer",
                "Iron and ironing board", "Additional towels", "Bathrobes",
                "Slippers", "Mini-bar refill", "Fruit basket", "Flowers",
            ],
        },
        "accessibility": {
            "description": "Accessibility requirements",
            "options": [
                "Wheelchair accessible room", "Roll-in shower", "Grab bars",
                "Lowered closet rods", "Visual alarm", "TTY phone",
                "Service animal accommodation",
            ],
        },
        "arrival_departure": {
            "description": "Arrival and departure preferences",
            "options": [
                "Early check-in (subject to availability)",
                "Late check-out (subject to availability)",
                "Airport shuttle", "Luggage storage before check-in",
                "Luggage storage after check-out",
            ],
        },
        "celebration": {
            "description": "Special occasion arrangements",
            "options": [
                "Birthday setup", "Anniversary setup", "Honeymoon package",
                "Romantic dinner", "Cake arrangement", "Champagne on arrival",
            ],
        },
        "dietary": {
            "description": "Dietary requirements for hotel restaurant",
            "options": [
                "Vegetarian", "Vegan", "Gluten-free", "Halal", "Kosher",
                "Nut-free", "Dairy-free", "Low-sodium", "Diabetic-friendly",
            ],
        },
    }
    
    @property
    def name(self) -> str:
        return "special_requests"
    
    @property
    def description(self) -> str:
        return "Submit or inquire about special requests: room preferences, amenities, accessibility needs, arrival/departure arrangements, celebrations, or dietary requirements."
    
    async def execute(
        self,
        action: str,  # "submit", "list_categories", "get_options"
        category: str | None = None,
        requests: list[str] | None = None,
        guest_name: str | None = None,
        booking_id: str | None = None,
        notes: str | None = None,
    ) -> ToolResult:
        try:
            if action == "list_categories":
                categories = {
                    cat: info["description"]
                    for cat, info in self.REQUEST_CATEGORIES.items()
                }
                return ToolResult(success=True, data={
                    "categories": categories,
                    "note": f"Use 'get_options' with a category to see available options for {self._hotel_name}.",
                })
            
            elif action == "get_options":
                if not category:
                    return ToolResult(success=False, error="Category required for get_options action.")
                
                if category not in self.REQUEST_CATEGORIES:
                    return ToolResult(
                        success=False,
                        error=f"Unknown category: {category}. Available: {list(self.REQUEST_CATEGORIES.keys())}",
                    )
                
                return ToolResult(success=True, data={
                    "category": category,
                    "description": self.REQUEST_CATEGORIES[category]["description"],
                    "options": self.REQUEST_CATEGORIES[category]["options"],
                    "note": f"These are common options for {self._hotel_name}. Custom requests are also welcome.",
                })
            
            elif action == "submit":
                if not requests:
                    return ToolResult(success=False, error="At least one request is required for submission.")
                
                if not guest_name:
                    return ToolResult(success=False, error="Guest name is required for submitting special requests.")
                
                # In production, this would save to a database linked to the booking
                request_id = f"SR-{hash(f'{guest_name}{booking_id}{requests}') % 100000:05d}"
                
                return ToolResult(success=True, data={
                    "request_id": request_id,
                    "guest_name": guest_name,
                    "booking_id": booking_id,
                    "requests": requests,
                    "notes": notes,
                    "status": "submitted",
                    "message": f"Your special requests have been forwarded to {self._hotel_name} staff. They will do their best to accommodate them.",
                    "note": "This is a mock submission. No real request has been logged. Special requests are subject to availability and may incur additional charges.",
                })
            
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}. Available: submit, list_categories, get_options")
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))
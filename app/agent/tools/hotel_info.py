from app.agent.tools.base import Tool, ToolResult
from app.settings.config import get_settings


class HotelInfoTool(Tool):
    """Tool to provide comprehensive hotel information."""
    
    ACTION_ENUMS = {
        "category": ["overview", "contact", "location", "directions", "attractions", "policies"],
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
        return "hotel_info"
    
    @property
    def description(self) -> str:
        return "Get comprehensive hotel information: contact details, location, directions, nearby attractions, policies, and general overview."
    
    async def execute(
        self,
        category: str | None = None,  # "contact", "location", "directions", "attractions", "policies", "overview"
    ) -> ToolResult:
        try:
            hotel_info = {
                "overview": {
                    "name": self._hotel_name,
                    "location": self._hotel_location,
                    "stars": self._hotel_stars,
                    "description": f"Welcome to {self._hotel_name}, a {self._hotel_stars}-star hotel in the heart of {self._hotel_location}. We offer comfortable accommodations, modern amenities, and exceptional service for both leisure and business travelers.",
                    "check_in": "15:00",
                    "check_out": "11:00",
                    "languages_spoken": ["English", "Portuguese", "Spanish", "French"],
                    "currencies_accepted": ["EUR"],
                },
                "contact": {
                    "phone": self._hotel_phone,
                    "email": self._hotel_email,
                    "website": f"https://{self._hotel_name.lower().replace(' ', '')}.com",
                    "address": f"{self._hotel_name}, {self._hotel_location}, Portugal",
                    "reception_hours": "24/7",
                },
                "location": {
                    "address": f"{self._hotel_name}, {self._hotel_location}, Portugal",
                    "coordinates": {"lat": 38.7223, "lng": -9.1393},  # Lisbon coordinates
                    "distance_to": {
                        "city_center_km": 2.5,
                        "airport_km": 7.0,
                        "train_station_km": 3.0,
                        "beach_km": 15.0,
                    },
                    "public_transport": [
                        "Metro: Blue Line (5 min walk)",
                        "Bus: Routes 728, 729, 759 (2 min walk)",
                        "Taxi stand: 1 min walk",
                    ],
                },
                "directions": {
                    "from_airport": "Take the Metro Red Line to Alameda, transfer to Blue Line to Restauradores. Hotel is 5 min walk. Or taxi (15 min, ~€15-20).",
                    "from_train_station": "From Santa Apolónia: Metro Blue Line to Restauradores (10 min). From Oriente: Metro Red Line to Alameda, transfer to Blue Line (25 min).",
                    "by_car": "From A1: Follow signs to Lisbon Center. Take exit to Av. da Liberdade. Hotel has private parking (reservation required).",
                },
                "attractions": {
                    "nearby": [
                        {"name": "Rossio Square", "distance_km": 0.5, "walk_time_min": 6},
                        {"name": "Praça do Comércio", "distance_km": 0.8, "walk_time_min": 10},
                        {"name": "Santa Justa Lift", "distance_km": 0.6, "walk_time_min": 7},
                        {"name": "Carmo Convent", "distance_km": 0.7, "walk_time_min": 8},
                        {"name": "Rossio Train Station", "distance_km": 0.4, "walk_time_min": 5},
                    ],
                    "popular": [
                        {"name": "Belém Tower", "distance_km": 6.5, "transport": "Tram 15E (30 min)"},
                        {"name": "Jerónimos Monastery", "distance_km": 6.8, "transport": "Tram 15E (30 min)"},
                        {"name": "São Jorge Castle", "distance_km": 2.0, "transport": "Tram 28E (15 min) + walk"},
                        {"name": "Alfama District", "distance_km": 1.5, "transport": "Walk (20 min) or Tram 28E"},
                        {"name": "Parque das Nações", "distance_km": 8.0, "transport": "Metro Red Line (20 min)"},
                    ],
                },
                "policies": {
                    "check_in": "15:00 (24-hour reception available for earlier luggage storage)",
                    "check_out": "11:00 (late check-out available on request, subject to availability)",
                    "cancellation": "Free cancellation up to 48 hours before arrival. Within 48 hours: 1 night charge.",
                    "children": "Children of all ages welcome. Cots available on request (free). Extra beds: €30/night.",
                    "pets": "Allowed in selected rooms only. Additional €15/night. Must be pre-arranged.",
                    "smoking": "Strictly non-smoking property. Designated outdoor smoking area available.",
                    "parties": "Parties/events not permitted in rooms.",
                    "payment": "Credit cards accepted (Visa, Mastercard, Amex). Pre-authorization at check-in.",
                },
            }
            
            if category:
                category = category.lower()
                if category in hotel_info:
                    return ToolResult(success=True, data={category: hotel_info[category]})
                return ToolResult(
                    success=False,
                    error=f"Unknown category: {category}. Available: {list(hotel_info.keys())}",
                )
            
            return ToolResult(success=True, data=hotel_info)
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))
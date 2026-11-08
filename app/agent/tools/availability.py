from app.agent.tools.base import Tool, ToolResult
from datetime import datetime, timedelta
import random


class CheckAvailabilityTool(Tool):
    """Tool to check room availability (mock implementation)."""
    
    ACTION_ENUMS = {
        "room_type": ["Standard Room", "Deluxe Room", "Family Suite"],
    }
    
    # Room configuration with realistic hotel data
    ROOM_CONFIG = {
        "Standard Room": {
            "base_price": 120,
            "max_guests": 2,
            "size_sqm": 20,
            "beds": "1 double bed",
            "amenities": ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Private bathroom", "City view"],
        },
        "Deluxe Room": {
            "base_price": 180,
            "max_guests": 2,
            "size_sqm": 30,
            "beds": "1 king-size bed",
            "amenities": ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Private bathroom", "City view", "Mini-bar", "Sitting area"],
        },
        "Family Suite": {
            "base_price": 280,
            "max_guests": 4,
            "size_sqm": 50,
            "beds": "1 king-size bed + 2 single beds",
            "amenities": ["Free Wi-Fi", "Air conditioning", "Flat-screen TV", "Private bathroom", "Sea view", "Mini-bar", "Living area", "Balcony"],
        },
    }
    
    @property
    def name(self) -> str:
        return "check_availability"
    
    @property
    def description(self) -> str:
        return "Check room availability for specific dates. Returns mock data until real integration exists. Provide check_in and check_out in YYYY-MM-DD format, optional room_type, and number of guests."
    
    def _validate_dates(self, check_in: str, check_out: str) -> tuple[datetime.date, datetime.date] | tuple[None, None, str]:
        """Validate and parse dates. Returns (check_in_date, check_out_date, error) or (None, None, error)."""
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return None, None, "Invalid date format. Use YYYY-MM-DD."
        
        if check_in_date >= check_out_date:
            return None, None, "Check-out must be after check-in."
        
        if check_in_date < datetime.now().date():
            return None, None, "Check-in date cannot be in the past."
        
        # Optional: limit how far in the future bookings can be made
        max_future = datetime.now().date() + timedelta(days=365)
        if check_in_date > max_future:
            return None, None, f"Check-in date cannot be more than 1 year in the future."
        
        return check_in_date, check_out_date, None
    
    def _calculate_availability(self, room_type: str, check_in_date: datetime.date, check_out_date: datetime.date, seed: int | None = None) -> dict:
        """Calculate mock availability for a room type. Uses deterministic pseudo-random based on dates."""
        if seed is not None:
            random.seed(seed)
        
        # Deterministic "randomness" based on room type and dates
        # This ensures consistent results for the same query
        hash_input = f"{room_type}{check_in_date}{check_out_date}"
        seed_value = hash(hash_input) % 10000
        random.seed(seed_value)
        
        config = self.ROOM_CONFIG[room_type]
        nights = (check_out_date - check_in_date).days
        
        # 75% chance of availability (higher than before)
        is_available = random.random() < 0.75
        
        if is_available:
            # Add some price variation (±10%)
            price_variation = random.uniform(0.9, 1.1)
            price_per_night = round(config["base_price"] * price_variation)
            
            return {
                "room_type": room_type,
                "available": True,
                "price_per_night": price_per_night,
                "total_price": price_per_night * nights,
                "max_guests": config["max_guests"],
                "size_sqm": config["size_sqm"],
                "beds": config["beds"],
                "amenities": config["amenities"],
                "nights": nights,
            }
        else:
            return {
                "room_type": room_type,
                "available": False,
                "reason": "Fully booked for these dates",
            }
    
    async def execute(
        self,
        check_in: str,
        check_out: str,
        room_type: str | None = None,
        guests: int = 1,
    ) -> ToolResult:
        try:
            # Validate dates
            check_in_date, check_out_date, error = self._validate_dates(check_in, check_out)
            if error:
                return ToolResult(success=False, error=error)
            
            # Validate room_type if provided
            available_room_types = list(self.ROOM_CONFIG.keys())
            if room_type and room_type not in available_room_types:
                return ToolResult(
                    success=False,
                    error=f"Unknown room type: '{room_type}'. Available types: {available_room_types}",
                )
            
            # Validate guests
            if guests < 1:
                return ToolResult(success=False, error="Number of guests must be at least 1.")
            
            # If specific room_type requested, check if it accommodates the guests
            if room_type:
                max_guests = self.ROOM_CONFIG[room_type]["max_guests"]
                if guests > max_guests:
                    return ToolResult(
                        success=False,
                        error=f"{room_type} accommodates maximum {max_guests} guests. Requested: {guests}.",
                    )
            
            # Check availability for requested room type(s)
            rooms_to_check = [room_type] if room_type else available_room_types
            
            available_rooms = []
            for rt in rooms_to_check:
                # Skip room types that can't accommodate the guests
                if guests > self.ROOM_CONFIG[rt]["max_guests"]:
                    available_rooms.append({
                        "room_type": rt,
                        "available": False,
                        "reason": f"Only accommodates {self.ROOM_CONFIG[rt]['max_guests']} guests",
                    })
                    continue
                
                availability = self._calculate_availability(rt, check_in_date, check_out_date)
                available_rooms.append(availability)
            
            # Reset random seed
            random.seed()
            
            # Check if any rooms are available
            any_available = any(r.get("available", False) for r in available_rooms)
            
            return ToolResult(success=True, data={
                "check_in": check_in,
                "check_out": check_out,
                "nights": (check_out_date - check_in_date).days,
                "guests": guests,
                "rooms": available_rooms,
                "any_available": any_available,
                "note": "This is mock data. Real booking integration not yet implemented. Availability is simulated and not guaranteed.",
            })
        except Exception as e:
            random.seed()  # Reset seed on error
            return ToolResult(success=False, error=str(e))
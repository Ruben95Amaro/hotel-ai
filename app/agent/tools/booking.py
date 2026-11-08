from app.agent.tools.base import Tool, ToolResult
from datetime import datetime
import hashlib


class BookingManagementTool(Tool):
    """Tool to manage mock bookings (view, cancel, modify)."""
    
    ACTION_ENUMS = {
        "action": ["create", "view", "cancel", "modify"],
    }
    
    # In-memory storage for mock bookings (in production, this would be a database)
    _bookings: dict[str, dict] = {}
    
    @property
    def name(self) -> str:
        return "booking_management"
    
    @property
    def description(self) -> str:
        return "Manage hotel bookings: view booking details, cancel a booking, or modify dates. Requires booking reference or guest details."
    
    def _generate_booking_id(self, guest_name: str, check_in: str) -> str:
        """Generate a deterministic booking ID."""
        hash_input = f"{guest_name}{check_in}{datetime.now().isoformat()}"
        return f"BK-{hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()}"
    
    def _create_mock_booking(self, guest_name: str, email: str, check_in: str, check_out: str, room_type: str, guests: int) -> dict:
        """Create a mock booking entry."""
        booking_id = self._generate_booking_id(guest_name, check_in)
        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        
        base_prices = {"Standard Room": 120, "Deluxe Room": 180, "Family Suite": 280}
        price = base_prices.get(room_type, 150)
        
        return {
            "booking_id": booking_id,
            "guest_name": guest_name,
            "email": email,
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "room_type": room_type,
            "guests": guests,
            "price_per_night": price,
            "total_price": price * nights,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "special_requests": [],
        }
    
    async def execute(
        self,
        action: str,  # "view", "cancel", "modify", "create"
        booking_id: str | None = None,
        guest_name: str | None = None,
        email: str | None = None,
        check_in: str | None = None,
        check_out: str | None = None,
        room_type: str | None = None,
        guests: int | None = None,
        new_check_in: str | None = None,
        new_check_out: str | None = None,
        new_room_type: str | None = None,
    ) -> ToolResult:
        try:
            if action == "create":
                # Create a new mock booking
                if not all([guest_name, email, check_in, check_out, room_type, guests]):
                    return ToolResult(
                        success=False,
                        error="Missing required fields for booking creation: guest_name, email, check_in, check_out, room_type, guests",
                    )
                
                # Validate dates
                try:
                    ci = datetime.strptime(check_in, "%Y-%m-%d").date()
                    co = datetime.strptime(check_out, "%Y-%m-%d").date()
                except ValueError:
                    return ToolResult(success=False, error="Invalid date format. Use YYYY-MM-DD.")
                
                if ci >= co:
                    return ToolResult(success=False, error="Check-out must be after check-in.")
                if ci < datetime.now().date():
                    return ToolResult(success=False, error="Check-in date cannot be in the past.")
                
                booking = self._create_mock_booking(guest_name, email, check_in, check_out, room_type, guests)
                self._bookings[booking["booking_id"]] = booking
                
                return ToolResult(success=True, data={
                    "message": "Booking created successfully (mock)",
                    "booking": booking,
                    "note": "This is a mock booking. No real reservation has been made.",
                })
            
            # For view, cancel, modify - need to find the booking
            if not booking_id:
                # Try to find by guest details
                if not guest_name or not email:
                    return ToolResult(
                        success=False,
                        error="Booking ID or guest name + email required to find booking.",
                    )
                
                # Find booking by guest details
                matches = [
                    b for b in self._bookings.values()
                    if b["guest_name"].lower() == guest_name.lower() and b["email"].lower() == email.lower()
                ]
                
                if not matches:
                    return ToolResult(
                        success=False,
                        error="No booking found for the provided details.",
                    )
                
                if len(matches) > 1:
                    return ToolResult(
                        success=False,
                        error=f"Multiple bookings found. Please provide booking ID. Found: {[b['booking_id'] for b in matches]}",
                    )
                
                booking = matches[0]
                booking_id = booking["booking_id"]
            else:
                booking = self._bookings.get(booking_id)
                if not booking:
                    return ToolResult(success=False, error=f"Booking {booking_id} not found.")
            
            if action == "view":
                return ToolResult(success=True, data={
                    "booking": booking,
                    "note": "This is mock data. No real booking system integration.",
                })
            
            elif action == "cancel":
                if booking["status"] == "cancelled":
                    return ToolResult(success=False, error="Booking is already cancelled.")
                
                booking["status"] = "cancelled"
                booking["cancelled_at"] = datetime.now().isoformat()
                
                return ToolResult(success=True, data={
                    "message": f"Booking {booking_id} has been cancelled (mock).",
                    "booking": booking,
                    "note": "This is a mock cancellation. No real reservation has been cancelled.",
                })
            
            elif action == "modify":
                # Validate new dates if provided
                if new_check_in or new_check_out:
                    ci = new_check_in or booking["check_in"]
                    co = new_check_out or booking["check_out"]
                    try:
                        ci_date = datetime.strptime(ci, "%Y-%m-%d").date()
                        co_date = datetime.strptime(co, "%Y-%m-%d").date()
                    except ValueError:
                        return ToolResult(success=False, error="Invalid date format. Use YYYY-MM-DD.")
                    
                    if ci_date >= co_date:
                        return ToolResult(success=False, error="Check-out must be after check-in.")
                    if ci_date < datetime.now().date():
                        return ToolResult(success=False, error="Check-in date cannot be in the past.")
                    
                    booking["check_in"] = ci
                    booking["check_out"] = co
                    booking["nights"] = (co_date - ci_date).days
                
                if new_room_type:
                    if new_room_type not in ["Standard Room", "Deluxe Room", "Family Suite"]:
                        return ToolResult(success=False, error=f"Unknown room type: {new_room_type}")
                    booking["room_type"] = new_room_type
                
                booking["modified_at"] = datetime.now().isoformat()
                
                return ToolResult(success=True, data={
                    "message": f"Booking {booking_id} has been modified (mock).",
                    "booking": booking,
                    "note": "This is a mock modification. No real reservation has been changed.",
                })
            
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}. Available: create, view, cancel, modify")
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))
"""
Database tools for the agent.
Tools for user registration and reservation management.
"""
from app.agent.tools.base import Tool, ToolResult
from app.db.repositories import UserRepository, ReservationRepository
from app.db.models import User, Reservation, RoomType, ReservationStatus
from app.settings.config import get_settings
from datetime import datetime
from typing import Optional
import uuid


class RegisterUserTool(Tool):
    """Tool to register a new hotel guest."""

    name = "register_user"
    description = (
        "Register a new hotel guest. "
        "Parameters: email (str, required), full_name (str, required), "
        "phone (str, optional), document_id (str, optional), nationality (str, optional). "
        "Returns the created user with ID."
    )

    def __init__(self, user_repository: UserRepository):
        self._user_repo = user_repository

    async def execute(self, **kwargs) -> ToolResult:
        email = kwargs.get("email")
        full_name = kwargs.get("full_name")
        phone = kwargs.get("phone", "")
        document_id = kwargs.get("document_id", "")
        nationality = kwargs.get("nationality", "")

        if not email or not full_name:
            return ToolResult(
                success=False,
                error="Email and full_name are required",
            )

        # Check if user already exists
        existing = await self._user_repo.get_by_email(email)
        if existing:
            return ToolResult(
                success=False,
                error=f"User with email {email} already exists",
                data={"user_id": existing.id},
            )

        existing_doc = await self._user_repo.get_by_document_id(document_id)
        if existing_doc and document_id:
            return ToolResult(
                success=False,
                error=f"User with document ID {document_id} already exists",
                data={"user_id": existing_doc.id},
            )

        # Create new user
        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            document_id=document_id,
            nationality=nationality,
        )

        created_user = await self._user_repo.create(user)

        return ToolResult(
            success=True,
            data={
                "user_id": created_user.id,
                "email": created_user.email,
                "full_name": created_user.full_name,
                "message": f"User {created_user.full_name} registered successfully",
            },
        )


class GetUserTool(Tool):
    """Tool to retrieve user information."""

    name = "get_user"
    description = (
        "Get user information by ID, email, or document ID. "
        "Parameters: user_id (str, optional), email (str, optional), document_id (str, optional). "
        "At least one parameter is required."
    )

    def __init__(self, user_repository: UserRepository):
        self._user_repo = user_repository

    async def execute(self, **kwargs) -> ToolResult:
        user_id = kwargs.get("user_id")
        email = kwargs.get("email")
        document_id = kwargs.get("document_id")

        if not any([user_id, email, document_id]):
            return ToolResult(
                success=False,
                error="At least one of user_id, email, or document_id is required",
            )

        user = None
        if user_id:
            user = await self._user_repo.get_by_id(user_id)
        elif email:
            user = await self._user_repo.get_by_email(email)
        elif document_id:
            user = await self._user_repo.get_by_document_id(document_id)

        if not user:
            return ToolResult(
                success=False,
                error="User not found",
            )

        return ToolResult(
            success=True,
            data={
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "document_id": user.document_id,
                "nationality": user.nationality,
                "preferences": user.preferences,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
        )


class CreateReservationTool(Tool):
    """Tool to create a new hotel reservation."""

    name = "create_reservation"
    description = (
        "Create a new hotel reservation. "
        "Parameters: user_id (str, required), room_type (str: standard/deluxe/suite/presidential, required), "
        "check_in (str: YYYY-MM-DD, required), check_out (str: YYYY-MM-DD, required), "
        "guests (int, optional, default=1), special_requests (str, optional). "
        "Returns the created reservation with confirmation code."
    )

    def __init__(self, reservation_repository: ReservationRepository, user_repository: UserRepository):
        self._reservation_repo = reservation_repository
        self._user_repo = user_repository

    async def execute(self, **kwargs) -> ToolResult:
        user_id = kwargs.get("user_id")
        room_type_str = kwargs.get("room_type")
        check_in_str = kwargs.get("check_in")
        check_out_str = kwargs.get("check_out")
        guests = kwargs.get("guests", 1)
        special_requests = kwargs.get("special_requests", "")

        if not all([user_id, room_type_str, check_in_str, check_out_str]):
            return ToolResult(
                success=False,
                error="user_id, room_type, check_in, and check_out are required",
            )

        # Validate user exists
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return ToolResult(
                success=False,
                error=f"User with ID {user_id} not found",
            )

        # Parse dates
        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d")
        except ValueError:
            return ToolResult(
                success=False,
                error="Invalid date format. Use YYYY-MM-DD",
            )

        if check_in >= check_out:
            return ToolResult(
                success=False,
                error="Check-out must be after check-in",
            )

        if check_in < datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0):
            return ToolResult(
                success=False,
                error="Check-in cannot be in the past",
            )

        # Parse room type
        try:
            room_type = RoomType(room_type_str.lower())
        except ValueError:
            return ToolResult(
                success=False,
                error=f"Invalid room type. Use: standard, deluxe, suite, presidential",
            )

        # Check availability
        available = await self._reservation_repo.check_availability(room_type, check_in, check_out)
        if available <= 0:
            return ToolResult(
                success=False,
                error=f"No {room_type.value} rooms available for those dates",
            )

        # Calculate price (mock pricing)
        nights = (check_out - check_in).days
        price_per_night = {
            RoomType.STANDARD: 150.0,
            RoomType.DELUXE: 250.0,
            RoomType.SUITE: 400.0,
            RoomType.PRESIDENTIAL: 800.0,
        }
        total_price = nights * price_per_night.get(room_type, 150.0)

        # Create reservation
        reservation = Reservation(
            user_id=user_id,
            room_type=room_type,
            check_in=check_in,
            check_out=check_out,
            status=ReservationStatus.CONFIRMED,
            guests=guests,
            special_requests=special_requests,
            total_price=total_price,
        )

        created = await self._reservation_repo.create(reservation)

        return ToolResult(
            success=True,
            data={
                "reservation_id": created.id,
                "confirmation_code": created.confirmation_code,
                "user_id": created.user_id,
                "room_type": created.room_type.value,
                "check_in": created.check_in.strftime("%Y-%m-%d"),
                "check_out": created.check_out.strftime("%Y-%m-%d"),
                "guests": created.guests,
                "nights": created.nights,
                "total_price": created.total_price,
                "status": created.status.value,
                "special_requests": created.special_requests,
                "message": f"Reservation confirmed! Confirmation code: {created.confirmation_code}",
            },
        )


class GetReservationTool(Tool):
    """Tool to retrieve reservation information."""

    name = "get_reservation"
    description = (
        "Get reservation by ID or confirmation code. "
        "Parameters: reservation_id (str, optional), confirmation_code (str, optional). "
        "At least one parameter is required."
    )

    def __init__(self, reservation_repository: ReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, **kwargs) -> ToolResult:
        reservation_id = kwargs.get("reservation_id")
        confirmation_code = kwargs.get("confirmation_code")

        if not any([reservation_id, confirmation_code]):
            return ToolResult(
                success=False,
                error="At least one of reservation_id or confirmation_code is required",
            )

        reservation = None
        if reservation_id:
            reservation = await self._reservation_repo.get_by_id(reservation_id)
        elif confirmation_code:
            reservation = await self._reservation_repo.get_by_confirmation_code(confirmation_code)

        if not reservation:
            return ToolResult(
                success=False,
                error="Reservation not found",
            )

        return ToolResult(
            success=True,
            data={
                "reservation_id": reservation.id,
                "confirmation_code": reservation.confirmation_code,
                "user_id": reservation.user_id,
                "room_type": reservation.room_type.value,
                "check_in": reservation.check_in.strftime("%Y-%m-%d"),
                "check_out": reservation.check_out.strftime("%Y-%m-%d"),
                "guests": reservation.guests,
                "nights": reservation.nights,
                "total_price": reservation.total_price,
                "status": reservation.status.value,
                "special_requests": reservation.special_requests,
                "created_at": reservation.created_at.isoformat() if reservation.created_at else None,
            },
        )


class ListUserReservationsTool(Tool):
    """Tool to list reservations for a user."""

    name = "list_user_reservations"
    description = (
        "List all reservations for a user. "
        "Parameters: user_id (str, required), status (str: pending/confirmed/checked_in/checked_out/cancelled/no_show, optional), "
        "upcoming_only (bool, optional, default=false)."
    )

    def __init__(self, reservation_repository: ReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, **kwargs) -> ToolResult:
        user_id = kwargs.get("user_id")
        status_str = kwargs.get("status")
        upcoming_only = kwargs.get("upcoming_only", False)

        if not user_id:
            return ToolResult(
                success=False,
                error="user_id is required",
            )

        status = None
        if status_str:
            try:
                status = ReservationStatus(status_str.lower())
            except ValueError:
                return ToolResult(
                    success=False,
                    error=f"Invalid status. Use: pending, confirmed, checked_in, checked_out, cancelled, no_show",
                )

        reservations = await self._reservation_repo.get_by_user_id(
            user_id=user_id,
            status=status,
            upcoming_only=upcoming_only,
        )

        return ToolResult(
            success=True,
            data={
                "reservations": [
                    {
                        "reservation_id": r.id,
                        "confirmation_code": r.confirmation_code,
                        "room_type": r.room_type.value,
                        "check_in": r.check_in.strftime("%Y-%m-%d"),
                        "check_out": r.check_out.strftime("%Y-%m-%d"),
                        "guests": r.guests,
                        "nights": r.nights,
                        "total_price": r.total_price,
                        "status": r.status.value,
                        "special_requests": r.special_requests,
                        "is_upcoming": r.is_upcoming,
                        "is_active": r.is_active,
                    }
                    for r in reservations
                ],
                "count": len(reservations),
            },
        )


class CancelReservationTool(Tool):
    """Tool to cancel a reservation."""

    name = "cancel_reservation"
    description = (
        "Cancel a reservation. "
        "Parameters: reservation_id (str, optional), confirmation_code (str, optional), "
        "reason (str, optional). At least one of reservation_id or confirmation_code is required."
    )

    def __init__(self, reservation_repository: ReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, **kwargs) -> ToolResult:
        reservation_id = kwargs.get("reservation_id")
        confirmation_code = kwargs.get("confirmation_code")
        reason = kwargs.get("reason", "Cancelled by user")

        if not any([reservation_id, confirmation_code]):
            return ToolResult(
                success=False,
                error="At least one of reservation_id or confirmation_code is required",
            )

        reservation = None
        if reservation_id:
            reservation = await self._reservation_repo.get_by_id(reservation_id)
        elif confirmation_code:
            reservation = await self._reservation_repo.get_by_confirmation_code(confirmation_code)

        if not reservation:
            return ToolResult(
                success=False,
                error="Reservation not found",
            )

        if reservation.status == ReservationStatus.CANCELLED:
            return ToolResult(
                success=False,
                error="Reservation is already cancelled",
            )

        success = await self._reservation_repo.cancel(reservation.id, reason)

        if success:
            return ToolResult(
                success=True,
                data={
                    "reservation_id": reservation.id,
                    "confirmation_code": reservation.confirmation_code,
                    "message": f"Reservation {reservation.confirmation_code} cancelled successfully",
                },
            )
        else:
            return ToolResult(
                success=False,
                error="Failed to cancel reservation",
            )


class ModifyReservationTool(Tool):
    """Tool to modify a reservation."""

    name = "modify_reservation"
    description = (
        "Modify a reservation (dates, room type, guests, special requests). "
        "Parameters: reservation_id (str, optional), confirmation_code (str, optional), "
        "check_in (str: YYYY-MM-DD, optional), check_out (str: YYYY-MM-DD, optional), "
        "room_type (str: standard/deluxe/suite/presidential, optional), "
        "guests (int, optional), special_requests (str, optional). "
        "At least one of reservation_id or confirmation_code is required."
    )

    def __init__(self, reservation_repository: ReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, **kwargs) -> ToolResult:
        reservation_id = kwargs.get("reservation_id")
        confirmation_code = kwargs.get("confirmation_code")
        check_in_str = kwargs.get("check_in")
        check_out_str = kwargs.get("check_out")
        room_type_str = kwargs.get("room_type")
        guests = kwargs.get("guests")
        special_requests = kwargs.get("special_requests")

        if not any([reservation_id, confirmation_code]):
            return ToolResult(
                success=False,
                error="At least one of reservation_id or confirmation_code is required",
            )

        reservation = None
        if reservation_id:
            reservation = await self._reservation_repo.get_by_id(reservation_id)
        elif confirmation_code:
            reservation = await self._reservation_repo.get_by_confirmation_code(confirmation_code)

        if not reservation:
            return ToolResult(
                success=False,
                error="Reservation not found",
            )

        if reservation.status == ReservationStatus.CANCELLED:
            return ToolResult(
                success=False,
                error="Cannot modify a cancelled reservation",
            )

        # Parse dates if provided
        check_in = reservation.check_in
        check_out = reservation.check_out
        
        if check_in_str:
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d")
            except ValueError:
                return ToolResult(
                    success=False,
                    error="Invalid check_in date format. Use YYYY-MM-DD",
                )
        
        if check_out_str:
            try:
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d")
            except ValueError:
                return ToolResult(
                    success=False,
                    error="Invalid check_out date format. Use YYYY-MM-DD",
                )

        if check_in >= check_out:
            return ToolResult(
                success=False,
                error="Check-out must be after check-in",
            )

        # Parse room type if provided
        room_type = reservation.room_type
        if room_type_str:
            try:
                room_type = RoomType(room_type_str.lower())
            except ValueError:
                return ToolResult(
                    success=False,
                    error=f"Invalid room type. Use: standard, deluxe, suite, presidential",
                )

        # Check availability for new dates/room type (excluding current reservation)
        available = await self._reservation_repo.check_availability(
            room_type, check_in, check_out, exclude_reservation_id=reservation.id
        )
        if available <= 0:
            return ToolResult(
                success=False,
                error=f"No {room_type.value} rooms available for those dates",
            )

        # Update reservation
        reservation.check_in = check_in
        reservation.check_out = check_out
        reservation.room_type = room_type
        if guests is not None:
            reservation.guests = guests
        if special_requests is not None:
            reservation.special_requests = special_requests
        
        # Recalculate price
        nights = (check_out - check_in).days
        price_per_night = {
            RoomType.STANDARD: 150.0,
            RoomType.DELUXE: 250.0,
            RoomType.SUITE: 400.0,
            RoomType.PRESIDENTIAL: 800.0,
        }
        reservation.total_price = nights * price_per_night.get(room_type, 150.0)

        updated = await self._reservation_repo.update(reservation)

        return ToolResult(
            success=True,
            data={
                "reservation_id": updated.id,
                "confirmation_code": updated.confirmation_code,
                "room_type": updated.room_type.value,
                "check_in": updated.check_in.strftime("%Y-%m-%d"),
                "check_out": updated.check_out.strftime("%Y-%m-%d"),
                "guests": updated.guests,
                "nights": updated.nights,
                "total_price": updated.total_price,
                "status": updated.status.value,
                "special_requests": updated.special_requests,
                "message": f"Reservation {updated.confirmation_code} modified successfully",
            },
        )


class CheckAvailabilityTool(Tool):
    """Tool to check room availability."""

    name = "check_availability_db"
    description = (
        "Check room availability for specific dates and room type. "
        "Parameters: room_type (str: standard/deluxe/suite/presidential, required), "
        "check_in (str: YYYY-MM-DD, required), check_out (str: YYYY-MM-DD, required)."
    )

    def __init__(self, reservation_repository: ReservationRepository):
        self._reservation_repo = reservation_repository

    async def execute(self, **kwargs) -> ToolResult:
        room_type_str = kwargs.get("room_type")
        check_in_str = kwargs.get("check_in")
        check_out_str = kwargs.get("check_out")

        if not all([room_type_str, check_in_str, check_out_str]):
            return ToolResult(
                success=False,
                error="room_type, check_in, and check_out are required",
            )

        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d")
        except ValueError:
            return ToolResult(
                success=False,
                error="Invalid date format. Use YYYY-MM-DD",
            )

        if check_in >= check_out:
            return ToolResult(
                success=False,
                error="Check-out must be after check-in",
            )

        try:
            room_type = RoomType(room_type_str.lower())
        except ValueError:
            return ToolResult(
                success=False,
                error=f"Invalid room type. Use: standard, deluxe, suite, presidential",
            )

        available = await self._reservation_repo.check_availability(room_type, check_in, check_out)

        return ToolResult(
            success=True,
            data={
                "room_type": room_type.value,
                "check_in": check_in_str,
                "check_out": check_out_str,
                "available_rooms": available,
                "message": f"{available} {room_type.value} room(s) available",
            },
        )
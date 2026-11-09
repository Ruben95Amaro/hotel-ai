"""
Booking API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.db.repositories import ReservationRepository, UserRepository
from app.di import get_reservation_repository, get_user_repository

router = APIRouter(prefix="/bookings", tags=["bookings"])


class RoomType(str, Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    PRESIDENTIAL = "presidential"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class BookingCreateRequest(BaseModel):
    user_id: str
    room_type: RoomType
    check_in: datetime
    check_out: datetime
    guests: int = Field(default=1, ge=1, le=4)
    special_requests: Optional[str] = None


class BookingModifyRequest(BaseModel):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    room_type: Optional[RoomType] = None
    guests: Optional[int] = Field(default=None, ge=1, le=4)
    special_requests: Optional[str] = None


class CancelRequest(BaseModel):
    reason: str = "Cancelled by user"


class BookingResponse(BaseModel):
    id: str
    confirmation_code: str
    user_id: str
    room_type: str
    check_in: datetime
    check_out: datetime
    guests: int
    nights: int
    total_price: float
    status: str
    special_requests: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]
    count: int


# Pricing
ROOM_PRICES = {
    RoomType.STANDARD: 150.0,
    RoomType.DELUXE: 250.0,
    RoomType.SUITE: 400.0,
    RoomType.PRESIDENTIAL: 800.0,
}

MAX_GUESTS_PER_ROOM = {
    RoomType.STANDARD: 2,
    RoomType.DELUXE: 3,
    RoomType.SUITE: 4,
    RoomType.PRESIDENTIAL: 4,
}


async def get_current_user_id() -> str:
    """Extract user_id from auth (simplified)."""
    # In production, get from validated JWT
    # For demo, we'll require user_id in request
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth not fully implemented - provide user_id in request"
    )


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: BookingCreateRequest,
    reservation_repo: ReservationRepository = Depends(get_reservation_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Create a new booking."""
    # Verify user exists
    user = await user_repo.get_by_id(request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate dates
    if request.check_in >= request.check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out must be after check-in"
        )
    
    if request.check_in < datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in cannot be in the past"
        )
    
    # Validate guest count
    max_guests = MAX_GUESTS_PER_ROOM.get(request.room_type, 2)
    if request.guests > max_guests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {max_guests} guests for {request.room_type.value} room"
        )
    
    # Check availability
    available = await reservation_repo.check_availability(
        request.room_type, request.check_in, request.check_out
    )
    if available <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No {request.room_type.value} rooms available for those dates"
        )
    
    # Calculate price
    nights = (request.check_out - request.check_in).days
    price_per_night = ROOM_PRICES.get(request.room_type, 150.0)
    total_price = nights * price_per_night
    
    # Create reservation
    from app.db.models import Reservation, ReservationStatus as ModelStatus, RoomType as ModelRoomType
    reservation = Reservation(
        user_id=request.user_id,
        room_type=ModelRoomType(request.room_type.value),
        check_in=request.check_in,
        check_out=request.check_out,
        status=ModelStatus.CONFIRMED,
        guests=request.guests,
        special_requests=request.special_requests or "",
        total_price=total_price,
    )
    
    created = await reservation_repo.create(reservation)
    
    return BookingResponse(
        id=created.id,
        confirmation_code=created.confirmation_code,
        user_id=created.user_id,
        room_type=created.room_type.value,
        check_in=created.check_in,
        check_out=created.check_out,
        guests=created.guests,
        nights=created.nights,
        total_price=created.total_price,
        status=created.status.value,
        special_requests=created.special_requests,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("", response_model=BookingListResponse)
async def list_bookings(
    user_id: str,  # In production, get from JWT
    status: Optional[str] = None,
    upcoming_only: bool = False,
    reservation_repo: ReservationRepository = Depends(get_reservation_repository)
):
    """List bookings for a user."""
    from app.db.models import ReservationStatus
    
    status_enum = None
    if status:
        try:
            status_enum = ReservationStatus(status.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Use: {[s.value for s in ReservationStatus]}"
            )
    
    bookings = await reservation_repo.get_by_user_id(
        user_id=user_id,
        status=status_enum,
        upcoming_only=upcoming_only
    )
    
    return BookingListResponse(
        bookings=[
            BookingResponse(
                id=b.id,
                confirmation_code=b.confirmation_code,
                user_id=b.user_id,
                room_type=b.room_type.value,
                check_in=b.check_in,
                check_out=b.check_out,
                guests=b.guests,
                nights=b.nights,
                total_price=b.total_price,
                status=b.status.value,
                special_requests=b.special_requests,
                created_at=b.created_at,
                updated_at=b.updated_at,
            )
            for b in bookings
        ],
        count=len(bookings)
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    reservation_repo: ReservationRepository = Depends(get_reservation_repository)
):
    """Get booking by ID."""
    booking = await reservation_repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return BookingResponse(
        id=booking.id,
        confirmation_code=booking.confirmation_code,
        user_id=booking.user_id,
        room_type=booking.room_type.value,
        check_in=booking.check_in,
        check_out=booking.check_out,
        guests=booking.guests,
        nights=booking.nights,
        total_price=booking.total_price,
        status=booking.status.value,
        special_requests=booking.special_requests,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@router.get("/confirmation/{code}", response_model=BookingResponse)
async def get_booking_by_confirmation(
    code: str,
    reservation_repo: ReservationRepository = Depends(get_reservation_repository)
):
    """Get booking by confirmation code."""
    booking = await reservation_repo.get_by_confirmation_code(code)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return BookingResponse(
        id=booking.id,
        confirmation_code=booking.confirmation_code,
        user_id=booking.user_id,
        room_type=booking.room_type.value,
        check_in=booking.check_in,
        check_out=booking.check_out,
        guests=booking.guests,
        nights=booking.nights,
        total_price=booking.total_price,
        status=booking.status.value,
        special_requests=booking.special_requests,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: str,
    request: CancelRequest,
    reservation_repo: ReservationRepository = Depends(get_reservation_repository)
):
    """Cancel a booking."""
    booking = await reservation_repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status.value == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking already cancelled"
        )
    
    success = await reservation_repo.cancel(booking_id, request.reason)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        )
    
    # Refresh
    cancelled = await reservation_repo.get_by_id(booking_id)
    
    return BookingResponse(
        id=cancelled.id,
        confirmation_code=cancelled.confirmation_code,
        user_id=cancelled.user_id,
        room_type=cancelled.room_type.value,
        check_in=cancelled.check_in,
        check_out=cancelled.check_out,
        guests=cancelled.guests,
        nights=cancelled.nights,
        total_price=cancelled.total_price,
        status=cancelled.status.value,
        special_requests=cancelled.special_requests,
        created_at=cancelled.created_at,
        updated_at=cancelled.updated_at,
    )


@router.put("/{booking_id}", response_model=BookingResponse)
async def modify_booking(
    booking_id: str,
    request: BookingModifyRequest,
    reservation_repo: ReservationRepository = Depends(get_reservation_repository)
):
    """Modify a booking."""
    booking = await reservation_repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status.value == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify a cancelled booking"
        )
    
    # Apply changes
    check_in = request.check_in or booking.check_in
    check_out = request.check_out or booking.check_out
    room_type = request.room_type or booking.room_type
    guests = request.guests or booking.guests
    special_requests = request.special_requests if request.special_requests is not None else booking.special_requests
    
    # Validate
    if check_in >= check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out must be after check-in"
        )
    
    # Check availability (exclude current booking)
    from app.db.models import RoomType as ModelRoomType
    available = await reservation_repo.check_availability(
        ModelRoomType(room_type.value), check_in, check_out, exclude_reservation_id=booking_id
    )
    if available <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No {room_type.value} rooms available for those dates"
        )
    
    # Recalculate price
    nights = (check_out - check_in).days
    price_per_night = ROOM_PRICES.get(ModelRoomType(room_type.value), 150.0)
    total_price = nights * price_per_night
    
    # Update
    from app.db.models import RoomType as ModelRoomType
    booking.check_in = check_in
    booking.check_out = check_out
    booking.room_type = ModelRoomType(room_type.value)
    booking.guests = guests
    booking.special_requests = special_requests
    booking.total_price = total_price
    
    updated = await reservation_repo.update(booking)
    
    return BookingResponse(
        id=updated.id,
        confirmation_code=updated.confirmation_code,
        user_id=updated.user_id,
        room_type=updated.room_type.value,
        check_in=updated.check_in,
        check_out=updated.check_out,
        guests=updated.guests,
        nights=updated.nights,
        total_price=updated.total_price,
        status=updated.status.value,
        special_requests=updated.special_requests,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )
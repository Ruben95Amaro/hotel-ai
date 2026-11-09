"""
Database-agnostic domain models.
These are pure Python dataclasses - no ORM dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ReservationStatus(str, Enum):
    """Reservation status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class RoomType(str, Enum):
    """Room type enumeration."""
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    PRESIDENTIAL = "presidential"


@dataclass
class User:
    """User/Guest domain model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    full_name: str = ""
    phone: str = ""
    document_id: str = ""  # Passport/ID number
    nationality: str = ""
    password_hash: str = ""  # Hashed password
    preferences: dict = field(default_factory=dict)  # Room preferences, dietary, etc.
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class Reservation:
    """Hotel reservation domain model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    room_type: RoomType = RoomType.STANDARD
    check_in: datetime = field(default_factory=datetime.utcnow)
    check_out: datetime = field(default_factory=datetime.utcnow)
    status: ReservationStatus = ReservationStatus.PENDING
    guests: int = 1
    special_requests: str = ""
    total_price: float = 0.0
    confirmation_code: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    cancellation_reason: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.confirmation_code:
            self.confirmation_code = str(uuid.uuid4())[:8].upper()

    @property
    def nights(self) -> int:
        """Calculate number of nights."""
        delta = self.check_out - self.check_in
        return max(1, delta.days)

    @property
    def is_active(self) -> bool:
        """Check if reservation is active (not cancelled)."""
        return self.status not in (ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW)

    @property
    def is_upcoming(self) -> bool:
        """Check if reservation is in the future."""
        return self.check_in > datetime.utcnow() and self.is_active

    @property
    def is_current(self) -> bool:
        """Check if reservation is current (checked in)."""
        return self.status == ReservationStatus.CHECKED_IN
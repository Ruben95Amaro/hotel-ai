"""
Database-agnostic repository interfaces.
Implement these interfaces for any database (PostgreSQL, MySQL, SQLite, MongoDB, etc.)
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db.models import User, Reservation, ReservationStatus, RoomType


class UserRepository(ABC):
    """Abstract interface for user data access."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        ...

    @abstractmethod
    async def get_by_document_id(self, document_id: str) -> Optional[User]:
        """Get user by document ID (passport/national ID)."""
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user."""
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        ...

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List users with pagination."""
        ...


class ReservationRepository(ABC):
    """Abstract interface for reservation data access."""

    @abstractmethod
    async def create(self, reservation: Reservation) -> Reservation:
        """Create a new reservation."""
        ...

    @abstractmethod
    async def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """Get reservation by ID."""
        ...

    @abstractmethod
    async def get_by_confirmation_code(self, code: str) -> Optional[Reservation]:
        """Get reservation by confirmation code."""
        ...

    @abstractmethod
    async def get_by_user_id(
        self, 
        user_id: str, 
        status: Optional[ReservationStatus] = None,
        upcoming_only: bool = False
    ) -> List[Reservation]:
        """Get reservations for a user."""
        ...

    @abstractmethod
    async def update(self, reservation: Reservation) -> Reservation:
        """Update reservation."""
        ...

    @abstractmethod
    async def cancel(self, reservation_id: str, reason: str = "") -> bool:
        """Cancel a reservation."""
        ...

    @abstractmethod
    async def list(
        self, 
        limit: int = 100, 
        offset: int = 0,
        status: Optional[ReservationStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Reservation]:
        """List reservations with filters."""
        ...

    @abstractmethod
    async def check_availability(
        self, 
        room_type: RoomType, 
        check_in: datetime, 
        check_out: datetime,
        exclude_reservation_id: Optional[str] = None
    ) -> int:
        """Check available rooms of a type for given dates."""
        ...


class DatabaseManager(ABC):
    """Abstract interface for database connection management."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database connection pool."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close database connections."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check database connectivity."""
        ...

    @abstractmethod
    async def run_migrations(self) -> None:
        """Run database migrations."""
        ...

    @property
    @abstractmethod
    def user_repository(self) -> UserRepository:
        """Get user repository instance."""
        ...

    @property
    @abstractmethod
    def reservation_repository(self) -> ReservationRepository:
        """Get reservation repository instance."""
        ...
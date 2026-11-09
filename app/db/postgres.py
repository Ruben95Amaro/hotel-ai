"""
PostgreSQL implementation of database interfaces.
Uses psycopg (via SQLAlchemy) for async operations.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey, Index, select, func, and_, or_, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from typing import List, Optional, Union
import uuid

from app.db.models import User, Reservation, ReservationStatus, RoomType
from app.db.repositories import UserRepository, ReservationRepository, DatabaseManager
from app.settings.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy base class."""
    pass


class UserORM(Base):
    """SQLAlchemy ORM model for users."""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    document_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=True, index=True)
    nationality: Mapped[str] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )


class ReservationORM(Base):
    """SQLAlchemy ORM model for reservations."""
    __tablename__ = "reservations"
    
    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    room_type: Mapped[str] = mapped_column(String(20), nullable=False)
    check_in: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    check_out: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=ReservationStatus.PENDING.value, nullable=False, index=True)
    guests: Mapped[int] = mapped_column(default=1)
    special_requests: Mapped[str] = mapped_column(default="")
    total_price: Mapped[float] = mapped_column(default=0.0)
    confirmation_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = mapped_column(DateTime, nullable=True)
    cancellation_reason: Mapped[str] = mapped_column(default="")
    
    __table_args__ = (
        Index("ix_reservations_user_status", "user_id", "status"),
        Index("ix_reservations_dates", "check_in", "check_out"),
        Index("ix_reservations_room_dates", "room_type", "check_in", "check_out"),
    )


def user_orm_to_domain(orm: UserORM) -> User:
    """Convert ORM to domain model."""
    return User(
        id=str(orm.id),
        email=orm.email,
        full_name=orm.full_name,
        phone=orm.phone or "",
        document_id=orm.document_id or "",
        nationality=orm.nationality or "",
        password_hash=orm.password_hash or "",
        preferences=orm.preferences or {},
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        is_active=orm.is_active,
    )


def reservation_orm_to_domain(orm: ReservationORM) -> Reservation:
    """Convert ORM to domain model."""
    return Reservation(
        id=str(orm.id),
        user_id=str(orm.user_id),
        room_type=RoomType(orm.room_type),
        check_in=orm.check_in,
        check_out=orm.check_out,
        status=ReservationStatus(orm.status),
        guests=orm.guests,
        special_requests=orm.special_requests or "",
        total_price=orm.total_price,
        confirmation_code=orm.confirmation_code,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        cancelled_at=orm.cancelled_at,
        cancellation_reason=orm.cancellation_reason or "",
    )


def user_domain_to_orm(domain: User) -> UserORM:
    """Convert domain model to ORM."""
    return UserORM(
        id=domain.id,
        email=domain.email,
        full_name=domain.full_name,
        phone=domain.phone,
        document_id=domain.document_id,
        nationality=domain.nationality,
        password_hash=domain.password_hash,
        preferences=domain.preferences,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        is_active=domain.is_active,
    )


def reservation_domain_to_orm(domain: Reservation) -> ReservationORM:
    """Convert domain model to ORM."""
    return ReservationORM(
        id=domain.id,
        user_id=domain.user_id,
        room_type=domain.room_type.value,
        check_in=domain.check_in,
        check_out=domain.check_out,
        status=domain.status.value,
        guests=domain.guests,
        special_requests=domain.special_requests,
        total_price=domain.total_price,
        confirmation_code=domain.confirmation_code,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        cancelled_at=domain.cancelled_at,
        cancellation_reason=domain.cancellation_reason,
    )


class PostgresUserRepository(UserRepository):
    """PostgreSQL implementation of UserRepository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create(self, user: User) -> User:
        async with self._session_factory() as session:
            orm = user_domain_to_orm(user)
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return user_orm_to_domain(orm)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        async with self._session_factory() as session:
            result = await session.execute(select(UserORM).where(UserORM.id == user_id))
            orm = result.scalar_one_or_none()
            return user_orm_to_domain(orm) if orm else None

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserORM).where(UserORM.email == email, UserORM.is_active == True)
            )
            orm = result.scalar_one_or_none()
            return user_orm_to_domain(orm) if orm else None

    async def get_by_document_id(self, document_id: str) -> Optional[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserORM).where(UserORM.document_id == document_id, UserORM.is_active == True)
            )
            orm = result.scalar_one_or_none()
            return user_orm_to_domain(orm) if orm else None

    async def update(self, user: User) -> User:
        async with self._session_factory() as session:
            user.updated_at = datetime.utcnow()
            orm = user_domain_to_orm(user)
            await session.merge(orm)
            await session.commit()
            return user

    async def delete(self, user_id: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserORM).where(UserORM.id == user_id)
            )
            orm = result.scalar_one_or_none()
            if orm:
                orm.is_active = False
                await session.commit()
                return True
            return False

    async def list(self, limit: int = 100, offset: int = 0) -> List[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserORM)
                .where(UserORM.is_active == True)
                .order_by(UserORM.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return [user_orm_to_domain(orm) for orm in result.scalars().all()]


class PostgresReservationRepository(ReservationRepository):
    """PostgreSQL implementation of ReservationRepository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create(self, reservation: Reservation) -> Reservation:
        async with self._session_factory() as session:
            orm = reservation_domain_to_orm(reservation)
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return reservation_orm_to_domain(orm)

    async def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReservationORM).where(ReservationORM.id == reservation_id)
            )
            orm = result.scalar_one_or_none()
            return reservation_orm_to_domain(orm) if orm else None

    async def get_by_confirmation_code(self, code: str) -> Optional[Reservation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReservationORM).where(ReservationORM.confirmation_code == code)
            )
            orm = result.scalar_one_or_none()
            return reservation_orm_to_domain(orm) if orm else None

    async def get_by_user_id(
        self, 
        user_id: str, 
        status: Optional[ReservationStatus] = None,
        upcoming_only: bool = False
    ) -> List[Reservation]:
        async with self._session_factory() as session:
            query = select(ReservationORM).where(ReservationORM.user_id == user_id)
            
            if status:
                query = query.where(ReservationORM.status == status.value)
            
            if upcoming_only:
                query = query.where(ReservationORM.check_in > datetime.utcnow())
            
            query = query.order_by(ReservationORM.check_in.desc())
            result = await session.execute(query)
            return [reservation_orm_to_domain(orm) for orm in result.scalars().all()]

    async def update(self, reservation: Reservation) -> Reservation:
        async with self._session_factory() as session:
            reservation.updated_at = datetime.utcnow()
            orm = reservation_domain_to_orm(reservation)
            await session.merge(orm)
            await session.commit()
            return reservation

    async def cancel(self, reservation_id: str, reason: str = "") -> bool:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ReservationORM).where(ReservationORM.id == reservation_id)
            )
            orm = result.scalar_one_or_none()
            if orm:
                orm.status = ReservationStatus.CANCELLED.value
                orm.cancelled_at = datetime.utcnow()
                orm.cancellation_reason = reason
                orm.updated_at = datetime.utcnow()
                await session.commit()
                return True
            return False

    async def list(
        self, 
        limit: int = 100, 
        offset: int = 0,
        status: Optional[ReservationStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Reservation]:
        async with self._session_factory() as session:
            query = select(ReservationORM)
            
            if status:
                query = query.where(ReservationORM.status == status.value)
            if date_from:
                query = query.where(ReservationORM.check_in >= date_from)
            if date_to:
                query = query.where(ReservationORM.check_out <= date_to)
            
            query = query.order_by(ReservationORM.check_in.desc()).limit(limit).offset(offset)
            result = await session.execute(query)
            return [reservation_orm_to_domain(orm) for orm in result.scalars().all()]

    async def check_availability(
        self, 
        room_type: RoomType, 
        check_in: datetime, 
        check_out: datetime,
        exclude_reservation_id: Optional[str] = None
    ) -> int:
        """
        Check available rooms of a type for given dates.
        Returns count of available rooms (assuming 10 rooms per type for now).
        """
        # In a real implementation, you'd have a rooms table with room counts per type
        # For now, we assume 10 rooms per type and count conflicting reservations
        MAX_ROOMS_PER_TYPE = 10
        
        async with self._session_factory() as session:
            query = select(func.count(ReservationORM.id)).where(
                and_(
                    ReservationORM.room_type == room_type.value,
                    ReservationORM.status.in_([
                        ReservationStatus.CONFIRMED.value,
                        ReservationStatus.CHECKED_IN.value,
                        ReservationStatus.PENDING.value
                    ]),
                    # Overlapping dates: check_in < existing_check_out AND check_out > existing_check_in
                    ReservationORM.check_in < check_out,
                    ReservationORM.check_out > check_in,
                )
            )
            
            if exclude_reservation_id:
                query = query.where(ReservationORM.id != exclude_reservation_id)
            
            result = await session.execute(query)
            booked_count = result.scalar() or 0
            return max(0, MAX_ROOMS_PER_TYPE - booked_count)


class PostgresDatabaseManager(DatabaseManager):
    """PostgreSQL implementation of DatabaseManager."""

    def __init__(self):
        self._engine = None
        self._session_factory = None
        self._user_repo = None
        self._reservation_repo = None
        self._settings = get_settings()

    @property
    def _database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self._settings.postgres_user}:{self._settings.postgres_password}"
            f"@{self._settings.postgres_host}:{self._settings.postgres_port}/{self._settings.postgres_db}"
        )

    async def initialize(self) -> None:
        """Initialize database connection pool with retry logic."""
        import asyncio
        import logging
        from sqlalchemy.exc import OperationalError, DisconnectionError
        
        logger = logging.getLogger(__name__)
        max_retries = 15
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self._engine = create_async_engine(
                    self._database_url,
                    pool_size=self._settings.postgres_pool_size,
                    max_overflow=self._settings.postgres_max_overflow,
                    pool_pre_ping=True,
                    echo=self._settings.environment == "development",
                )
                self._session_factory = async_sessionmaker(
                    self._engine, class_=AsyncSession, expire_on_commit=False
                )
                self._user_repo = PostgresUserRepository(self._session_factory)
                self._reservation_repo = PostgresReservationRepository(self._session_factory)
                # Create tables - this tests the connection
                async with self._engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Database initialized successfully", extra={"attempt": attempt + 1})
                return
            except (OperationalError, DisconnectionError, ConnectionError, OSError) as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        "Database connection failed, retrying",
                        extra={"attempt": attempt + 1, "max_retries": max_retries, "error": str(e), "delay": retry_delay}
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 30)
                else:
                    logger.error("Database connection failed after all retries", extra={"attempts": max_retries, "error": str(e)})
                    raise
            except Exception as e:
                # Catch any other unexpected errors during init
                if attempt < max_retries - 1:
                    logger.warning(
                        "Database initialization error, retrying",
                        extra={"attempt": attempt + 1, "max_retries": max_retries, "error": str(e), "delay": retry_delay}
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 30)
                else:
                    logger.error("Database initialization failed after all retries", extra={"attempts": max_retries, "error": str(e)})
                    raise

    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()

    async def health_check(self) -> bool:
        """Check database connectivity."""
        import logging
        logger = logging.getLogger(__name__)
        try:
            if not self._engine:
                return False
            async with self._engine.connect() as conn:
                await conn.execute(select(1))
            return True
        except Exception as e:
            logger.warning("Database health check failed", extra={"error": str(e)})
            return False

    async def run_migrations(self) -> None:
        """Run database migrations (using Alembic in production)."""
        # For now, just create tables
        if self._engine:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    @property
    def user_repository(self) -> UserRepository:
        if not self._user_repo:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._user_repo

    @property
    def reservation_repository(self) -> ReservationRepository:
        if not self._reservation_repo:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._reservation_repo
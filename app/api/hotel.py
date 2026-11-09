"""
Hotel Information API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.settings.config import get_settings

router = APIRouter(prefix="/hotel", tags=["hotel"])


class RoomInfo(BaseModel):
    type: str
    name: str
    description: str
    base_price: float
    max_guests: int
    size: str
    beds: str
    view: str
    amenities: List[str]


class ServiceInfo(BaseModel):
    id: str
    title: str
    description: str
    features: List[str]
    hours: str
    location: str


class HotelInfo(BaseModel):
    name: str
    location: str
    stars: int
    phone: str
    email: str
    description: str
    address: str


class AvailabilityRequest(BaseModel):
    room_type: str
    check_in: datetime
    check_out: datetime


class AvailabilityResponse(BaseModel):
    room_type: str
    check_in: str
    check_out: str
    available_rooms: int
    total_rooms: int = 10


# Hotel configuration from settings
def get_hotel_info() -> HotelInfo:
    settings = get_settings()
    return HotelInfo(
        name=settings.hotel_name,
        location=settings.hotel_location,
        stars=settings.hotel_stars,
        phone=settings.hotel_phone,
        email=settings.hotel_email,
        description=(
            f"Experience luxury and comfort at {settings.hotel_name} in {settings.hotel_location}. "
            f"Our {settings.hotel_stars}-star hotel offers world-class amenities, "
            f"exceptional service, and unforgettable experiences."
        ),
        address=settings.hotel_address,
    )


ROOM_TYPES = [
    RoomInfo(
        type="standard",
        name="Standard Room",
        description="Elegant comfort with garden or city views. Perfect for solo travelers or couples.",
        base_price=150.0,
        max_guests=2,
        size="25 m²",
        beds="1 King or 2 Twin",
        view="Garden/City",
        amenities=[
            "Free WiFi", "Air Conditioning", "Flat-screen TV", "Minibar",
            "Safe", "En-suite bathroom", "Daily housekeeping"
        ],
    ),
    RoomInfo(
        type="deluxe",
        name="Deluxe Room",
        description="Spacious rooms with private balcony and partial ocean views. Enhanced amenities.",
        base_price=250.0,
        max_guests=3,
        size="35 m²",
        beds="1 King + Sofa bed",
        view="Partial Ocean",
        amenities=[
            "Free WiFi", "Air Conditioning", "Flat-screen TV", "Minibar",
            "Safe", "En-suite bathroom", "Private balcony", "Bathrobes",
            "Premium toiletries", "Daily housekeeping", "Turndown service"
        ],
    ),
    RoomInfo(
        type="suite",
        name="Junior Suite",
        description="Separate living area with stunning ocean views. Luxury bath with soaking tub.",
        base_price=400.0,
        max_guests=4,
        size="50 m²",
        beds="1 King + Living room sofa bed",
        view="Full Ocean",
        amenities=[
            "Free WiFi", "Air Conditioning", "Flat-screen TV", "Minibar",
            "Safe", "En-suite bathroom", "Private balcony", "Bathrobes",
            "Premium toiletries", "Separate living area", "Soaking tub",
            "Nespresso machine", "Daily housekeeping", "Turndown service",
            "Butler service on request"
        ],
    ),
    RoomInfo(
        type="presidential",
        name="Presidential Suite",
        description="Ultimate luxury with panoramic ocean views, private terrace, butler service.",
        base_price=800.0,
        max_guests=4,
        size="100 m²",
        beds="1 King + 2 Sofa beds",
        view="Panoramic Ocean",
        amenities=[
            "Free WiFi", "Air Conditioning", "Flat-screen TV", "Minibar (complimentary)",
            "Safe", "En-suite bathroom", "Private terrace", "Bathrobes",
            "Premium toiletries", "Separate living area", "Soaking tub",
            "Nespresso machine", "Daily housekeeping", "Turndown service",
            "Dedicated butler", "Private check-in/out", "Laundry service",
            "Welcome champagne", "Fruit basket"
        ],
    ),
]

SERVICES = [
    ServiceInfo(
        id="dining",
        title="Fine Dining",
        description="Experience culinary excellence at our Michelin-starred restaurant Ocean's Bounty, featuring fresh Atlantic seafood and Portuguese-inspired cuisine.",
        features=[
            "Ocean's Bounty Restaurant", "Sea Breeze Bar & Terrace",
            "In-Room Dining 24/7", "Private Dining Rooms", "Wine Cellar Tastings"
        ],
        hours="6:30 AM - 11:00 PM",
        location="Ground Floor & Rooftop",
    ),
    ServiceInfo(
        id="spa",
        title="Ocean Wellness Spa",
        description="Rejuvenate body and mind with our signature treatments inspired by the healing powers of the Atlantic Ocean.",
        features=[
            "Signature Ocean Rituals", "Thalassotherapy Pool",
            "Sauna & Steam Rooms", "Couples Treatment Suites",
            "Fitness Center 24/7", "Yoga & Meditation Classes"
        ],
        hours="9:00 AM - 9:00 PM",
        location="Level -1",
    ),
    ServiceInfo(
        id="concierge",
        title="Personal Concierge",
        description="Our dedicated concierge team curates unforgettable experiences tailored to your preferences.",
        features=[
            "Private Tours & Excursions", "Restaurant Reservations",
            "Event Tickets", "Transportation Arrangements",
            "Special Occasion Planning", "Local Expert Recommendations"
        ],
        hours="24/7",
        location="Lobby",
    ),
    ServiceInfo(
        id="pool",
        title="Infinity Pool & Terrace",
        description="Our stunning rooftop infinity pool merges with the Atlantic horizon, offering the perfect setting for relaxation.",
        features=[
            "Heated Infinity Pool", "Poolside Bar Service",
            "Private Cabanas", "Sunset Cocktail Hour",
            "Poolside Light Bites", "Towel & Robe Service"
        ],
        hours="7:00 AM - 10:00 PM",
        location="Rooftop (Level 8)",
    ),
    ServiceInfo(
        id="business",
        title="Business & Events",
        description="State-of-the-art facilities for meetings, conferences, and celebrations with panoramic ocean views.",
        features=[
            "5 Meeting Rooms", "Grand Ballroom (300 guests)",
            "Advanced AV Technology", "Dedicated Event Planner",
            "Custom Catering Menus", "High-Speed Internet"
        ],
        hours="By Appointment",
        location="Levels 1-2",
    ),
    ServiceInfo(
        id="family",
        title="Family Services",
        description="Thoughtful amenities and activities to ensure our youngest guests have a magical stay.",
        features=[
            "Kids' Club (4-12 years)", "Babysitting Services",
            "Children's Menu", "Family Pool Hours",
            "Welcome Gifts for Kids", "Connecting Rooms Available"
        ],
        hours="9:00 AM - 6:00 PM",
        location="Level 3",
    ),
]


@router.get("/info", response_model=HotelInfo)
async def get_hotel_info_endpoint():
    """Get hotel information."""
    return get_hotel_info()


@router.get("/rooms", response_model=List[RoomInfo])
async def get_rooms():
    """Get all room types with details."""
    return ROOM_TYPES


@router.get("/rooms/{room_type}", response_model=RoomInfo)
async def get_room(room_type: str):
    """Get specific room type."""
    for room in ROOM_TYPES:
        if room.type == room_type.lower():
            return room
    raise HTTPException(status_code=404, detail="Room type not found")


@router.get("/services", response_model=List[ServiceInfo])
async def get_services():
    """Get all hotel services."""
    return SERVICES


@router.get("/services/{service_id}", response_model=ServiceInfo)
async def get_service(service_id: str):
    """Get specific service."""
    for service in SERVICES:
        if service.id == service_id.lower():
            return service
    raise HTTPException(status_code=404, detail="Service not found")


@router.post("/availability", response_model=AvailabilityResponse)
async def check_availability(request: AvailabilityRequest):
    """Check room availability for dates."""
    from app.di import get_reservation_repository
    from app.db.models import RoomType
    
    try:
        room_type_enum = RoomType(request.room_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid room type. Use: {[r.value for r in RoomType]}"
        )
    
    # Get repository (simplified - in production use DI)
    from app.db.postgres import PostgresDatabaseManager
    from app.settings.config import get_settings
    
    settings = get_settings()
    db = PostgresDatabaseManager()
    await db.initialize()
    
    try:
        available = await db.reservation_repository.check_availability(
            room_type_enum, request.check_in, request.check_out
        )
        return AvailabilityResponse(
            room_type=request.room_type,
            check_in=request.check_in.strftime("%Y-%m-%d"),
            check_out=request.check_out.strftime("%Y-%m-%d"),
            available_rooms=available,
        )
    finally:
        await db.close()
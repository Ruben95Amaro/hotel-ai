"""
Special Requests API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.db.repositories import ReservationRepository
from app.di import get_reservation_repository

router = APIRouter(prefix="/special-requests", tags=["special-requests"])


class RequestType(str, Enum):
    ROOM_PREFERENCE = "room_preference"
    DIETARY = "dietary"
    ACCESSIBILITY = "accessibility"
    CELEBRATION = "celebration"
    TRANSPORT = "transport"
    OTHER = "other"


class RequestStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


class SpecialRequestCreate(BaseModel):
    user_id: str
    booking_id: Optional[str] = None
    type: RequestType
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)


class SpecialRequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    staff_notes: Optional[str] = None


class SpecialRequestResponse(BaseModel):
    id: str
    user_id: str
    booking_id: Optional[str]
    type: str
    title: str
    description: str
    status: str
    staff_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SpecialRequestListResponse(BaseModel):
    requests: List[SpecialRequestResponse]
    count: int


# In-memory storage for demo (in production, use database table)
_special_requests_db = []
_request_id_counter = 0


def _generate_id() -> str:
    global _request_id_counter
    _request_id_counter += 1
    return f"req_{_request_id_counter}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


@router.post("", response_model=SpecialRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_special_request(
    request: SpecialRequestCreate
):
    """Create a new special request."""
    global _special_requests_db
    
    new_request = {
        "id": _generate_id(),
        "user_id": request.user_id,
        "booking_id": request.booking_id,
        "type": request.type.value,
        "title": request.title,
        "description": request.description,
        "status": RequestStatus.PENDING.value,
        "staff_notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    _special_requests_db.append(new_request)
    
    return SpecialRequestResponse(**new_request)


@router.get("", response_model=SpecialRequestListResponse)
async def list_special_requests(
    user_id: str,  # In production, get from JWT
    status: Optional[str] = None
):
    """List special requests for a user."""
    filtered = [r for r in _special_requests_db if r["user_id"] == user_id]
    
    if status:
        filtered = [r for r in filtered if r["status"] == status.lower()]
    
    # Sort by created_at descending
    filtered.sort(key=lambda x: x["created_at"], reverse=True)
    
    return SpecialRequestListResponse(
        requests=[SpecialRequestResponse(**r) for r in filtered],
        count=len(filtered)
    )


@router.get("/{request_id}", response_model=SpecialRequestResponse)
async def get_special_request(request_id: str):
    """Get special request by ID."""
    for r in _special_requests_db:
        if r["id"] == request_id:
            return SpecialRequestResponse(**r)
    
    raise HTTPException(
        status_code=404,
        detail="Special request not found"
    )


@router.put("/{request_id}", response_model=SpecialRequestResponse)
async def update_special_request(
    request_id: str,
    request: SpecialRequestUpdate
):
    """Update special request (staff only)."""
    for r in _special_requests_db:
        if r["id"] == request_id:
            if request.status:
                r["status"] = request.status.value
            if request.staff_notes is not None:
                r["staff_notes"] = request.staff_notes
            r["updated_at"] = datetime.utcnow()
            return SpecialRequestResponse(**r)
    
    raise HTTPException(
        status_code=404,
        detail="Special request not found"
    )
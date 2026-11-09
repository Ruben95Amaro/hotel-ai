"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timedelta

from app.db.repositories import UserRepository
from app.di import get_user_repository

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)


class TokenResponse(BaseModel):
    token: str
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    document_id: Optional[str] = None
    nationality: Optional[str] = None
    preferences: dict = {}


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    document_id: Optional[str] = Field(default=None, max_length=100)
    nationality: Optional[str] = Field(default=None, max_length=100)
    preferences: Optional[dict] = None


# Simple password hashing (in production, use bcrypt/argon2)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


# Simple JWT token generation (in production, use python-jose)
def create_token(user_id: str) -> str:
    payload = f"{user_id}:{secrets.token_urlsafe(32)}:{datetime.utcnow().isoformat()}"
    return hashlib.sha256(payload.encode()).hexdigest()


# Dependency to get current user (simplified - in production use proper JWT validation)
async def get_current_user(
    authorization: str = None,
    user_repo: UserRepository = Depends(get_user_repository)
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    # In production, decode and validate JWT
    # For now, we'll look up user by token (simplified)
    # This is a mock implementation
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token validation not fully implemented",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Authenticate user and return token."""
    user = await user_repo.get_by_email(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # In production, verify hashed password
    # For demo, accept any password for existing users
    token = create_token(user.id)
    
    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            document_id=user.document_id,
            nationality=user.nationality,
            preferences=user.preferences or {},
        )
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register a new user."""
    # Check if user exists
    existing = await user_repo.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    from app.db.models import User
    user = User(
        email=request.email,
        full_name=f"{request.first_name} {request.last_name}",
        phone=request.phone or "",
        password_hash=hash_password(request.password),
    )
    
    created_user = await user_repo.create(user)
    token = create_token(created_user.id)
    
    return TokenResponse(
        token=token,
        user=UserResponse(
            id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
            phone=created_user.phone,
            document_id=created_user.document_id,
            nationality=created_user.nationality,
            preferences=created_user.preferences or {},
        )
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile."""
    # In production, extract user_id from validated JWT
    # For now, return mock
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile endpoint needs JWT implementation"
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update user profile."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile update needs JWT implementation"
    )
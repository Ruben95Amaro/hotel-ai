"""
Authentication API endpoints with JWT and admin support.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import secrets
import hashlib
from datetime import datetime, timedelta
import jwt

from app.db.repositories import UserRepository
from app.db.models import User
from app.di import get_user_repository
from app.settings.config import get_settings

router = APIRouter(prefix="/auth", tags=["authentication"])

# JWT Settings
settings = get_settings()
JWT_SECRET = settings.jwt_secret if hasattr(settings, 'jwt_secret') else "your-super-secret-jwt-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


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
    is_admin: bool = False
    preferences: dict = {}


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    document_id: Optional[str] = Field(default=None, max_length=100)
    nationality: Optional[str] = Field(default=None, max_length=100)
    preferences: Optional[dict] = None


class AdminUserListResponse(BaseModel):
    users: List[UserResponse]
    count: int


# Password hashing
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


# JWT functions
def create_token(user_id: str, is_admin: bool = False) -> str:
    payload = {
        "sub": user_id,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# Dependencies
async def get_current_user(
    authorization: str = Header(None),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    user_id = payload.get("sub")
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Authenticate user and return JWT token."""
    user = await user_repo.get_by_email(request.email)
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_token(user.id, user.is_admin)
    
    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            document_id=user.document_id,
            nationality=user.nationality,
            is_admin=user.is_admin,
            preferences=user.preferences or {},
        )
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register a new user."""
    existing = await user_repo.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = User(
        email=request.email,
        full_name=f"{request.first_name} {request.last_name}",
        phone=request.phone or "",
        password_hash=hash_password(request.password),
        is_admin=False,
    )
    
    created_user = await user_repo.create(user)
    token = create_token(created_user.id, created_user.is_admin)
    
    return TokenResponse(
        token=token,
        user=UserResponse(
            id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
            phone=created_user.phone,
            document_id=created_user.document_id,
            nationality=created_user.nationality,
            is_admin=created_user.is_admin,
            preferences=created_user.preferences or {},
        )
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        document_id=current_user.document_id,
        nationality=current_user.nationality,
        is_admin=current_user.is_admin,
        preferences=current_user.preferences or {},
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update user profile."""
    if request.first_name is not None:
        current_user.full_name = f"{request.first_name} {current_user.full_name.split(' ')[-1]}"
    if request.last_name is not None:
        current_user.full_name = f"{current_user.full_name.split(' ')[0]} {request.last_name}"
    if request.phone is not None:
        current_user.phone = request.phone
    if request.document_id is not None:
        current_user.document_id = request.document_id
    if request.nationality is not None:
        current_user.nationality = request.nationality
    if request.preferences is not None:
        current_user.preferences = request.preferences
    
    current_user.updated_at = datetime.utcnow()
    updated = await user_repo.update(current_user)
    
    return UserResponse(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        phone=updated.phone,
        document_id=updated.document_id,
        nationality=updated.nationality,
        is_admin=updated.is_admin,
        preferences=updated.preferences or {},
    )


# Admin endpoints
@router.get("/admin/users", response_model=AdminUserListResponse)
async def list_users(
    limit: int = 100,
    offset: int = 0,
    current_admin: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """List all users (admin only)."""
    users = await user_repo.list(limit=limit, offset=offset)
    return AdminUserListResponse(
        users=[
            UserResponse(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                phone=u.phone,
                document_id=u.document_id,
                nationality=u.nationality,
                is_admin=u.is_admin,
                preferences=u.preferences or {},
            )
            for u in users
        ],
        count=len(users)
    )


@router.post("/admin/users/{user_id}/make-admin", response_model=UserResponse)
async def make_admin(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Make a user an admin (admin only)."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = True
    user.updated_at = datetime.utcnow()
    updated = await user_repo.update(user)
    
    return UserResponse(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        phone=updated.phone,
        document_id=updated.document_id,
        nationality=updated.nationality,
        is_admin=updated.is_admin,
        preferences=updated.preferences or {},
    )


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Delete a user (admin only)."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )
    
    await user_repo.delete(user_id)
    return {"message": "User deleted successfully"}
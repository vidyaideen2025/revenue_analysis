"""Pydantic schemas for User model."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole, Department


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    department: Department | None = None
    role: UserRole = UserRole.OPERATIONS


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, min_length=1, max_length=255)
    department: Department | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=100)


class UserInDB(UserBase):
    """Schema for user data stored in database."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class User(UserInDB):
    """Schema for user response (public view)."""
    pass


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: UUID | None = None
    email: str | None = None
    role: UserRole | None = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    token_type: str
    user: dict


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    items: list[User]
    total: int
    skip: int
    limit: int


class UserStatusUpdate(BaseModel):
    """Schema for updating user status."""
    is_active: bool

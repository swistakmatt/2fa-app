"""
Pydantic schemas for user.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(
        ..., 
        min_length=8,
        max_length=72,
        description="User password (min. 8 characters, max. 72 - bcrypt limit)"
    )


class UserLogin(UserBase):
    """Schema for user login."""
    password: str = Field(..., description="User password")


class UserUpdate(BaseModel):
    """Schema for updating user data."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=72,
        description="New password (min. 8 characters, max. 72 - bcrypt limit)"
    )


class UserResponse(UserBase):
    """Schema for user data response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    """Schema for user from database (with password hash)."""
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

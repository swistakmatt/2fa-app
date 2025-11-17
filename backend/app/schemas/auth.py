"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for data contained in JWT token."""
    email: Optional[str] = None


class LoginResponse(BaseModel):
    """Schema for successful login response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")


class RegisterResponse(BaseModel):
    """Schema for successful registration response."""
    id: int = Field(..., description="ID of newly created user")
    email: str = Field(..., description="User email")
    message: str = Field(default="User successfully registered")


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str = Field(..., description="Error details")

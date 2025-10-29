"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Sprite Schemas
class SpriteRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500)
    size: int = Field(default=64, ge=32, le=512)
    style: Optional[str] = None


class SpriteResponse(BaseModel):
    id: int
    user_id: int
    prompt: str
    image_url: str
    size: int
    style: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Enhanced Schemas
class EnhanceRequest(BaseModel):
    enhancement_prompt: str = Field(..., min_length=1, max_length=500)
    style: str = Field(default="photorealistic")


class EnhancedResponse(BaseModel):
    id: int
    sprite_id: int
    image_url: str
    enhancement_prompt: str
    style: str
    generation_time: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Complete Sprite with Enhanced
class SpriteWithEnhanced(SpriteResponse):
    enhanced: Optional[EnhancedResponse] = None


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


"""Pydantic schemas for image-related requests and responses"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class GenerateImageRequest(BaseModel):
    """Request schema for generating images"""
    subject_type: str = Field(..., pattern="^(scene|item|character)$")
    subject_name: str = Field(..., min_length=1, max_length=200)
    prompt: str = Field(..., min_length=10, max_length=1000)
    custom_prompt: Optional[str] = Field(None, max_length=200)
    aspect_ratio: str = Field("16:9", pattern="^(1:1|16:9|4:3|9:16)$")
    component: str = Field("scene-viewer")

    @validator('custom_prompt')
    def validate_custom_prompt(cls, v, values):
        """Validate custom prompt for security and content requirements"""
        if v:
            # Check dangerous patterns
            dangerous = ['<script', 'javascript:', 'onerror', 'eval(', '<?php', '<iframe']
            if any(d in v.lower() for d in dangerous):
                raise ValueError("Invalid content in custom prompt")

            # Must contain subject name
            if 'subject_name' in values:
                if values['subject_name'].lower() not in v.lower():
                    raise ValueError(f"Custom prompt must mention {values['subject_name']}")
        return v


class ImageResponse(BaseModel):
    """Response schema for image data"""
    id: int
    subject_name: str
    subject_type: str
    component: str
    storage_path_full: str
    storage_path_thumbnail: str
    file_size_bytes: int
    generation_time_ms: int
    created_at: datetime
    is_featured: bool
    use_count: int

    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    """Response schema for paginated image lists"""
    items: List[ImageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Standardized error response format"""
    status: str = "error"
    code: int
    message: str
    detail: Optional[Dict[str, Any]] = None


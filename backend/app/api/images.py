"""Image generation and management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..schemas.image import GenerateImageRequest, ImageResponse, ImageListResponse
from ..services.gemini_client import GeminiClient, QuotaExceededError, GenerationTimeoutError
from ..services.storage import StorageService
from ..models.image_asset import ImageAsset
from ..config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1/images", tags=["images"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate", response_model=ImageResponse)
@limiter.limit(f"{settings.MAX_REQUESTS_PER_MINUTE}/minute")
async def generate_image(
    request: Request,
    data: GenerateImageRequest,
    db: Session = Depends(get_db)
):
    """
    Generate new image with error handling

    Rate limited to MAX_REQUESTS_PER_MINUTE per minute per IP address.
    """
    try:
        # Initialize services
        gemini = GeminiClient(settings.GEMINI_API_KEY)
        storage = StorageService(settings.IMAGE_STORAGE_DIR)

        # Build full prompt
        full_prompt = data.prompt
        if data.custom_prompt:
            full_prompt = f"{data.prompt}. {data.custom_prompt}"

        # Generate image
        image_bytes, gen_time = gemini.generate_image(full_prompt, data.aspect_ratio)

        # Save to filesystem
        paths = storage.save_image(image_bytes, data.subject_name)

        # Save to database (atomic transaction)
        asset = ImageAsset(
            component=data.component,
            subject_type=data.subject_type,
            subject_name=data.subject_name,
            prompt_used=full_prompt,
            custom_prompt=data.custom_prompt,
            storage_path_full=paths["full_path"],
            storage_path_thumbnail=paths["thumbnail_path"],
            file_size_bytes=paths["file_size_bytes"],
            aspect_ratio=data.aspect_ratio,
            generation_time_ms=gen_time
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    except QuotaExceededError as e:
        raise HTTPException(
            status_code=429,
            detail={
                "status": "error",
                "code": 429,
                "message": "API quota exceeded",
                "detail": str(e)
            }
        )
    except GenerationTimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail={
                "status": "error",
                "code": 504,
                "message": "Image generation timeout",
                "detail": str(e)
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "code": 500,
                "message": "Image generation failed",
                "detail": str(e)
            }
        )


@router.get("/search", response_model=ImageListResponse)
async def search_images(
    subject_name: Optional[str] = None,
    subject_type: Optional[str] = None,
    is_featured: Optional[bool] = None,
    page: int = 1,
    page_size: int = 12,
    db: Session = Depends(get_db)
):
    """
    Search images with pagination and filtering

    Query parameters:
    - subject_name: Filter by subject name
    - subject_type: Filter by type (scene, item, character)
    - is_featured: Filter by featured status
    - page: Page number (default: 1)
    - page_size: Items per page (default: 12)
    """
    # Base query - exclude deleted images
    query = db.query(ImageAsset).filter(ImageAsset.deleted_at == None)

    # Apply filters
    if subject_name:
        query = query.filter(ImageAsset.subject_name == subject_name)
    if subject_type:
        query = query.filter(ImageAsset.subject_type == subject_type)
    if is_featured is not None:
        query = query.filter(ImageAsset.is_featured == is_featured)

    # Order: featured first, then newest
    query = query.order_by(
        ImageAsset.is_featured.desc(),
        ImageAsset.created_at.desc()
    )

    # Pagination
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return ImageListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{image_id}")
async def get_image(image_id: int, include_data: bool = True, db: Session = Depends(get_db)):
    """
    Get specific image by ID with optional base64 data

    Increments use_count and updates last_used timestamp.

    Query params:
    - include_data: If true (default), includes base64 encoded image data
    """
    asset = db.query(ImageAsset).filter(
        ImageAsset.id == image_id,
        ImageAsset.deleted_at == None
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "code": 404,
                "message": "Image not found"
            }
        )

    # Increment usage counter
    asset.use_count += 1
    db.commit()

    # Convert to dict
    response_data = {
        "id": asset.id,
        "subject_name": asset.subject_name,
        "subject_type": asset.subject_type,
        "component": asset.component,
        "storage_path_full": asset.storage_path_full,
        "storage_path_thumbnail": asset.storage_path_thumbnail,
        "file_size_bytes": asset.file_size_bytes,
        "generation_time_ms": asset.generation_time_ms,
        "created_at": asset.created_at.isoformat(),
        "is_featured": asset.is_featured,
        "use_count": asset.use_count
    }

    # Include base64 data if requested
    if include_data:
        import base64
        import os

        # storage_path_full already includes "images/full/...", so just use it directly
        full_path = os.path.join('backend', asset.storage_path_full) if not asset.storage_path_full.startswith('/') else asset.storage_path_full

        # Try backend-relative path first, then absolute
        if not os.path.exists(full_path):
            full_path = asset.storage_path_full

        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                image_bytes = f.read()
                response_data['base64_data'] = base64.b64encode(image_bytes).decode('utf-8')
        else:
            response_data['base64_data'] = None

    return response_data


@router.put("/{image_id}/feature")
async def toggle_featured(image_id: int, db: Session = Depends(get_db)):
    """
    Set image as featured (unsets others for same subject)

    Only one image can be featured per subject_name at a time.
    """
    asset = db.query(ImageAsset).filter(
        ImageAsset.id == image_id,
        ImageAsset.deleted_at == None
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "code": 404,
                "message": "Image not found"
            }
        )

    # Unset all other featured images for this subject
    db.query(ImageAsset).filter(
        ImageAsset.subject_name == asset.subject_name,
        ImageAsset.id != image_id
    ).update({ImageAsset.is_featured: False})

    # Toggle this image
    asset.is_featured = not asset.is_featured
    db.commit()

    return {
        "id": asset.id,
        "is_featured": asset.is_featured,
        "subject_name": asset.subject_name
    }


@router.delete("/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    """
    Soft delete image (marks deleted_at timestamp)

    Actual file deletion happens via cleanup job after 30 days.
    """
    asset = db.query(ImageAsset).filter(
        ImageAsset.id == image_id,
        ImageAsset.deleted_at == None
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "code": 404,
                "message": "Image not found"
            }
        )

    # Soft delete
    from datetime import datetime
    asset.deleted_at = datetime.now()
    db.commit()

    return {
        "id": asset.id,
        "status": "deleted",
        "message": "Image marked for deletion"
    }


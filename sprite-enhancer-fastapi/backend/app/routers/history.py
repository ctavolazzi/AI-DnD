"""History and user sprite management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[schemas.SpriteWithEnhanced])
async def get_user_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get user's sprite history with pagination.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 100)
    """
    sprites = db.query(models.Sprite).filter(
        models.Sprite.user_id == current_user.id
    ).order_by(desc(models.Sprite.created_at)).offset(skip).limit(limit).all()

    return sprites


@router.get("/count")
async def get_history_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get total count of user's sprites."""
    count = db.query(models.Sprite).filter(
        models.Sprite.user_id == current_user.id
    ).count()

    return {"count": count}


@router.delete("/clear")
async def clear_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete all user's sprites and enhanced versions."""
    deleted_count = db.query(models.Sprite).filter(
        models.Sprite.user_id == current_user.id
    ).delete()

    db.commit()

    return {
        "message": "History cleared successfully",
        "deleted_count": deleted_count
    }


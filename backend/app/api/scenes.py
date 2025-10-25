"""Scene generation and caching API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..schemas.image import GenerateImageRequest, ImageResponse
from ..models.scene_cache import SceneCache
from ..models.image_asset import ImageAsset
from ..config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
from .images import generate_image

router = APIRouter(prefix="/api/v1/scenes", tags=["scenes"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate", response_model=ImageResponse)
@limiter.limit("5/minute")  # Stricter limit for scenes
async def generate_scene(
    request: Request,
    location: str,
    time_of_day: str = "day",
    weather: str = "clear",
    force_regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Generate or retrieve cached scene

    Checks cache first (unless force_regenerate=true). Cache entries
    expire after CACHE_EXPIRY_DAYS days.

    Rate limited to 5/minute per IP address.
    """

    # Check cache first (unless forced)
    if not force_regenerate:
        cached = db.query(SceneCache).join(ImageAsset).filter(
            SceneCache.location == location,
            SceneCache.time_of_day == time_of_day,
            SceneCache.weather == weather,
            SceneCache.expires_at > datetime.now(),
            ImageAsset.deleted_at == None
        ).first()

        if cached:
            # Cache hit - update usage stats
            cached.use_count += 1
            cached.last_used = datetime.now()
            db.commit()
            return cached.image_asset

    # Cache miss - generate new scene
    prompt = f"A {weather} {time_of_day} at {location}. Fantasy RPG setting, detailed environment, atmospheric lighting."

    # Generate via image API (reuse logic)
    asset = await generate_image(
        request=request,
        data=GenerateImageRequest(
            subject_type="scene",
            subject_name=location,
            prompt=prompt,
            aspect_ratio="16:9",
            component="scene-viewer"
        ),
        db=db
    )

    # Create cache entry
    cache_entry = SceneCache(
        location=location,
        time_of_day=time_of_day,
        weather=weather,
        image_asset_id=asset.id,
        expires_at=datetime.now() + timedelta(days=settings.CACHE_EXPIRY_DAYS)
    )
    db.add(cache_entry)
    db.commit()

    return asset


@router.get("/cache/stats")
async def cache_stats(db: Session = Depends(get_db)):
    """
    Get cache statistics

    Returns:
    - total_scenes: Total cached scenes
    - active_cache_entries: Non-expired entries
    - expired: Expired entries waiting for cleanup
    - cache_hit_rate: Percentage of cache hits
    """
    total = db.query(SceneCache).count()
    active = db.query(SceneCache).filter(
        SceneCache.expires_at > datetime.now()
    ).count()

    # Calculate hit rate (scenes with use_count > 1)
    cache_hits = db.query(SceneCache).filter(
        SceneCache.use_count > 1
    ).count()

    hit_rate = (cache_hits / total * 100) if total > 0 else 0

    return {
        "total_scenes": total,
        "active_cache_entries": active,
        "expired": total - active,
        "cache_hit_rate": round(hit_rate, 2),
        "timestamp": datetime.now().isoformat()
    }


@router.delete("/cache/clear")
async def clear_cache(
    location: str = None,
    db: Session = Depends(get_db)
):
    """
    Clear scene cache

    If location is specified, clears only that location.
    Otherwise, clears all cache entries.
    """
    query = db.query(SceneCache)

    if location:
        query = query.filter(SceneCache.location == location)
        deleted = query.delete()
        message = f"Cleared cache for {location}"
    else:
        deleted = query.delete()
        message = "Cleared all scene cache"

    db.commit()

    return {
        "deleted": deleted,
        "message": message
    }


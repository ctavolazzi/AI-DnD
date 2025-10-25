"""Maintenance and cleanup API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..models.scene_cache import SceneCache
from ..models.image_asset import ImageAsset
from ..services.storage import StorageService
from ..config import settings

router = APIRouter(prefix="/api/v1/maintenance", tags=["maintenance"])


@router.post("/cleanup/expired-cache")
async def cleanup_expired_cache(db: Session = Depends(get_db)):
    """
    Delete expired scene cache entries

    Removes cache entries where expires_at < now().
    """
    expired = db.query(SceneCache).filter(
        SceneCache.expires_at < datetime.now()
    ).all()

    count = len(expired)
    for entry in expired:
        db.delete(entry)

    db.commit()

    return {
        "deleted": count,
        "message": f"Deleted {count} expired cache entries",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/cleanup/orphaned-images")
async def cleanup_orphaned_images(db: Session = Depends(get_db)):
    """
    Delete images marked deleted > BACKUP_RETENTION_DAYS days ago

    Performs hard delete - removes from filesystem and database.
    """
    cutoff = datetime.now() - timedelta(days=settings.BACKUP_RETENTION_DAYS)

    orphaned = db.query(ImageAsset).filter(
        ImageAsset.deleted_at < cutoff
    ).all()

    storage = StorageService(settings.IMAGE_STORAGE_DIR)
    count = 0

    for asset in orphaned:
        # Delete files
        try:
            storage.delete_image(asset.storage_path_full, asset.storage_path_thumbnail)
        except Exception as e:
            print(f"Error deleting files for asset {asset.id}: {e}")

        # Delete from database
        db.delete(asset)
        count += 1

    db.commit()

    return {
        "deleted": count,
        "message": f"Deleted {count} orphaned images",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get overall system statistics

    Returns counts and sizes for images, cache, and storage.
    """
    # Image counts
    total_images = db.query(ImageAsset).filter(ImageAsset.deleted_at == None).count()
    deleted_images = db.query(ImageAsset).filter(ImageAsset.deleted_at != None).count()

    # Cache stats
    total_cache = db.query(SceneCache).count()
    active_cache = db.query(SceneCache).filter(
        SceneCache.expires_at > datetime.now()
    ).count()

    # Storage size
    total_size = db.query(
        ImageAsset.file_size_bytes
    ).filter(
        ImageAsset.deleted_at == None
    ).all()
    total_bytes = sum(row[0] for row in total_size)
    total_mb = round(total_bytes / (1024 * 1024), 2)

    return {
        "images": {
            "active": total_images,
            "deleted": deleted_images,
            "storage_mb": total_mb
        },
        "cache": {
            "total": total_cache,
            "active": active_cache,
            "expired": total_cache - active_cache
        },
        "timestamp": datetime.now().isoformat()
    }


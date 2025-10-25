"""Migration API endpoint for LocalStorage to database migration"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any
import base64
from ..database import get_db
from ..models.image_asset import ImageAsset
from ..models.scene_cache import SceneCache
from ..services.storage import StorageService
from ..config import settings

router = APIRouter(prefix="/api/v1/migrate", tags=["migration"])


def parse_scene_key(key: str) -> tuple:
    """
    Parse LocalStorage scene cache key

    Format: scene_cache_Location_TimeOfDay_Weather
    Example: scene_cache_Emberpeak_dawn_clear
    """
    parts = key.replace('scene_cache_', '').split('_')
    if len(parts) >= 3:
        location = parts[0]
        time_of_day = parts[1]
        weather = '_'.join(parts[2:])  # Handle multi-word weather
        return location, time_of_day, weather
    return None, None, None


@router.post("/from-localstorage")
async def migrate_from_localstorage(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Migrate LocalStorage data to database

    Expected format:
    {
        "scene_cache": {
            "scene_cache_Location_Time_Weather": {
                "image": "base64_encoded_image",
                "timestamp": "ISO timestamp"
            }
        },
        "item_images": {
            "item_image_ItemName": {
                "images": [{
                    "image": "base64_encoded_image",
                    "custom_prompt": "optional",
                    "is_featured": true/false
                }]
            }
        }
    }
    """
    migrated = {
        "scenes": 0,
        "items": 0,
        "errors": [],
        "total_size_mb": 0
    }

    storage = StorageService(settings.IMAGE_STORAGE_DIR)
    total_bytes = 0

    # Migrate scene cache
    for key, value in data.get("scene_cache", {}).items():
        try:
            # Parse key
            location, time_of_day, weather = parse_scene_key(key)
            if not location:
                migrated["errors"].append({
                    "key": key,
                    "error": "Invalid key format"
                })
                continue

            # Decode base64 image
            image_b64 = value.get("image", "").split(',')[1] if ',' in value.get("image", "") else value.get("image", "")
            image_bytes = base64.b64decode(image_b64)
            total_bytes += len(image_bytes)

            # Save to filesystem
            paths = storage.save_image(image_bytes, location)

            # Create image asset
            asset = ImageAsset(
                component="scene-viewer",
                subject_type="scene",
                subject_name=location,
                prompt_used=f"A {weather} {time_of_day} at {location}. Fantasy RPG setting.",
                storage_path_full=paths["full_path"],
                storage_path_thumbnail=paths["thumbnail_path"],
                file_size_bytes=paths["file_size_bytes"],
                aspect_ratio="16:9",
                generation_time_ms=0  # Unknown for migrated images
            )
            db.add(asset)
            db.flush()  # Get asset.id

            # Create scene cache entry
            cache = SceneCache(
                location=location,
                time_of_day=time_of_day,
                weather=weather,
                image_asset_id=asset.id,
                use_count=1,
                expires_at=datetime.now() + timedelta(days=settings.CACHE_EXPIRY_DAYS)
            )
            db.add(cache)

            migrated["scenes"] += 1

        except Exception as e:
            migrated["errors"].append({
                "key": key,
                "error": str(e)
            })

    # Migrate item images
    for key, value in data.get("item_images", {}).items():
        try:
            # Parse item name
            item_name = key.replace('item_image_', '')

            # Process each image variant
            for img_data in value.get("images", []):
                # Decode base64
                image_b64 = img_data.get("image", "").split(',')[1] if ',' in img_data.get("image", "") else img_data.get("image", "")
                image_bytes = base64.b64decode(image_b64)
                total_bytes += len(image_bytes)

                # Save to filesystem
                paths = storage.save_image(image_bytes, item_name)

                # Create image asset
                asset = ImageAsset(
                    component="item-modal",
                    subject_type="item",
                    subject_name=item_name,
                    prompt_used=img_data.get("prompt", f"Item: {item_name}"),
                    custom_prompt=img_data.get("custom_prompt"),
                    storage_path_full=paths["full_path"],
                    storage_path_thumbnail=paths["thumbnail_path"],
                    file_size_bytes=paths["file_size_bytes"],
                    aspect_ratio="1:1",
                    generation_time_ms=0,  # Unknown for migrated images
                    is_featured=img_data.get("is_featured", False)
                )
                db.add(asset)

                migrated["items"] += 1

        except Exception as e:
            migrated["errors"].append({
                "key": key,
                "error": str(e)
            })

    # Commit all changes
    try:
        db.commit()
        migrated["total_size_mb"] = round(total_bytes / (1024 * 1024), 2)
        migrated["status"] = "success" if len(migrated["errors"]) == 0 else "partial"
    except Exception as e:
        db.rollback()
        migrated["status"] = "failed"
        migrated["errors"].append({
            "key": "database",
            "error": f"Commit failed: {str(e)}"
        })

    return migrated


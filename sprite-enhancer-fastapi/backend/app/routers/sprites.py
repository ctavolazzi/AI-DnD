"""Sprite generation and enhancement endpoints."""
import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services import pixellab, gemini, storage
from app.routers.auth import get_current_user

router = APIRouter()


@router.post("/generate", response_model=schemas.SpriteResponse)
async def generate_sprite(
    request: schemas.SpriteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a pixel art sprite using PixelLab.

    - **prompt**: Description of the sprite to generate
    - **size**: Size in pixels (32-512)
    - **style**: Optional style preset
    """
    try:
        # Generate sprite using PixelLab
        sprite_data = await pixellab.generate_sprite(
            prompt=request.prompt,
            size=request.size,
            no_background=True
        )

        # Upload to storage
        filename = f"sprites/user_{current_user.id}/{int(time.time())}_{request.prompt[:30]}.png"
        image_url = await storage.storage.upload_image(sprite_data, filename)

        # Save to database
        db_sprite = models.Sprite(
            user_id=current_user.id,
            prompt=request.prompt,
            image_url=image_url,
            size=request.size,
            style=request.style
        )
        db.add(db_sprite)
        db.commit()
        db.refresh(db_sprite)

        return db_sprite

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprite generation failed: {str(e)}")


@router.post("/{sprite_id}/enhance", response_model=schemas.EnhancedResponse)
async def enhance_sprite(
    sprite_id: int,
    request: schemas.EnhanceRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Enhance a sprite using Gemini AI.

    - **sprite_id**: ID of the sprite to enhance
    - **enhancement_prompt**: Description of desired enhancement
    - **style**: Enhancement style (photorealistic, fantasy, etc.)
    """
    # Get sprite
    sprite = db.query(models.Sprite).filter(
        models.Sprite.id == sprite_id,
        models.Sprite.user_id == current_user.id
    ).first()

    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")

    # Check if already enhanced
    if sprite.enhanced:
        raise HTTPException(status_code=400, detail="Sprite already enhanced. Delete the enhancement first.")

    try:
        start_time = time.time()

        # Download original sprite
        sprite_image = await storage.storage.get_image(sprite.image_url)

        # Enhance using Gemini
        enhanced_data = await gemini.enhance_image(
            sprite_image,
            enhancement_prompt=request.enhancement_prompt,
            style=request.style
        )

        generation_time = int((time.time() - start_time) * 1000)  # milliseconds

        # Upload enhanced image
        filename = f"enhanced/user_{current_user.id}/{sprite_id}_{int(time.time())}.png"
        image_url = await storage.storage.upload_image(enhanced_data, filename)

        # Save to database
        db_enhanced = models.Enhanced(
            sprite_id=sprite_id,
            image_url=image_url,
            enhancement_prompt=request.enhancement_prompt,
            style=request.style,
            generation_time=generation_time
        )
        db.add(db_enhanced)
        db.commit()
        db.refresh(db_enhanced)

        return db_enhanced

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")


@router.get("/{sprite_id}", response_model=schemas.SpriteWithEnhanced)
async def get_sprite(
    sprite_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific sprite by ID, including enhanced version if exists."""
    sprite = db.query(models.Sprite).filter(
        models.Sprite.id == sprite_id,
        models.Sprite.user_id == current_user.id
    ).first()

    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")

    return sprite


@router.delete("/{sprite_id}")
async def delete_sprite(
    sprite_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a sprite and its enhanced version."""
    sprite = db.query(models.Sprite).filter(
        models.Sprite.id == sprite_id,
        models.Sprite.user_id == current_user.id
    ).first()

    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")

    db.delete(sprite)
    db.commit()

    return {"message": "Sprite deleted successfully"}


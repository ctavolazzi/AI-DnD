"""Character Generation API endpoints with Gemini AI enhancement"""
import logging
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings
from ..models.character_enhancement import (
    CharacterGenerationRequest, CharacterGenerationResponse,
    CharacterEnhancementRequest, CharacterEnhancementResponse,
    CharacterRetrievalResponse, ErrorResponse, HealthCheckResponse,
    CharacterType, CharacterTone, EnhancementType, ThinkingLevel
)
from ..services.gemini_client import GeminiClient, GeminiError, QuotaExceededError, GenerationTimeoutError
from ..services.gemini_character_enhancer import GeminiCharacterEnhancer
from character_generator_core import CharacterGeneratorCore, CharacterType as CoreCharacterType, CharacterTone as CoreCharacterTone

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/api/character", tags=["character"])

# Global instances (in production, these would be dependency injected)
_gemini_client: Optional[GeminiClient] = None
_character_enhancer: Optional[GeminiCharacterEnhancer] = None
_character_generator: Optional[CharacterGeneratorCore] = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        # Get API key from environment
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured"
            )
        _gemini_client = GeminiClient(
            api_key=api_key,
            timeout=30,
            text_model=settings.GEMINI_MODEL,
            thinking_level=settings.GEMINI_THINKING_LEVEL
        )
    return _gemini_client


def get_character_enhancer() -> GeminiCharacterEnhancer:
    """Get or create character enhancer instance"""
    global _character_enhancer
    if _character_enhancer is None:
        gemini_client = get_gemini_client()
        _character_enhancer = GeminiCharacterEnhancer(gemini_client)
    return _character_enhancer


def get_character_generator() -> CharacterGeneratorCore:
    """Get or create character generator instance"""
    global _character_generator
    if _character_generator is None:
        _character_generator = CharacterGeneratorCore()
    return _character_generator


def convert_core_character_type(api_type: CharacterType) -> CoreCharacterType:
    """Convert API character type to core character type"""
    type_mapping = {
        CharacterType.HERO: CoreCharacterType.HERO,
        CharacterType.NPC: CoreCharacterType.NPC,
        CharacterType.VILLAIN: CoreCharacterType.VILLAIN,
        CharacterType.COMPANION: CoreCharacterType.COMPANION,
        CharacterType.MERCHANT: CoreCharacterType.MERCHANT,
        CharacterType.GUARD: CoreCharacterType.GUARD,
        CharacterType.NOBLE: CoreCharacterType.NOBLE,
        CharacterType.SCHOLAR: CoreCharacterType.SCHOLAR,
        CharacterType.COMMONER: CoreCharacterType.COMMONER,
    }
    return type_mapping.get(api_type, CoreCharacterType.HERO)


def convert_core_character_tone(api_tone: CharacterTone) -> CoreCharacterTone:
    """Convert API character tone to core character tone"""
    tone_mapping = {
        CharacterTone.REALISTIC: CoreCharacterTone.REALISTIC,
        CharacterTone.FANTASY: CoreCharacterTone.FANTASY,
        CharacterTone.SCI_FI: CoreCharacterTone.SCI_FI,
        CharacterTone.MODERN: CoreCharacterTone.MODERN,
        CharacterTone.HISTORICAL: CoreCharacterTone.HISTORICAL,
        CharacterTone.COMEDY: CoreCharacterTone.COMEDY,
        CharacterTone.DARK: CoreCharacterTone.DARK,
    }
    return tone_mapping.get(api_tone, CoreCharacterTone.FANTASY)


@router.post("/generate", response_model=CharacterGenerationResponse)
@limiter.limit("10/minute")
async def generate_character(
    request: CharacterGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a new D&D character with optional AI enhancement

    - **character_type**: Type of character to generate
    - **tone**: Tone/style of character
    - **level**: Character level (1-20)
    - **enhance_with_ai**: Whether to enhance with AI
    """
    start_time = time.time()

    try:
        # Generate base character
        generator = get_character_generator()
        core_type = convert_core_character_type(request.character_type)
        core_tone = convert_core_character_tone(request.tone)

        character = generator.generate_character(
            character_type=core_type,
            tone=core_tone,
            level=request.level
        )

        character_dict = character.to_dict()
        enhancement = None
        ai_enhanced = False
        enhancement_reason = None

        requested_thinking_level = request.thinking_level.value if request.thinking_level else None

        # Enhance with AI if requested
        if request.enhance_with_ai:
            try:
                enhancer = get_character_enhancer()
                enhancement, cache_hit = await enhancer.enhance_character(
                    character,
                    EnhancementType.FULL,
                    thinking_level=requested_thinking_level
                )
                ai_enhanced = True

                # Add enhancement data to character
                character_dict["ai_enhancement"] = enhancement.dict()

                logger.info(f"Generated and enhanced character: {character.name}")

            except QuotaExceededError:
                enhancement_reason = "quota_exceeded"
                logger.warning(f"Quota exceeded for character enhancement: {character.name}")
            except GenerationTimeoutError:
                enhancement_reason = "timeout"
                logger.warning(f"Timeout for character enhancement: {character.name}")
            except GeminiError as e:
                enhancement_reason = "error"
                logger.warning(f"AI enhancement failed for character {character.name}: {e}")

        generation_time_ms = int((time.time() - start_time) * 1000)

        return CharacterGenerationResponse(
            success=True,
            character=character_dict,
            enhancement=enhancement,
            ai_enhanced=ai_enhanced,
            enhancement_reason=enhancement_reason,
            generation_time_ms=generation_time_ms,
            cache_hit=False  # Base generation is never cached
        )

    except Exception as e:
        logger.error(f"Character generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Character generation failed: {str(e)}"
        )


@router.post("/enhance", response_model=CharacterEnhancementResponse)
@limiter.limit("20/minute")
async def enhance_character(request: CharacterEnhancementRequest):
    """
    Enhance an existing character with AI

    - **character_data**: Character data to enhance
    - **enhancement_type**: Type of enhancement (backstory, personality, quests, full)
    - **include_quests**: Whether to include quest hooks
    - **include_voice**: Whether to include character voice examples
    """
    start_time = time.time()

    try:
        enhancer = get_character_enhancer()
        requested_thinking_level = request.thinking_level.value if request.thinking_level else None

        # Enhance character
        enhancement, cache_hit = await enhancer.enhance_character(
            request.character_data,
            request.enhancement_type,
            thinking_level=requested_thinking_level
        )

        # Add enhancement to character data
        enhanced_character = request.character_data.copy()
        enhanced_character["ai_enhancement"] = enhancement.dict()

        generation_time_ms = int((time.time() - start_time) * 1000)

        return CharacterEnhancementResponse(
            success=True,
            character=enhanced_character,
            enhancement=enhancement,
            ai_enhanced=True,
            generation_time_ms=generation_time_ms,
            cache_hit=cache_hit
        )

    except QuotaExceededError:
        logger.warning("Quota exceeded for character enhancement")
        return CharacterEnhancementResponse(
            success=False,
            character=request.character_data,
            ai_enhanced=False,
            enhancement_reason="quota_exceeded",
            generation_time_ms=int((time.time() - start_time) * 1000)
        )
    except GenerationTimeoutError:
        logger.warning("Timeout for character enhancement")
        return CharacterEnhancementResponse(
            success=False,
            character=request.character_data,
            ai_enhanced=False,
            enhancement_reason="timeout",
            generation_time_ms=int((time.time() - start_time) * 1000)
        )
    except GeminiError as e:
        logger.error(f"AI enhancement failed: {e}")
        return CharacterEnhancementResponse(
            success=False,
            character=request.character_data,
            ai_enhanced=False,
            enhancement_reason="error",
            generation_time_ms=int((time.time() - start_time) * 1000)
        )
    except Exception as e:
        logger.error(f"Character enhancement failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Character enhancement failed: {str(e)}"
        )


@router.post("/generate-enhanced", response_model=CharacterGenerationResponse)
@limiter.limit("5/minute")
async def generate_enhanced_character(
    request: CharacterGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a character and enhance it with AI in one call

    This is a convenience endpoint that combines generation and enhancement.
    """
    # Set enhance_with_ai to True for this endpoint
    request.enhance_with_ai = True
    return await generate_character(request, background_tasks)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check the health of the character generation service"""
    try:
        enhancer = get_character_enhancer()
        health_data = await enhancer.health_check()

        return HealthCheckResponse(
            status=health_data["status"],
            gemini_api_available=health_data["gemini_api_available"],
            cache_status=health_data["cache_status"],
            last_check=health_data["last_check"]
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            gemini_api_available=False,
            cache_status="unknown",
            last_check=time.strftime("%Y-%m-%d %H:%M:%S")
        )


@router.post("/cache/clear")
@limiter.limit("5/minute")
async def clear_cache(request: Request):
    """Clear the character enhancement cache"""
    try:
        enhancer = get_character_enhancer()
        enhancer.clear_cache()

        return {
            "success": True,
            "message": "Character enhancement cache cleared"
        }

    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cache clear failed: {str(e)}"
        )


@router.get("/types")
async def get_character_types():
    """Get available character types"""
    return {
        "character_types": [{"value": t.value, "label": t.value.title()} for t in CharacterType],
        "character_tones": [{"value": t.value, "label": t.value.title()} for t in CharacterTone],
        "enhancement_types": [{"value": t.value, "label": t.value.title()} for t in EnhancementType]
    }


# Note: Character retrieval endpoint would require a database/storage system
# For now, we'll skip implementing GET /api/character/{character_id}
# This would be added in a future iteration with proper character storage

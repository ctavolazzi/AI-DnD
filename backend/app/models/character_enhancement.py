"""Pydantic models for character enhancement API"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class CharacterType(str, Enum):
    """Character types for API validation"""
    HERO = "hero"
    NPC = "npc"
    VILLAIN = "villain"
    COMPANION = "companion"
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    SCHOLAR = "scholar"
    COMMONER = "commoner"


class CharacterTone(str, Enum):
    """Character tones for API validation"""
    REALISTIC = "realistic"
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    MODERN = "modern"
    HISTORICAL = "historical"
    COMEDY = "comedy"
    DARK = "dark"


class EnhancementType(str, Enum):
    """Types of character enhancement"""
    BACKSTORY = "backstory"
    PERSONALITY = "personality"
    QUESTS = "quests"
    FULL = "full"


class CharacterGenerationRequest(BaseModel):
    """Request model for character generation"""
    character_type: CharacterType = Field(default=CharacterType.HERO, description="Type of character to generate")
    tone: CharacterTone = Field(default=CharacterTone.FANTASY, description="Tone/style of character")
    level: int = Field(default=1, ge=1, le=20, description="Character level")
    enhance_with_ai: bool = Field(default=True, description="Whether to enhance with AI")


class CharacterEnhancementRequest(BaseModel):
    """Request model for character enhancement"""
    character_data: Dict[str, Any] = Field(description="Character data to enhance")
    enhancement_type: EnhancementType = Field(default=EnhancementType.FULL, description="Type of enhancement")
    include_quests: bool = Field(default=True, description="Whether to include quest hooks")
    include_voice: bool = Field(default=True, description="Whether to include character voice examples")


class EnhancedBackstory(BaseModel):
    """AI-generated backstory structure"""
    backstory: str = Field(description="Rich character backstory (3-4 paragraphs)")
    early_life: Optional[str] = Field(default=None, description="Early life experiences")
    formative_events: Optional[str] = Field(default=None, description="Key events that shaped personality")
    current_situation: Optional[str] = Field(default=None, description="Current situation and challenges")
    future_aspirations: Optional[str] = Field(default=None, description="Future goals and fears")


class PersonalityInsights(BaseModel):
    """Deep personality analysis"""
    analysis: str = Field(description="Deep personality analysis")
    trait_interactions: Optional[str] = Field(default=None, description="How traits interact and create conflicts")
    development_potential: Optional[str] = Field(default=None, description="Character development opportunities")
    internal_conflicts: Optional[str] = Field(default=None, description="Internal conflicts and motivations")


class CharacterVoice(BaseModel):
    """Character voice and dialogue examples"""
    speech_pattern: str = Field(description="Character's speech pattern")
    dialogue_examples: List[str] = Field(description="Sample dialogue showing speech patterns")
    mannerisms: List[str] = Field(description="Character mannerisms and quirks")
    emotional_responses: Optional[Dict[str, str]] = Field(default=None, description="How they express different emotions")


class QuestHook(BaseModel):
    """Individual quest hook"""
    title: str = Field(description="Quest title")
    description: str = Field(description="Brief quest description")
    personal_connection: str = Field(description="How it connects to character motivations")
    potential_rewards: List[str] = Field(description="Potential rewards")
    difficulty: Optional[str] = Field(default=None, description="Quest difficulty level")


class QuestHooks(BaseModel):
    """Personalized quest opportunities"""
    quests: List[QuestHook] = Field(description="List of personalized quest hooks")
    motivation_connections: Optional[str] = Field(default=None, description="How quests connect to motivations")
    fear_challenges: Optional[str] = Field(default=None, description="How quests challenge character fears")


class CharacterEnhancement(BaseModel):
    """Complete character enhancement data"""
    backstory: Optional[EnhancedBackstory] = Field(default=None, description="Enhanced backstory")
    personality: Optional[PersonalityInsights] = Field(default=None, description="Personality insights")
    voice: Optional[CharacterVoice] = Field(default=None, description="Character voice examples")
    quests: Optional[QuestHooks] = Field(default=None, description="Personalized quest hooks")
    raw_response: Optional[str] = Field(default=None, description="Raw AI response")
    enhancement_type: EnhancementType = Field(description="Type of enhancement performed")
    generation_time_ms: Optional[int] = Field(default=None, description="Time taken to generate enhancement")


class CharacterEnhancementResponse(BaseModel):
    """Response model for character enhancement"""
    success: bool = Field(description="Whether enhancement was successful")
    character: Dict[str, Any] = Field(description="Enhanced character data")
    enhancement: Optional[CharacterEnhancement] = Field(default=None, description="AI enhancement data")
    ai_enhanced: bool = Field(description="Whether AI enhancement was applied")
    enhancement_reason: Optional[str] = Field(default=None, description="Reason if AI enhancement failed")
    generation_time_ms: Optional[int] = Field(default=None, description="Total generation time")
    cache_hit: bool = Field(default=False, description="Whether result was served from cache")


class CharacterGenerationResponse(BaseModel):
    """Response model for character generation"""
    success: bool = Field(description="Whether generation was successful")
    character: Dict[str, Any] = Field(description="Generated character data")
    enhancement: Optional[CharacterEnhancement] = Field(default=None, description="AI enhancement data")
    ai_enhanced: bool = Field(description="Whether AI enhancement was applied")
    enhancement_reason: Optional[str] = Field(default=None, description="Reason if AI enhancement failed")
    generation_time_ms: Optional[int] = Field(default=None, description="Total generation time")
    cache_hit: bool = Field(default=False, description="Whether result was served from cache")


class CharacterRetrievalResponse(BaseModel):
    """Response model for character retrieval"""
    success: bool = Field(description="Whether retrieval was successful")
    character: Optional[Dict[str, Any]] = Field(default=None, description="Character data")
    enhancement: Optional[CharacterEnhancement] = Field(default=None, description="AI enhancement data")
    found: bool = Field(description="Whether character was found")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    gemini_api_available: bool = Field(description="Whether Gemini API is available")
    cache_status: str = Field(description="Cache system status")
    last_check: str = Field(description="Last health check timestamp")

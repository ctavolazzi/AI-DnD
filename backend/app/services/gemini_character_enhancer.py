"""Gemini Character Enhancement Service"""
import logging
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from ..services.gemini_client import GeminiClient, GeminiError, QuotaExceededError, GenerationTimeoutError
from ..models.character_enhancement import (
    CharacterEnhancement, EnhancedBackstory, PersonalityInsights,
    CharacterVoice, QuestHooks, QuestHook, EnhancementType
)

logger = logging.getLogger(__name__)


class CharacterEnhancementCache:
    """Simple in-memory cache for character enhancements"""

    def __init__(self, ttl_hours: int = 1):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_hours = ttl_hours

    def _generate_key(self, character_data: Dict[str, Any], enhancement_type: str) -> str:
        """Generate cache key from character data and enhancement type"""
        # Create a stable hash from key character attributes
        key_data = {
            "name": character_data.get("name", ""),
            "character_type": character_data.get("character_type", ""),
            "primary_trait": character_data.get("primary_trait", ""),
            "motivation": character_data.get("motivation", ""),
            "enhancement_type": enhancement_type
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, character_data: Dict[str, Any], enhancement_type: str) -> Optional[Dict[str, Any]]:
        """Get cached enhancement"""
        key = self._generate_key(character_data, enhancement_type)

        if key in self.cache:
            cached_data = self.cache[key]
            cached_time = datetime.fromisoformat(cached_data["cached_at"])

            # Check if cache entry is still valid
            if datetime.now() - cached_time < timedelta(hours=self.ttl_hours):
                logger.info(f"Cache hit for enhancement type: {enhancement_type}")
                return cached_data["enhancement"]
            else:
                # Remove expired entry
                del self.cache[key]
                logger.info(f"Cache expired for enhancement type: {enhancement_type}")

        return None

    def set(self, character_data: Dict[str, Any], enhancement_type: str, enhancement: Dict[str, Any]):
        """Cache enhancement"""
        key = self._generate_key(character_data, enhancement_type)

        self.cache[key] = {
            "enhancement": enhancement,
            "cached_at": datetime.now().isoformat(),
            "enhancement_type": enhancement_type
        }

        logger.info(f"Cached enhancement for type: {enhancement_type}")

    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        logger.info("Character enhancement cache cleared")


class GeminiCharacterEnhancer:
    """Service for enhancing D&D characters using Gemini AI"""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        self.cache = CharacterEnhancementCache(ttl_hours=1)

    def _extract_character_data(self, character: Any) -> Dict[str, Any]:
        """Extract character data for enhancement prompts"""
        try:
            # Handle both Character objects and dictionaries
            if hasattr(character, 'to_dict'):
                char_dict = character.to_dict()
            elif isinstance(character, dict):
                char_dict = character
            else:
                raise ValueError("Character must be Character object or dictionary")

            # Extract key data for enhancement
            return {
                "name": char_dict.get("name", "Unknown"),
                "character_type": char_dict.get("character_type", "hero"),
                "age": char_dict.get("appearance", {}).get("age", "Unknown"),
                "gender": char_dict.get("appearance", {}).get("gender", "Unknown"),
                "occupation": char_dict.get("background", {}).get("occupation", "Adventurer"),
                "primary_trait": char_dict.get("personality", {}).get("primary_trait", "Brave"),
                "secondary_trait": char_dict.get("personality", {}).get("secondary_trait", "Loyal"),
                "motivation": char_dict.get("personality", {}).get("motivation", "adventure"),
                "fear": char_dict.get("personality", {}).get("fear", "failure"),
                "secret": char_dict.get("personality", {}).get("secret", "has a mysterious past"),
                "quirk": char_dict.get("personality", {}).get("quirk", "always punctual"),
                "goals": char_dict.get("background", {}).get("goals", ["become famous"]),
                "tone": char_dict.get("tone", "fantasy")
            }
        except Exception as e:
            logger.error(f"Error extracting character data: {e}")
            # Return minimal data
            return {
                "name": "Unknown",
                "character_type": "hero",
                "age": "Unknown",
                "gender": "Unknown",
                "occupation": "Adventurer",
                "primary_trait": "Brave",
                "secondary_trait": "Loyal",
                "motivation": "adventure",
                "fear": "failure",
                "secret": "has a mysterious past",
                "quirk": "always punctual",
                "goals": ["become famous"],
                "tone": "fantasy"
            }

    async def enhance_character(
        self,
        character: Any,
        enhancement_type: EnhancementType = EnhancementType.FULL
    ) -> Tuple[CharacterEnhancement, bool]:
        """
        Enhance a character using Gemini AI

        Args:
            character: Character object or dictionary to enhance
            enhancement_type: Type of enhancement to perform

        Returns:
            Tuple of (enhancement_data, cache_hit)

        Raises:
            GeminiError: If AI enhancement fails
        """
        character_data = self._extract_character_data(character)

        # Check cache first
        cached_enhancement = self.cache.get(character_data, enhancement_type.value)
        if cached_enhancement:
            return CharacterEnhancement(**cached_enhancement), True

        try:
            # Generate enhancement using Gemini
            enhancement_data, generation_time = self.gemini_client.generate_character_enhancement(
                character_data,
                enhancement_type.value
            )

            # Parse enhancement data into structured format
            enhancement = self._parse_enhancement_data(enhancement_data, enhancement_type, generation_time)

            # Cache the result
            self.cache.set(character_data, enhancement_type.value, enhancement.dict())

            logger.info(f"Successfully enhanced character '{character_data['name']}' with {enhancement_type.value} enhancement")
            return enhancement, False

        except QuotaExceededError as e:
            logger.warning(f"Gemini quota exceeded for character enhancement: {e}")
            raise GeminiError("AI enhancement unavailable due to quota limits") from e
        except GenerationTimeoutError as e:
            logger.warning(f"Gemini timeout for character enhancement: {e}")
            raise GeminiError("AI enhancement timed out") from e
        except Exception as e:
            logger.error(f"Unexpected error during character enhancement: {e}")
            raise GeminiError(f"Character enhancement failed: {e}") from e

    def _parse_enhancement_data(
        self,
        enhancement_data: Dict[str, Any],
        enhancement_type: EnhancementType,
        generation_time: int
    ) -> CharacterEnhancement:
        """Parse Gemini response into structured CharacterEnhancement"""

        # Extract raw response
        raw_response = enhancement_data.get("raw_response", "")

        # Initialize enhancement object
        enhancement = CharacterEnhancement(
            enhancement_type=enhancement_type,
            generation_time_ms=generation_time,
            raw_response=raw_response
        )

        try:
            if enhancement_type == EnhancementType.BACKSTORY:
                enhancement.backstory = EnhancedBackstory(backstory=raw_response)

            elif enhancement_type == EnhancementType.PERSONALITY:
                enhancement.personality = PersonalityInsights(analysis=raw_response)

            elif enhancement_type == EnhancementType.QUESTS:
                # Parse quest hooks from response
                quests = self._parse_quest_hooks(raw_response)
                enhancement.quests = quests

            else:  # FULL enhancement
                # Try to parse structured sections
                sections = enhancement_data.get("sections", {})

                # Parse backstory
                if "backstory" in sections:
                    enhancement.backstory = EnhancedBackstory(backstory=sections["backstory"])
                elif "backstory" in enhancement_data:
                    enhancement.backstory = EnhancedBackstory(backstory=enhancement_data["backstory"])

                # Parse personality insights
                if "personality" in sections:
                    enhancement.personality = PersonalityInsights(analysis=sections["personality"])
                elif "personality_analysis" in enhancement_data:
                    enhancement.personality = PersonalityInsights(analysis=enhancement_data["personality_analysis"])

                # Parse character voice
                if "voice" in sections:
                    voice_data = self._parse_character_voice(sections["voice"])
                    enhancement.voice = voice_data

                # Parse quest hooks
                if "quests" in sections:
                    quests = self._parse_quest_hooks(sections["quests"])
                    enhancement.quests = quests
                elif "quest_hooks" in enhancement_data:
                    quests = self._parse_quest_hooks(enhancement_data["quest_hooks"])
                    enhancement.quests = quests

        except Exception as e:
            logger.warning(f"Error parsing enhancement data: {e}")
            # Keep raw response even if parsing fails

        return enhancement

    def _parse_quest_hooks(self, quest_text: str) -> QuestHooks:
        """Parse quest hooks from text response"""
        try:
            # Simple parsing - look for quest patterns
            lines = quest_text.split('\n')
            quests = []

            current_quest = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for quest titles (usually start with numbers or are capitalized)
                if line and (line[0].isdigit() or line.isupper() or 'quest' in line.lower()):
                    if current_quest:
                        quests.append(QuestHook(**current_quest))
                    current_quest = {"title": line, "description": "", "personal_connection": "", "potential_rewards": []}
                elif current_quest:
                    if "description" in line.lower() or len(current_quest.get("description", "")) < 50:
                        current_quest["description"] += line + " "
                    elif "reward" in line.lower() or "gain" in line.lower():
                        current_quest["potential_rewards"].append(line)
                    else:
                        current_quest["personal_connection"] += line + " "

            # Add final quest
            if current_quest:
                quests.append(QuestHook(**current_quest))

            # If no structured quests found, create generic ones
            if not quests:
                quests = [
                    QuestHook(
                        title="Personal Quest 1",
                        description="A quest connected to your character's motivations",
                        personal_connection="This quest aligns with your character's goals",
                        potential_rewards=["Experience", "Gold", "Items"]
                    ),
                    QuestHook(
                        title="Challenge Quest",
                        description="A quest that tests your character's fears",
                        personal_connection="This quest challenges your character's weaknesses",
                        potential_rewards=["Character Growth", "New Abilities"]
                    ),
                    QuestHook(
                        title="Discovery Quest",
                        description="A quest for exploration and discovery",
                        personal_connection="This quest satisfies your character's curiosity",
                        potential_rewards=["Knowledge", "Allies", "Treasure"]
                    )
                ]

            return QuestHooks(quests=quests)

        except Exception as e:
            logger.warning(f"Error parsing quest hooks: {e}")
            # Return default quest hooks
            return QuestHooks(quests=[
                QuestHook(
                    title="Default Quest",
                    description="A personalized quest for your character",
                    personal_connection="Connected to your motivations",
                    potential_rewards=["Experience", "Gold"]
                )
            ])

    def _parse_character_voice(self, voice_text: str) -> CharacterVoice:
        """Parse character voice from text response"""
        try:
            lines = voice_text.split('\n')
            dialogue_examples = []
            mannerisms = []
            speech_pattern = ""

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for dialogue (usually in quotes)
                if '"' in line or "'" in line:
                    dialogue_examples.append(line)
                elif "speech" in line.lower() or "pattern" in line.lower():
                    speech_pattern = line
                elif "mannerism" in line.lower() or "quirk" in line.lower():
                    mannerisms.append(line)

            return CharacterVoice(
                speech_pattern=speech_pattern or "Clear and direct",
                dialogue_examples=dialogue_examples or ["Hello there!", "I see what you mean."],
                mannerisms=mannerisms or ["Adjusts equipment", "Looks around carefully"]
            )

        except Exception as e:
            logger.warning(f"Error parsing character voice: {e}")
            return CharacterVoice(
                speech_pattern="Clear and direct",
                dialogue_examples=["Hello there!", "I see what you mean."],
                mannerisms=["Adjusts equipment", "Looks around carefully"]
            )

    async def health_check(self) -> Dict[str, Any]:
        """Check if the enhancement service is healthy"""
        try:
            # Test Gemini API with a simple prompt
            test_prompt = "Say 'Hello' if you can respond."
            response, _ = self.gemini_client.generate_text(test_prompt)

            return {
                "status": "healthy",
                "gemini_api_available": True,
                "cache_status": "operational",
                "cache_size": len(self.cache.cache),
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "gemini_api_available": False,
                "cache_status": "operational",
                "cache_size": len(self.cache.cache),
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }

    def clear_cache(self):
        """Clear the enhancement cache"""
        self.cache.clear()
        logger.info("Character enhancement cache cleared")

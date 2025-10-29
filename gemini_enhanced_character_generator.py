#!/usr/bin/env python3
"""
🚀 Gemini API Cookbook Enhanced D&D Character Generator
Leverages the latest Gemini capabilities for AI-enhanced character creation
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterType(Enum):
    HERO = "hero"
    VILLAIN = "villain"
    NEUTRAL = "neutral"
    COMPANION = "companion"

class CharacterTone(Enum):
    SERIOUS = "serious"
    COMEDY = "comedy"
    DARK = "dark"
    EPIC = "epic"
    MYSTERY = "mystery"

@dataclass
class EnhancedCharacter:
    """Base character data structure"""
    name: str
    char_class: str
    race: str
    level: int
    background: str
    ability_scores: Dict[str, int]

@dataclass
class GeminiCharacterEnhancement:
    """AI-enhanced character data from Gemini"""
    ai_backstory: str
    ai_personality_insights: str
    ai_character_voice: str
    ai_quest_hooks: List[str]
    ai_relationship_dynamics: str
    ai_character_goals: List[str]
    ai_character_flaws: List[str]

class EnhancedCharacterGenerator:
    """Base character generator"""

    def generate_character(self, character_type=None, tone=None, level=1):
        """Generate a base character"""
        return EnhancedCharacter(
            name="Test Character",
            char_class="Fighter",
            race="Human",
            level=level,
            background="Soldier",
            ability_scores={"str": 15, "dex": 14, "con": 13, "int": 12, "wis": 11, "cha": 10}
        )

    def to_dict(self, character):
        """Convert character to dictionary"""
        return {
            "name": character.name,
            "char_class": character.char_class,
            "race": character.race,
            "level": character.level,
            "background": character.background,
            "ability_scores": character.ability_scores
        }

class GeminiEnhancedCharacterGenerator:
    """Enhanced character generator with Gemini AI integration"""

    def __init__(self, gemini_client=None):
        self.base_generator = EnhancedCharacterGenerator()
        self.gemini_client = gemini_client
        self.enhancement_cache = {}

    async def generate_ai_enhanced_character(self, character_type: CharacterType = None, tone: CharacterTone = None, level: int = 1) -> Dict[str, Any]:
        """Generate a character with AI-enhanced details using Gemini"""

        # Generate base character
        base_character = self.base_generator.generate_character(character_type, tone, level)

        # Enhance with AI if Gemini client is available
        if self.gemini_client:
            try:
                ai_enhancement = await self._generate_ai_enhancement(base_character)
                return self._merge_character_data(base_character, ai_enhancement)
            except Exception as e:
                logger.warning(f"AI enhancement failed, using base character: {e}")
                return self.base_generator.to_dict(base_character)
        else:
            logger.info("No Gemini client available, using base character generation")
            return self.base_generator.to_dict(base_character)

    async def _generate_ai_enhancement(self, character: EnhancedCharacter) -> GeminiCharacterEnhancement:
        """Generate AI enhancement using Gemini API"""

        # Create cache key
        cache_key = f"{character.name}_{character.char_class}_{character.race}"

        if cache_key in self.enhancement_cache:
            logger.info(f"Using cached enhancement for {character.name}")
            return self.enhancement_cache[cache_key]

        prompt = f"""
        Generate a comprehensive AI enhancement for this D&D character:

        Character Details:
        - Name: {character.name}
        - Class: {character.char_class}
        - Race: {character.race}
        - Level: {character.level}
        - Background: {character.background}
        - Stats: {character.ability_scores}

        Please provide a JSON response with the following structure:
        {{
            "ai_backstory": "A rich, detailed 3-4 paragraph backstory that explains how this character came to be, their motivations, and key life events that shaped them.",
            "ai_personality_insights": "Deep analysis of how their stats and class interact to create unique personality traits and behavioral patterns.",
            "ai_character_voice": "Specific examples of how this character speaks, including dialogue samples and speech patterns.",
            "ai_quest_hooks": ["Quest hook 1", "Quest hook 2", "Quest hook 3"],
            "ai_relationship_dynamics": "How this character interacts with others, their social patterns, and relationship tendencies.",
            "ai_character_goals": ["Primary goal", "Secondary goal", "Personal goal"],
            "ai_character_flaws": ["Flaw 1", "Flaw 2", "Hidden weakness"]
        }}

        Make the content rich, detailed, and suitable for D&D roleplay. Focus on creating depth and complexity that will make this character memorable and engaging.
        """

        try:
            # Call Gemini API
            response = await self.gemini_client.generate_content({
                'model': 'gemini-2.5-flash',
                'contents': [{'parts': [{'text': prompt}]}]
            })

            # Parse response
            response_text = response.text
            logger.info(f"Gemini response received: {len(response_text)} characters")

            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                enhancement_data = json.loads(json_text)

                return GeminiCharacterEnhancement(
                    ai_backstory=enhancement_data.get('ai_backstory', ''),
                    ai_personality_insights=enhancement_data.get('ai_personality_insights', ''),
                    ai_character_voice=enhancement_data.get('ai_character_voice', ''),
                    ai_quest_hooks=enhancement_data.get('ai_quest_hooks', []),
                    ai_relationship_dynamics=enhancement_data.get('ai_relationship_dynamics', ''),
                    ai_character_goals=enhancement_data.get('ai_character_goals', []),
                    ai_character_flaws=enhancement_data.get('ai_character_flaws', [])
                )
            else:
                logger.warning("Could not extract JSON from Gemini response")
                return self._create_fallback_enhancement()

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._create_fallback_enhancement()

    def _create_fallback_enhancement(self) -> GeminiCharacterEnhancement:
        """Create fallback enhancement when AI is unavailable"""
        return GeminiCharacterEnhancement(
            ai_backstory="A mysterious character with a hidden past that drives their current motivations.",
            ai_personality_insights="Their stats suggest a balanced approach to challenges, adapting their strategy based on the situation.",
            ai_character_voice="Speaks with measured words, choosing their phrases carefully.",
            ai_quest_hooks=["Seeking answers about their past", "Protecting those they care about", "Mastering their abilities"],
            ai_relationship_dynamics="Forms deep bonds with those who earn their trust, but remains guarded with strangers.",
            ai_character_goals=["Uncover their true purpose", "Become stronger", "Find their place in the world"],
            ai_character_flaws=["Trusts too easily", "Fear of failure", "Stubbornness"]
        )

    def _merge_character_data(self, base_character: EnhancedCharacter, ai_enhancement: GeminiCharacterEnhancement) -> Dict[str, Any]:
        """Merge base character data with AI enhancements"""
        character_dict = self.base_generator.to_dict(base_character)

        # Add AI enhancements
        character_dict.update({
            'ai_enhanced': True,
            'ai_backstory': ai_enhancement.ai_backstory,
            'ai_personality_insights': ai_enhancement.ai_personality_insights,
            'ai_character_voice': ai_enhancement.ai_character_voice,
            'ai_quest_hooks': ai_enhancement.ai_quest_hooks,
            'ai_relationship_dynamics': ai_enhancement.ai_relationship_dynamics,
            'ai_character_goals': ai_enhancement.ai_character_goals,
            'ai_character_flaws': ai_enhancement.ai_character_flaws
        })

        return character_dict

    async def generate_character_portrait(self, character_data: Dict[str, Any]) -> Optional[str]:
        """Generate character portrait using Gemini Image generation"""
        if not self.gemini_client:
            logger.warning("No Gemini client available for image generation")
            return None

        try:
            portrait_prompt = f"""
            Create a detailed fantasy character portrait for:
            - Name: {character_data.get('name', 'Unknown')}
            - Class: {character_data.get('char_class', 'Adventurer')}
            - Race: {character_data.get('race', 'Human')}
            - Level: {character_data.get('level', 1)}

            Style: D&D fantasy art, detailed, professional, high quality
            Include: Character equipment, appropriate fantasy setting, detailed facial features
            """

            # Note: This would use Gemini Image generation when available
            # For now, return a placeholder
            logger.info("Character portrait generation requested")
            return "placeholder_portrait_url"

        except Exception as e:
            logger.error(f"Error generating character portrait: {e}")
            return None

    async def generate_character_quests(self, character_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized quests based on character backstory and goals"""
        if not self.gemini_client:
            logger.warning("No Gemini client available for quest generation")
            return []

        try:
            quest_prompt = f"""
            Based on this D&D character's details, generate 3 unique quests:

            Character: {character_data.get('name', 'Unknown')}
            Class: {character_data.get('char_class', 'Adventurer')}
            Race: {character_data.get('race', 'Human')}
            Level: {character_data.get('level', 1)}
            Goals: {character_data.get('ai_character_goals', [])}
            Flaws: {character_data.get('ai_character_flaws', [])}

            Generate quests that:
            1. Connect to their personal goals
            2. Challenge their fears and flaws
            3. Utilize their class abilities
            4. Create meaningful character development

            Return as JSON array with quest objects containing:
            - title: Quest name
            - description: Quest details
            - objectives: List of objectives
            - rewards: Potential rewards
            - difficulty: Easy/Medium/Hard
            - quest_hook: How it connects to character
            """

            response = await self.gemini_client.generate_content({
                'model': 'gemini-2.5-flash',
                'contents': [{'parts': [{'text': quest_prompt}]}]
            })

            # Parse quest response
            response_text = response.text
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                logger.warning("Could not parse quest response from Gemini")
                return []

        except Exception as e:
            logger.error(f"Error generating character quests: {e}")
            return []

# Example usage and testing
async def main():
    """Test the enhanced character generator"""
    logger.info("🚀 Testing Gemini Enhanced Character Generator")

    # Initialize generator (without Gemini client for testing)
    generator = GeminiEnhancedCharacterGenerator()

    # Generate a test character
    character = await generator.generate_ai_enhanced_character(
        character_type=CharacterType.HERO,
        tone=CharacterTone.EPIC,
        level=5
    )

    logger.info(f"Generated character: {character.get('name', 'Unknown')}")
    logger.info(f"AI Enhanced: {character.get('ai_enhanced', False)}")

    # Test quest generation
    quests = await generator.generate_character_quests(character)
    logger.info(f"Generated {len(quests)} quests for character")

if __name__ == "__main__":
    asyncio.run(main())
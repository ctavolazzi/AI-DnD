#!/usr/bin/env python3
"""
Gemini-Powered Narrative Decision Making Engine
Integrates Google Gemini 2.5 Flash API for intelligent D&D storytelling and decision support
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv is optional
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NarrativeContext:
    """Context for narrative generation"""
    campaign_id: str
    session_id: str
    current_scene: str
    player_actions: List[str]
    npc_states: Dict[str, Any]
    world_state: Dict[str, Any]
    campaign_tone: str = "epic"
    difficulty_level: str = "medium"

@dataclass
class DecisionOption:
    """Represents a decision option with AI reasoning"""
    option: str
    reasoning: str
    consequences: List[str]
    probability_success: float
    risk_level: str
    alignment: str  # good, neutral, evil

@dataclass
class StoryBranch:
    """Represents a story branch with predicted outcomes"""
    branch_name: str
    description: str
    immediate_consequences: List[str]
    long_term_effects: List[str]
    character_impact: Dict[str, str]
    world_changes: List[str]

@dataclass
class NPCBehavior:
    """Represents AI-generated NPC behavior"""
    npc_name: str
    personality_traits: List[str]
    current_mood: str
    reaction: str
    dialogue_suggestions: List[str]
    action_recommendations: List[str]

class GeminiNarrativeEngine:
    """Main engine for Gemini-powered narrative decision making"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini narrative engine"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        # Log API key status for debugging
        if self.api_key:
            logger.info(f"✅ Gemini API key loaded: {self.api_key[:10]}...")
        else:
            logger.warning("⚠️ No Gemini API key found - will use fallback mode")
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-3-pro-preview')
        self.thinking_level = self._validate_thinking_level(os.getenv('GEMINI_THINKING_LEVEL', 'high'))
        self.client = None
        self.safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),
        ]

        if self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1alpha"}
                )
                logger.info("✅ Gemini Narrative Engine initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ No Gemini API key found, engine will use fallback mode")

    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client is not None

    async def generate_narrative_response(
        self,
        context: NarrativeContext,
        prompt: str,
        max_tokens: int = 1000,
        thinking_level: Optional[str] = None
    ) -> str:
        """Generate narrative response using Gemini"""
        if not self.is_available():
            raise RuntimeError("Gemini engine not available")

        try:
            # Build context-aware prompt
            full_prompt = self._build_narrative_prompt(context, prompt)

            # Generate response
            response_text = await asyncio.to_thread(
                self._generate_text,
                full_prompt,
                max_output_tokens=max_tokens,
                temperature=0.8,
                top_p=0.9,
                top_k=40,
                thinking_level=thinking_level
            )

            return response_text.strip()

        except Exception as e:
            logger.error(f"❌ Error generating narrative response: {e}")
            raise

    def generate_decision_matrix(
        self,
        context: NarrativeContext,
        decision_scenario: str,
        options: List[str],
        thinking_level: Optional[str] = None
    ) -> List[DecisionOption]:
        """Generate AI-powered decision matrix with reasoning"""
        if not self.is_available():
            raise RuntimeError("Gemini engine not available")

        try:
            prompt = f"""
            As an expert D&D Dungeon Master, analyze this decision scenario and provide AI reasoning for each option.

            Scenario: {decision_scenario}
            Campaign Tone: {context.campaign_tone}
            Difficulty: {context.difficulty_level}

            Available Options:
            {chr(10).join(f"{i+1}. {option}" for i, option in enumerate(options))}

            For each option, provide:
            1. Reasoning (why this choice makes sense)
            2. Consequences (what happens next)
            3. Success probability (0.0-1.0)
            4. Risk level (low/medium/high)
            5. Alignment (good/neutral/evil)

            Format as JSON array with fields: option, reasoning, consequences, probability_success, risk_level, alignment
            """

            response_text = self._generate_text(
                prompt,
                max_output_tokens=800,
                temperature=0.7,
                thinking_level=thinking_level
            )
            decision_data = json.loads(response_text)

            return [
                DecisionOption(
                    option=item['option'],
                    reasoning=item['reasoning'],
                    consequences=item['consequences'],
                    probability_success=float(item['probability_success']),
                    risk_level=item['risk_level'],
                    alignment=item['alignment']
                )
                for item in decision_data
            ]

        except Exception as e:
            logger.error(f"❌ Error generating decision matrix: {e}")
            # Return fallback options
            return [
                DecisionOption(
                    option=option,
                    reasoning="AI analysis unavailable",
                    consequences=["Unknown consequences"],
                    probability_success=0.5,
                    risk_level="medium",
                    alignment="neutral"
                )
                for option in options
            ]

    def analyze_story_branches(
        self,
        context: NarrativeContext,
        player_choice: str,
        thinking_level: Optional[str] = None
    ) -> List[StoryBranch]:
        """Analyze potential story branches from player choice"""
        if not self.is_available():
            raise RuntimeError("Gemini engine not available")

        try:
            prompt = f"""
            As an expert D&D storyteller, analyze the potential story branches from this player choice.

            Current Scene: {context.current_scene}
            Player Choice: {player_choice}
            Campaign Tone: {context.campaign_tone}

            Generate 3-5 potential story branches with:
            1. Branch name and description
            2. Immediate consequences
            3. Long-term effects
            4. Character impact (how it affects each character)
            5. World changes (how it affects the game world)

            Format as JSON array with fields: branch_name, description, immediate_consequences, long_term_effects, character_impact, world_changes
            """

            response_text = self._generate_text(
                prompt,
                max_output_tokens=900,
                temperature=0.75,
                thinking_level=thinking_level
            )
            branch_data = json.loads(response_text)

            return [
                StoryBranch(
                    branch_name=item['branch_name'],
                    description=item['description'],
                    immediate_consequences=item['immediate_consequences'],
                    long_term_effects=item['long_term_effects'],
                    character_impact=item['character_impact'],
                    world_changes=item['world_changes']
                )
                for item in branch_data
            ]

        except Exception as e:
            logger.error(f"❌ Error analyzing story branches: {e}")
            return []

    def generate_npc_behavior(
        self,
        context: NarrativeContext,
        npc_name: str,
        npc_personality: str,
        situation: str,
        thinking_level: Optional[str] = None
    ) -> NPCBehavior:
        """Generate dynamic NPC behavior based on personality and situation"""
        if not self.is_available():
            raise RuntimeError("Gemini engine not available")

        try:
            prompt = f"""
            As an expert D&D character actor, generate realistic NPC behavior.

            NPC: {npc_name}
            Personality: {npc_personality}
            Current Situation: {situation}
            Campaign Tone: {context.campaign_tone}

            Generate:
            1. Current mood based on situation
            2. Realistic reaction
            3. Dialogue suggestions (3-5 options)
            4. Action recommendations (what the NPC might do)

            Format as JSON with fields: personality_traits, current_mood, reaction, dialogue_suggestions, action_recommendations
            """

            response_text = self._generate_text(
                prompt,
                max_output_tokens=700,
                temperature=0.65,
                thinking_level=thinking_level
            )
            behavior_data = json.loads(response_text)

            return NPCBehavior(
                npc_name=npc_name,
                personality_traits=behavior_data['personality_traits'],
                current_mood=behavior_data['current_mood'],
                reaction=behavior_data['reaction'],
                dialogue_suggestions=behavior_data['dialogue_suggestions'],
                action_recommendations=behavior_data['action_recommendations']
            )

        except Exception as e:
            logger.error(f"❌ Error generating NPC behavior: {e}")
            return NPCBehavior(
                npc_name=npc_name,
                personality_traits=["Unknown"],
                current_mood="neutral",
                reaction="The NPC remains silent",
                dialogue_suggestions=["NPC says nothing"],
                action_recommendations=["NPC waits"]
            )

    def generate_adaptive_story(
        self,
        context: NarrativeContext,
        story_element: str,
        thinking_level: Optional[str] = None
    ) -> str:
        """Generate adaptive story content based on campaign progression"""
        if not self.is_available():
            raise RuntimeError("Gemini engine not available")

        try:
            prompt = f"""
            As an expert D&D storyteller, create adaptive story content that evolves with the campaign.

            Story Element: {story_element}
            Campaign Tone: {context.campaign_tone}
            Difficulty: {context.difficulty_level}
            Player Actions: {', '.join(context.player_actions[-5:])}  # Last 5 actions
            World State: {json.dumps(context.world_state, indent=2)}

            Create engaging, adaptive content that:
            1. Builds on previous player actions
            2. Reflects the current world state
            3. Maintains campaign tone and difficulty
            4. Provides meaningful choices and consequences

            Return as narrative text (2-3 paragraphs).
            """

            response_text = self._generate_text(
                prompt,
                max_output_tokens=600,
                temperature=0.85,
                thinking_level=thinking_level
            )
            return response_text.strip()

        except Exception as e:
            logger.error(f"❌ Error generating adaptive story: {e}")
            return f"Story content for {story_element} is being prepared..."

    def _build_narrative_prompt(self, context: NarrativeContext, prompt: str) -> str:
        """Build context-aware prompt for narrative generation"""
        return f"""
        You are an expert D&D Dungeon Master with deep knowledge of storytelling, character development, and game mechanics.

        CAMPAIGN CONTEXT:
        - Campaign ID: {context.campaign_id}
        - Session ID: {context.session_id}
        - Current Scene: {context.current_scene}
        - Campaign Tone: {context.campaign_tone}
        - Difficulty Level: {context.difficulty_level}

        RECENT PLAYER ACTIONS:
        {chr(10).join(f"- {action}" for action in context.player_actions[-3:])}

        NPC STATES:
        {json.dumps(context.npc_states, indent=2)}

        WORLD STATE:
        {json.dumps(context.world_state, indent=2)}

        PLAYER REQUEST:
        {prompt}

        Provide a compelling, immersive response that:
        1. Maintains narrative consistency
        2. Reflects the campaign tone and difficulty
        3. Builds on previous actions and world state
        4. Offers meaningful choices and consequences
        5. Enhances the overall storytelling experience

        Response:
        """

    def _generate_text(
        self,
        prompt: str,
        *,
        max_output_tokens: int = 600,
        temperature: float = 0.8,
        top_p: float = 0.9,
        top_k: int = 40,
        thinking_level: Optional[str] = None
    ) -> str:
        """Call Gemini and return concatenated text output."""
        if not self.is_available():
            raise RuntimeError("Gemini engine not available")

        level = self._validate_thinking_level(thinking_level) if thinking_level else self.thinking_level
        config_kwargs = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
            "safety_settings": self.safety_settings
        }
        if level:
            config_kwargs["thinking_level"] = level

        try:
            config = types.GenerateContentConfig(**config_kwargs)
        except Exception as e:
            # Fallback for older SDK versions that don't support thinking_level
            if "thinking_level" in config_kwargs:
                logger.warning(f"⚠️ 'thinking_level' not supported by installed SDK version: {e}")
                del config_kwargs["thinking_level"]
                config = types.GenerateContentConfig(**config_kwargs)
            else:
                raise e

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt],
            config=config
        )

        return self._extract_text(response)

    def _extract_text(self, response: Any) -> str:
        """Extract plain text from a Gemini response."""
        if not response or not getattr(response, "candidates", None):
            raise ValueError("No candidates in Gemini response")

        text_parts: List[str] = []
        for candidate in response.candidates:
            content = getattr(candidate, "content", None)
            if not content or not getattr(content, "parts", None):
                continue
            for part in content.parts:
                if getattr(part, "text", None):
                    text_parts.append(part.text)

        if not text_parts:
            raise ValueError("No text parts in Gemini response")

        return "\n".join(text_parts).strip()

    def _validate_thinking_level(self, level: Optional[str]) -> Optional[str]:
        """Normalize and validate requested thinking level."""
        if level is None:
            return "high"

        normalized = str(level).lower().strip()
        allowed_levels = {"low", "high"}
        if normalized not in allowed_levels:
            logger.warning(f"⚠️ Invalid thinking level '{level}' provided. Falling back to 'high'.")
            return "high"
        return normalized

    def set_thinking_level(self, level: str) -> str:
        """Update the default thinking level for future generations."""
        self.thinking_level = self._validate_thinking_level(level)
        return self.thinking_level

    def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status and capabilities"""
        return {
            "engine_name": "Gemini Narrative Engine",
            "version": "1.0.0",
            "gemini_available": self.is_available(),
            "api_key_configured": bool(self.api_key),
            "model": self.model_name if self.is_available() else None,
            "thinking_level": self.thinking_level,
            "capabilities": [
                "narrative_generation",
                "decision_matrix",
                "story_branch_analysis",
                "npc_behavior_generation",
                "adaptive_storytelling"
            ],
            "timestamp": datetime.now().isoformat()
        }

    # =========================================================================
    # LEGACY COMPATIBILITY METHODS (for narrative_engine.py interface)
    # =========================================================================

    def generate_quest(self, difficulty="medium", theme=None, thinking_level: Optional[str] = None):
        """Generate a quest using Gemini or fallback"""
        if not self.is_available():
            return f"A {difficulty} quest in a fantasy world" + (f" with theme: {theme}" if theme else "")

        try:
            prompt = f"Generate a {difficulty} difficulty D&D quest"
            if theme:
                prompt += f" with the theme: {theme}"
            prompt += ". Provide a concise quest description with objectives."

            response_text = self._generate_text(
                prompt,
                max_output_tokens=300,
                temperature=0.8,
                thinking_level=thinking_level
            )
            return response_text.strip()
        except Exception as e:
            logger.error(f"Error generating quest: {e}")
            return f"Embark on a {difficulty} quest" + (f" themed around {theme}" if theme else "")

    def generate_random_encounter(self, party_level, environment, thinking_level: Optional[str] = None):
        """Generate a random encounter"""
        if not self.is_available():
            return f"You encounter enemies in the {environment}"

        try:
            prompt = f"Generate a brief D&D encounter for a level {party_level} party in a {environment}. Just describe what they encounter in 2-3 sentences."
            response_text = self._generate_text(
                prompt,
                max_output_tokens=200,
                temperature=0.8,
                thinking_level=thinking_level
            )
            return response_text.strip()
        except Exception as e:
            logger.error(f"Error generating encounter: {e}")
            return f"You encounter hostile creatures in the {environment}!"

    def describe_scene(self, location, characters, thinking_level: Optional[str] = None):
        """Describe a scene"""
        if not self.is_available():
            return f"{', '.join(characters)} stand in {location}"

        try:
            chars = ', '.join(characters)
            prompt = f"Describe in 2-3 vivid sentences: {chars} arrive at {location}. Make it atmospheric and engaging."
            response_text = self._generate_text(
                prompt,
                max_output_tokens=200,
                temperature=0.8,
                thinking_level=thinking_level
            )
            return response_text.strip()
        except Exception as e:
            logger.error(f"Error describing scene: {e}")
            return f"{chars} arrive at {location}, ready for adventure."

    def handle_player_action(self, player_name, action, context=None, thinking_level: Optional[str] = None):
        """Handle and narrate a player action"""
        if not self.is_available():
            return f"{player_name} {action}."

        try:
            prompt = f"Narrate in 1-2 sentences: {player_name} {action}. Make it engaging."
            if context:
                prompt += f" Context: {context}"
            response_text = self._generate_text(
                prompt,
                max_output_tokens=150,
                temperature=0.8,
                thinking_level=thinking_level
            )
            return response_text.strip()
        except Exception as e:
            logger.error(f"Error handling player action: {e}")
            return f"{player_name} {action}."

    def describe_combat(self, attacker, target, damage=0, success=True, thinking_level: Optional[str] = None):
        """Describe a combat action"""
        if not self.is_available():
            if success:
                return f"{attacker} hits {target} for {damage} damage!"
            else:
                return f"{attacker} misses {target}!"

        try:
            if success:
                prompt = f"In 1 sentence, describe: {attacker} successfully hits {target} dealing {damage} damage. Make it cinematic."
            else:
                prompt = f"In 1 sentence, describe: {attacker} attacks {target} but misses. Make it dramatic."

            response_text = self._generate_text(
                prompt,
                max_output_tokens=100,
                temperature=0.8,
                thinking_level=thinking_level
            )
            return response_text.strip()
        except Exception as e:
            logger.error(f"Error describing combat: {e}")
            if success:
                return f"{attacker} strikes {target} for {damage} damage!"
            else:
                return f"{attacker} swings but {target} dodges!"

# Global engine instance
narrative_engine = GeminiNarrativeEngine()

def get_narrative_engine() -> GeminiNarrativeEngine:
    """Get the global narrative engine instance"""
    return narrative_engine

# Example usage and testing
if __name__ == "__main__":
    async def test_engine():
        """Test the narrative engine functionality"""
        engine = get_narrative_engine()

        print("🤖 Gemini Narrative Engine Test")
        print("=" * 50)

        # Test engine status
        status = engine.get_engine_status()
        print(f"Engine Status: {json.dumps(status, indent=2)}")

        if engine.is_available():
            print("\n✅ Testing Gemini Integration...")

            # Create test context
            context = NarrativeContext(
                campaign_id="test_campaign",
                session_id="test_session",
                current_scene="A mysterious tavern",
                player_actions=["Entered tavern", "Approached bartender"],
                npc_states={"bartender": {"mood": "suspicious", "trust": 0.3}},
                world_state={"weather": "stormy", "time": "night"},
                campaign_tone="mystery",
                difficulty_level="medium"
            )

            try:
                # Test narrative generation
                response = await engine.generate_narrative_response(
                    context,
                    "The bartender looks at you suspiciously. What do you say?"
                )
                print(f"\n📖 Narrative Response:\n{response}")

                # Test decision matrix
                options = ["Ask about rumors", "Order a drink", "Leave quietly"]
                decisions = engine.generate_decision_matrix(
                    context,
                    "How do you interact with the suspicious bartender?",
                    options
                )
                print(f"\n🧠 Decision Matrix:")
                for decision in decisions:
                    print(f"- {decision.option}: {decision.reasoning}")

            except Exception as e:
                print(f"❌ Test failed: {e}")
        else:
            print("⚠️ Gemini not available - using fallback mode")

    # Run test
    asyncio.run(test_engine())

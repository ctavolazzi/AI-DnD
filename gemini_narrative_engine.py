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
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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
        self.model = None
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    'gemini-2.0-flash-exp',
                    safety_settings=self.safety_settings
                )
                logger.info("✅ Gemini Narrative Engine initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.model = None
        else:
            logger.warning("⚠️ No Gemini API key found, engine will use fallback mode")

    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.model is not None

    async def generate_narrative_response(
        self,
        context: NarrativeContext,
        prompt: str,
        max_tokens: int = 1000
    ) -> str:
        """Generate narrative response using Gemini"""
        if not self.is_available():
            raise RuntimeError("Gemini engine not available")

        try:
            # Build context-aware prompt
            full_prompt = self._build_narrative_prompt(context, prompt)

            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40
                )
            )

            return response.text.strip()

        except Exception as e:
            logger.error(f"❌ Error generating narrative response: {e}")
            raise

    def generate_decision_matrix(
        self,
        context: NarrativeContext,
        decision_scenario: str,
        options: List[str]
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

            response = self.model.generate_content(prompt)
            decision_data = json.loads(response.text)

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
        player_choice: str
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

            response = self.model.generate_content(prompt)
            branch_data = json.loads(response.text)

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
        situation: str
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

            response = self.model.generate_content(prompt)
            behavior_data = json.loads(response.text)

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
        story_element: str
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

            response = self.model.generate_content(prompt)
            return response.text.strip()

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

    def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status and capabilities"""
        return {
            "engine_name": "Gemini Narrative Engine",
            "version": "1.0.0",
            "gemini_available": self.is_available(),
            "api_key_configured": bool(self.api_key),
            "model": "gemini-2.0-flash-exp" if self.is_available() else None,
            "capabilities": [
                "narrative_generation",
                "decision_matrix",
                "story_branch_analysis",
                "npc_behavior_generation",
                "adaptive_storytelling"
            ],
            "timestamp": datetime.now().isoformat()
        }

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
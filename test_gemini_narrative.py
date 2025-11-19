#!/usr/bin/env python3
"""
Comprehensive Test Suite for Gemini-Powered Narrative Decision Making
Tests all components of the enhanced D&D narrative system
"""

import os
import sys
import json
import asyncio
import unittest
from unittest.mock import patch, MagicMock
import requests
import time

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_narrative_engine import (
    GeminiNarrativeEngine,
    NarrativeContext,
    DecisionOption,
    StoryBranch,
    NPCBehavior,
    get_narrative_engine
)
from narrative_engine import create_narrative_engine

class TestGeminiNarrativeEngine(unittest.TestCase):
    """Test the core Gemini narrative engine functionality"""

    def setUp(self):
        """Set up test environment"""
        self.engine = GeminiNarrativeEngine()
        # Ensure engine reports available without requiring real API calls
        self.engine.client = MagicMock()
        self.context = NarrativeContext(
            campaign_id="test_campaign",
            session_id="test_session",
            current_scene="A mysterious tavern",
            player_actions=["Entered tavern", "Approached bartender"],
            npc_states={"bartender": {"mood": "suspicious", "trust": 0.3}},
            world_state={"weather": "stormy", "time": "night"},
            campaign_tone="mystery",
            difficulty_level="medium"
        )

    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsInstance(self.engine, GeminiNarrativeEngine)
        self.assertIsNotNone(self.engine.api_key)
        self.assertIsNotNone(self.engine.safety_settings)
        # Thinking level might be None if not set in environment, forcing default
        # But get_engine_status should report the effective level
        status = self.engine.get_engine_status()
        self.assertIn(status["thinking_level"], ("low", "high"))

    def test_engine_status(self):
        """Test engine status reporting"""
        status = self.engine.get_engine_status()

        self.assertIn("engine_name", status)
        self.assertIn("version", status)
        self.assertIn("gemini_available", status)
        self.assertIn("capabilities", status)
        self.assertIn("timestamp", status)
        self.assertIn("thinking_level", status)

        self.assertEqual(status["engine_name"], "Gemini Narrative Engine")
        self.assertEqual(status["version"], "1.0.0")
        self.assertIsInstance(status["capabilities"], list)

    def test_context_creation(self):
        """Test narrative context creation"""
        self.assertEqual(self.context.campaign_id, "test_campaign")
        self.assertEqual(self.context.session_id, "test_session")
        self.assertEqual(self.context.current_scene, "A mysterious tavern")
        self.assertEqual(len(self.context.player_actions), 2)
        self.assertIn("bartender", self.context.npc_states)
        self.assertEqual(self.context.campaign_tone, "mystery")

    def test_narrative_response_generation(self):
        """Test narrative response generation with mocked Gemini"""
        mock_text = "The bartender eyes you suspiciously and mutters something under his breath."

        # Test async function
        async def run_test():
            with patch.object(self.engine, '_generate_text', return_value=mock_text):
                response = await self.engine.generate_narrative_response(
                    self.context,
                    "The bartender looks at you suspiciously. What do you say?"
                )
                self.assertIn("bartender", response.lower())
                self.assertIn("suspicious", response.lower())

        asyncio.run(run_test())

    def test_decision_matrix_generation(self):
        """Test decision matrix generation"""
        scenario = "How do you interact with the suspicious bartender?"
        options = ["Ask about rumors", "Order a drink", "Leave quietly"]

        # Test with mocked Gemini
        with patch.object(self.engine, '_generate_text') as mock_generate:
            mock_generate.return_value = json.dumps([
                {
                    "option": "Ask about rumors",
                    "reasoning": "This could reveal valuable information",
                    "consequences": ["Bartender becomes more suspicious", "May learn about local events"],
                    "probability_success": 0.6,
                    "risk_level": "medium",
                    "alignment": "neutral"
                },
                {
                    "option": "Order a drink",
                    "reasoning": "A neutral approach to gain trust",
                    "consequences": ["Bartender relaxes", "Opportunity for conversation"],
                    "probability_success": 0.8,
                    "risk_level": "low",
                    "alignment": "neutral"
                },
                {
                    "option": "Leave quietly",
                    "reasoning": "Avoids potential conflict",
                    "consequences": ["No information gained", "Safe but unproductive"],
                    "probability_success": 1.0,
                    "risk_level": "low",
                    "alignment": "neutral"
                }
            ])

            decisions = self.engine.generate_decision_matrix(
                self.context, scenario, options
            )

            self.assertEqual(len(decisions), 3)
            self.assertIsInstance(decisions[0], DecisionOption)
            self.assertEqual(decisions[0].option, "Ask about rumors")
            self.assertEqual(decisions[0].probability_success, 0.6)
            self.assertEqual(decisions[0].risk_level, "medium")

    def test_story_branch_analysis(self):
        """Test story branch analysis"""
        player_choice = "Ask the bartender about recent strange events"

        with patch.object(self.engine, '_generate_text') as mock_generate:
            mock_generate.return_value = json.dumps([
                {
                    "branch_name": "Information Gathering",
                    "description": "The bartender shares valuable information",
                    "immediate_consequences": ["Learn about missing travelers", "Bartender becomes helpful"],
                    "long_term_effects": ["Access to local knowledge", "Potential ally"],
                    "character_impact": {"party": "Gains crucial information"},
                    "world_changes": ["Local rumors become known", "Bartender's attitude shifts"]
                }
            ])

            branches = self.engine.analyze_story_branches(
                self.context, player_choice
            )

            self.assertEqual(len(branches), 1)
            self.assertIsInstance(branches[0], StoryBranch)
            self.assertEqual(branches[0].branch_name, "Information Gathering")
            self.assertIn("missing travelers", branches[0].immediate_consequences[0])

    def test_npc_behavior_generation(self):
        """Test NPC behavior generation"""
        npc_name = "Gareth the Bartender"
        npc_personality = "Suspicious but knowledgeable about local events"
        situation = "Strangers asking questions in his tavern"

        with patch.object(self.engine, '_generate_text') as mock_generate:
            mock_generate.return_value = json.dumps({
                "personality_traits": ["suspicious", "knowledgeable", "protective"],
                "current_mood": "wary",
                "reaction": "Gareth eyes you carefully, weighing whether to trust you",
                "dialogue_suggestions": [
                    "What brings strangers to my tavern?",
                    "I don't talk to just anyone about local matters",
                    "Maybe I've heard something... for the right price"
                ],
                "action_recommendations": [
                    "Continue serving drinks while observing",
                    "Signal to regulars to keep an eye on strangers",
                    "Prepare to call for help if needed"
                ]
            })

            behavior = self.engine.generate_npc_behavior(
                self.context, npc_name, npc_personality, situation
            )

            self.assertIsInstance(behavior, NPCBehavior)
            self.assertEqual(behavior.npc_name, npc_name)
            self.assertEqual(behavior.current_mood, "wary")
            self.assertIn("suspicious", behavior.personality_traits)
            self.assertEqual(len(behavior.dialogue_suggestions), 3)
            self.assertEqual(len(behavior.action_recommendations), 3)

    def test_adaptive_story_generation(self):
        """Test adaptive story generation"""
        story_element = "A mysterious figure approaches the party"

        mock_story = (
            "As the storm rages outside, a hooded figure emerges from the shadows of the tavern."
        )

        with patch.object(self.engine, '_generate_text', return_value=mock_story):

            story_content = self.engine.generate_adaptive_story(
                self.context, story_element
            )

            self.assertIsInstance(story_content, str)
            self.assertIn("hooded figure", story_content.lower())
            self.assertIn("tavern", story_content.lower())
            self.assertGreater(len(story_content), 50)

    def test_thinking_level_override(self):
        """Test that thinking level can be overridden per call"""
        mock_text = "Thoughtful response"

        # We need to patch the client to check if the config was passed correctly
        self.engine.client.models.generate_content = MagicMock(return_value=MagicMock(candidates=[MagicMock(content=MagicMock(parts=[MagicMock(text=mock_text)]))]))

        # Patch GenerateContentConfig to accept any kwargs for test purposes
        # This simulates the newer SDK version that supports thinking_level
        with patch('google.genai.types.GenerateContentConfig', lambda **kwargs: MagicMock(**kwargs)):
            self.engine._generate_text("Test prompt", thinking_level="low")

            # Check arguments passed to generate_content
            call_args = self.engine.client.models.generate_content.call_args
            self.assertIsNotNone(call_args)
            kwargs = call_args[1]
            self.assertIn("config", kwargs)
            # Verify thinking_level in config
            self.assertEqual(kwargs["config"].thinking_level, "low")

class TestNarrativeEngineIntegration(unittest.TestCase):
    """Test integration between Gemini and Ollama engines"""

    def test_create_narrative_engine_gemini(self):
        """Test creating narrative engine with Gemini"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            engine = create_narrative_engine("gemini")
            self.assertIsNotNone(engine)

    def test_create_narrative_engine_ollama(self):
        """Test creating narrative engine with Ollama fallback"""
        with patch.dict(os.environ, {}, clear=True):
            engine = create_narrative_engine("ollama")
            self.assertIsNotNone(engine)
            # Should be Ollama engine when Gemini not available
            self.assertFalse(hasattr(engine, 'generate_decision_matrix'))

class TestNarrativeServerAPI(unittest.TestCase):
    """Test the narrative server API endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5002"
        self.session_id = None

    def test_server_health(self):
        """Test if server is running"""
        try:
            response = requests.get(f"{self.base_url}/ai/engine-status", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("engine_status", data)
        except requests.exceptions.RequestException:
            self.skipTest("Server not running - start with: python3 dnd_narrative_server.py")

    def test_start_adventure(self):
        """Test starting a new adventure"""
        try:
            response = requests.post(
                f"{self.base_url}/start-adventure",
                json={"model": "gemini"},
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("session_id", data)
            self.assertIn("characters", data)
            self.assertIn("quest", data)
            self.assertIn("first_scene", data)

            self.session_id = data["session_id"]
        except requests.exceptions.RequestException:
            self.skipTest("Server not running - start with: python3 dnd_narrative_server.py")

    def test_decision_matrix_endpoint(self):
        """Test decision matrix API endpoint"""
        if not self.session_id:
            self.skipTest("No session ID available")

        try:
            response = requests.post(
                f"{self.base_url}/ai/decision-matrix",
                json={
                    "session_id": self.session_id,
                    "scenario": "How do you approach the mysterious stranger?",
                    "options": ["Greet politely", "Draw weapon", "Ignore them"]
                },
                timeout=15
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("decisions", data)
            self.assertEqual(len(data["decisions"]), 3)

            # Check decision structure
            decision = data["decisions"][0]
            self.assertIn("option", decision)
            self.assertIn("reasoning", decision)
            self.assertIn("consequences", decision)
            self.assertIn("probability_success", decision)
            self.assertIn("risk_level", decision)
            self.assertIn("alignment", decision)

        except requests.exceptions.RequestException:
            self.skipTest("Server not running - start with: python3 dnd_narrative_server.py")

    def test_story_branches_endpoint(self):
        """Test story branches API endpoint"""
        if not self.session_id:
            self.skipTest("No session ID available")

        try:
            response = requests.post(
                f"{self.base_url}/ai/story-branches",
                json={
                    "session_id": self.session_id,
                    "player_choice": "The party decides to investigate the mysterious stranger"
                },
                timeout=15
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("branches", data)
            self.assertGreater(len(data["branches"]), 0)

            # Check branch structure
            branch = data["branches"][0]
            self.assertIn("branch_name", branch)
            self.assertIn("description", branch)
            self.assertIn("immediate_consequences", branch)
            self.assertIn("long_term_effects", branch)
            self.assertIn("character_impact", branch)
            self.assertIn("world_changes", branch)

        except requests.exceptions.RequestException:
            self.skipTest("Server not running - start with: python3 dnd_narrative_server.py")

    def test_npc_behavior_endpoint(self):
        """Test NPC behavior API endpoint"""
        if not self.session_id:
            self.skipTest("No session ID available")

        try:
            response = requests.post(
                f"{self.base_url}/ai/npc-behavior",
                json={
                    "session_id": self.session_id,
                    "npc_name": "Elena the Mystic",
                    "npc_personality": "Wise but secretive, knows ancient lore",
                    "situation": "Party seeks information about magical artifacts"
                },
                timeout=15
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("behavior", data)

            # Check behavior structure
            behavior = data["behavior"]
            self.assertIn("npc_name", behavior)
            self.assertIn("personality_traits", behavior)
            self.assertIn("current_mood", behavior)
            self.assertIn("reaction", behavior)
            self.assertIn("dialogue_suggestions", behavior)
            self.assertIn("action_recommendations", behavior)

        except requests.exceptions.RequestException:
            self.skipTest("Server not running - start with: python3 dnd_narrative_server.py")

    def test_adaptive_story_endpoint(self):
        """Test adaptive story API endpoint"""
        if not self.session_id:
            self.skipTest("No session ID available")

        try:
            response = requests.post(
                f"{self.base_url}/ai/adaptive-story",
                json={
                    "session_id": self.session_id,
                    "story_element": "A magical portal appears in the tavern"
                },
                timeout=15
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("story_content", data)
            self.assertIsInstance(data["story_content"], str)
            self.assertGreater(len(data["story_content"]), 20)

        except requests.exceptions.RequestException:
            self.skipTest("Server not running - start with: python3 dnd_narrative_server.py")

class TestErrorHandling(unittest.TestCase):
    """Test error handling and fallback behavior"""

    def test_gemini_unavailable_fallback(self):
        """Test fallback when Gemini is unavailable"""
        with patch.dict(os.environ, {}, clear=True):
            engine = create_narrative_engine("gemini")
            # Should fallback to Ollama
            self.assertIsNotNone(engine)

    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses"""
        engine = GeminiNarrativeEngine()
        engine.client = MagicMock()

        with patch.object(engine, '_generate_text', return_value="Invalid JSON response"):
            # Should return fallback options
            decisions = engine.generate_decision_matrix(
                NarrativeContext(
                    campaign_id="test",
                    session_id="test",
                    current_scene="test",
                    player_actions=[],
                    npc_states={},
                    world_state={}
                ),
                "Test scenario",
                ["Option 1", "Option 2"]
            )

            self.assertEqual(len(decisions), 2)
            self.assertEqual(decisions[0].reasoning, "AI analysis unavailable")

    def test_api_error_handling(self):
        """Test API error handling"""
        try:
            response = requests.post(
                "http://localhost:5002/ai/decision-matrix",
                json={
                    "session_id": "invalid_session",
                    "scenario": "Test",
                    "options": ["Option 1"]
                },
                timeout=5
            )
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertFalse(data["success"])
            self.assertIn("error", data)
        except requests.exceptions.RequestException:
            self.skipTest("Server not running")

def run_performance_test():
    """Run performance tests"""
    print("\n🚀 Running Performance Tests...")

    engine = GeminiNarrativeEngine()
    context = NarrativeContext(
        campaign_id="perf_test",
        session_id="perf_test",
        current_scene="Performance test scene",
        player_actions=["Test action"],
        npc_states={},
        world_state={}
    )

    # Test response time
    start_time = time.time()

    if engine.is_available():
        print("✅ Gemini engine available - testing performance")
        # Test would go here with actual API calls
    else:
        print("⚠️ Gemini not available - testing Ollama fallback")
        ollama_engine = create_narrative_engine("ollama")
        response = ollama_engine.generate_quest(difficulty="medium", theme="performance test")
        print(f"✅ Ollama response time: {time.time() - start_time:.2f}s")
        print(f"📝 Response: {response}")

def run_integration_test():
    """Run integration test with actual server"""
    print("\n🔗 Running Integration Test...")

    try:
        # Test server status
        response = requests.get("http://localhost:5002/ai/engine-status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")

            # Test starting adventure
            response = requests.post(
                "http://localhost:5002/start-adventure",
                json={"model": "gemini"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                session_id = data["session_id"]
                print(f"✅ Adventure started: {session_id}")

                # Test AI features
                test_scenarios = [
                    {
                        "endpoint": "/ai/decision-matrix",
                        "data": {
                            "session_id": session_id,
                            "scenario": "How do you approach the dragon?",
                            "options": ["Fight", "Negotiate", "Flee"]
                        }
                    },
                    {
                        "endpoint": "/ai/story-branches",
                        "data": {
                            "session_id": session_id,
                            "player_choice": "The party decides to negotiate with the dragon"
                        }
                    }
                ]

                for scenario in test_scenarios:
                    response = requests.post(
                        f"http://localhost:5002{scenario['endpoint']}",
                        json=scenario["data"],
                        timeout=15
                    )

                    if response.status_code == 200:
                        print(f"✅ {scenario['endpoint']} working")
                    else:
                        print(f"❌ {scenario['endpoint']} failed: {response.status_code}")
            else:
                print(f"❌ Failed to start adventure: {response.status_code}")
        else:
            print("❌ Server not responding")

    except requests.exceptions.RequestException as e:
        print(f"❌ Server connection failed: {e}")
        print("💡 Start server with: python3 dnd_narrative_server.py")

if __name__ == "__main__":
    print("🧪 Gemini-Powered Narrative Decision Making - Test Suite")
    print("=" * 60)

    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run performance tests
    run_performance_test()

    # Run integration tests
    run_integration_test()

    print("\n🎉 Test Suite Complete!")
    print("\n📝 To run the full system:")
    print("1. Set GEMINI_API_KEY environment variable")
    print("2. Start server: python3 dnd_narrative_server.py")
    print("3. Open: dnd-narrative-theater.html")
    print("4. Select Gemini 2.5 Flash and start adventure")
    print("5. Use AI Decision Support features!")

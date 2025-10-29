#!/usr/bin/env python3
"""
FastAPI Migration Test Suite

This script tests the newly migrated FastAPI endpoints to ensure they work correctly.
It validates the complete game logic integration with the FastAPI backend.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class FastAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session_id = None
        self.character_ids = []
        self.location_ids = []

    def test_health(self) -> bool:
        """Test basic health endpoint"""
        print("🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def test_root(self) -> bool:
        """Test root endpoint"""
        print("🔍 Testing root endpoint...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root endpoint: {data['name']} v{data['version']}")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False

    def test_game_session_creation(self) -> bool:
        """Test game session creation"""
        print("🔍 Testing game session creation...")
        try:
            data = {
                "name": "FastAPI Migration Test",
                "difficulty": "medium",
                "ai_model": "mistral"
            }
            response = requests.post(f"{self.api_base}/game/sessions", json=data)
            if response.status_code == 201:
                session_data = response.json()
                self.session_id = session_data["id"]
                print(f"✅ Session created: {session_data['name']} (ID: {self.session_id})")
                return True
            else:
                print(f"❌ Session creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            return False

    def test_character_creation(self) -> bool:
        """Test character creation"""
        print("🔍 Testing character creation...")
        try:
            characters = [
                {"name": "Test Fighter", "char_class": "Fighter", "team": "player"},
                {"name": "Test Wizard", "char_class": "Wizard", "team": "player"},
                {"name": "Test Goblin", "char_class": "Goblin", "team": "enemy"}
            ]

            for char_data in characters:
                response = requests.post(
                    f"{self.api_base}/game-logic/sessions/{self.session_id}/characters",
                    json=char_data
                )
                if response.status_code == 200:
                    char_info = response.json()
                    self.character_ids.append(char_info["id"])
                    print(f"✅ Character created: {char_info['name']} ({char_info['char_class']})")
                else:
                    print(f"❌ Character creation failed: {response.status_code} - {response.text}")
                    return False
            return True
        except Exception as e:
            print(f"❌ Character creation error: {e}")
            return False

    def test_location_creation(self) -> bool:
        """Test location creation"""
        print("🔍 Testing location creation...")
        try:
            locations = [
                {
                    "name": "Test Tavern",
                    "description": "A cozy tavern for testing",
                    "location_type": "tavern",
                    "npcs": [{"name": "Barkeep", "type": "merchant"}],
                    "items": [{"name": "Health Potion", "type": "consumable"}]
                },
                {
                    "name": "Test Dungeon",
                    "description": "A dangerous dungeon for testing",
                    "location_type": "dungeon",
                    "npcs": [{"name": "Goblin Guard", "type": "enemy"}],
                    "items": [{"name": "Rusty Sword", "type": "weapon"}]
                }
            ]

            for loc_data in locations:
                response = requests.post(
                    f"{self.api_base}/narrative/sessions/{self.session_id}/locations",
                    json=loc_data
                )
                if response.status_code == 200:
                    loc_info = response.json()
                    self.location_ids.append(loc_info["id"])
                    print(f"✅ Location created: {loc_info['name']} ({loc_info['location_type']})")
                else:
                    print(f"❌ Location creation failed: {response.status_code} - {response.text}")
                    return False
            return True
        except Exception as e:
            print(f"❌ Location creation error: {e}")
            return False

    def test_combat_system(self) -> bool:
        """Test combat system"""
        print("🔍 Testing combat system...")
        try:
            if len(self.character_ids) < 2:
                print("❌ Need at least 2 characters for combat test")
                return False

            # Test attack action
            attacker_id = self.character_ids[0]  # Fighter
            target_id = self.character_ids[2]    # Goblin

            combat_data = {
                "action_type": "attack",
                "target_id": target_id,
                "attacker_id": attacker_id
            }

            response = requests.post(
                f"{self.api_base}/game-logic/sessions/{self.session_id}/combat/action",
                params={"char_id": attacker_id},
                json=combat_data
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Combat action: {result['description']}")
                return True
            else:
                print(f"❌ Combat action failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Combat system error: {e}")
            return False

    def test_narrative_events(self) -> bool:
        """Test narrative event creation"""
        print("🔍 Testing narrative events...")
        try:
            event_data = {
                "event_type": "combat",
                "description": "A fierce battle breaks out in the tavern!",
                "location_id": self.location_ids[0] if self.location_ids else None,
                "character_ids": self.character_ids[:2],
                "data": {"damage": 15, "victory": True}
            }

            response = requests.post(
                f"{self.api_base}/narrative/sessions/{self.session_id}/events",
                json=event_data
            )

            if response.status_code == 200:
                event_info = response.json()
                print(f"✅ Event created: {event_info['description']}")
                return True
            else:
                print(f"❌ Event creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Narrative events error: {e}")
            return False

    def test_frontend_integration(self) -> bool:
        """Test frontend integration endpoints"""
        print("🔍 Testing frontend integration...")
        try:
            # Test dashboard data
            response = requests.get(f"{self.api_base}/frontend/sessions/{self.session_id}/dashboard")
            if response.status_code == 200:
                dashboard = response.json()
                print(f"✅ Dashboard data: {dashboard['statistics']['characters']} characters, {dashboard['statistics']['locations']} locations")
            else:
                print(f"❌ Dashboard failed: {response.status_code}")
                return False

            # Test game state summary
            response = requests.get(f"{self.api_base}/frontend/sessions/{self.session_id}/state")
            if response.status_code == 200:
                state = response.json()
                print(f"✅ Game state: {len(state['characters'])} characters, turn {state['session']['turn_count']}")
            else:
                print(f"❌ Game state failed: {response.status_code}")
                return False

            # Test quick action
            response = requests.post(
                f"{self.api_base}/frontend/sessions/{self.session_id}/quick-action",
                params={"action": "move", "target_id": self.location_ids[0] if self.location_ids else None}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Quick action: {result['message']}")
            else:
                print(f"❌ Quick action failed: {response.status_code}")
                return False

            return True
        except Exception as e:
            print(f"❌ Frontend integration error: {e}")
            return False

    def test_quest_system(self) -> bool:
        """Test quest system"""
        print("🔍 Testing quest system...")
        try:
            quest_data = {
                "title": "Test Quest",
                "description": "A quest to test the system",
                "objectives": [
                    {"type": "kill", "target": "goblin", "count": 1},
                    {"type": "collect", "item": "health_potion", "count": 1}
                ],
                "reward_type": "experience",
                "reward_value": 100
            }

            response = requests.post(
                f"{self.api_base}/game-logic/sessions/{self.session_id}/quests",
                json=quest_data
            )

            if response.status_code == 200:
                quest_info = response.json()
                print(f"✅ Quest created: {quest_info['title']}")
                return True
            else:
                print(f"❌ Quest creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Quest system error: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        print("🚀 Starting FastAPI Migration Test Suite")
        print("=" * 60)

        tests = [
            ("Health Check", self.test_health),
            ("Root Endpoint", self.test_root),
            ("Game Session Creation", self.test_game_session_creation),
            ("Character Creation", self.test_character_creation),
            ("Location Creation", self.test_location_creation),
            ("Combat System", self.test_combat_system),
            ("Narrative Events", self.test_narrative_events),
            ("Quest System", self.test_quest_system),
            ("Frontend Integration", self.test_frontend_integration)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")

        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 ALL TESTS PASSED! FastAPI migration is successful!")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
            return False


def main():
    """Main test runner"""
    print("FastAPI Migration Test Suite")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Start it with: cd backend && python -m uvicorn app.main:app --reload")
    print()

    # Wait for user confirmation
    input("Press Enter when the server is ready...")

    tester = FastAPITester()
    success = tester.run_all_tests()

    if success:
        print("\n🎯 FastAPI Migration Complete!")
        print("The backend now provides comprehensive API endpoints for:")
        print("- Game session management")
        print("- Character creation and management")
        print("- Combat system")
        print("- Location and world management")
        print("- Narrative events")
        print("- Quest system")
        print("- Frontend integration")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the server logs and fix any issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()

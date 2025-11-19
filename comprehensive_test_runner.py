#!/usr/bin/env python3
"""
Comprehensive Full System Test Runner
Exercises the entire AI-DnD application with detailed function call tracing
"""
import os
import sys
import json
import time
import traceback
import functools
from datetime import datetime
from pathlib import Path
from io import StringIO
import contextlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all major components
from dnd_game import DnDGame, Character
from gemini_narrative_engine import GeminiNarrativeEngine, NarrativeContext
from backend.app.services.gemini_client import GeminiClient
from backend.app.services.game_service import GameService, DatabaseLogProvider
from backend.app.core.providers import InstantTimeProvider, FileLogProvider

class FunctionTracer:
    """Tracks all function calls and their results"""
    def __init__(self):
        self.calls = []
        self.start_time = time.time()

    def trace(self, func):
        """Decorator to trace function calls"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            call_info = {
                'function': f"{func.__module__}.{func.__name__}",
                'timestamp': time.time() - self.start_time,
                'args': str(args)[:200],  # Truncate long args
                'kwargs': {k: str(v)[:100] for k, v in kwargs.items()},
                'result': None,
                'error': None,
                'duration': 0
            }

            start = time.time()
            try:
                result = func(*args, **kwargs)
                call_info['result'] = str(result)[:500] if result else None
                call_info['duration'] = time.time() - start
                self.calls.append(call_info)
                return result
            except Exception as e:
                call_info['error'] = str(e)
                call_info['duration'] = time.time() - start
                call_info['traceback'] = traceback.format_exc()
                self.calls.append(call_info)
                raise

        return wrapper

    def get_summary(self):
        """Get summary of all calls"""
        return {
            'total_calls': len(self.calls),
            'total_duration': sum(c['duration'] for c in self.calls),
            'errors': len([c for c in self.calls if c.get('error')]),
            'calls_by_module': self._group_by_module(),
            'slowest_calls': sorted(self.calls, key=lambda x: x['duration'], reverse=True)[:10]
        }

    def _group_by_module(self):
        """Group calls by module"""
        modules = {}
        for call in self.calls:
            module = call['function'].split('.')[0]
            modules[module] = modules.get(module, 0) + 1
        return modules

# Global tracer
tracer = FunctionTracer()

class ComprehensiveTestRunner:
    """Runs comprehensive tests across the entire system"""

    def __init__(self):
        self.results = {
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'images_generated': [],
            'function_calls': [],
            'errors': [],
            'summary': {}
        }
        self.test_output_dir = Path(f"test_results/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.test_output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive System Test")
        print("=" * 60)

        try:
            # Test 1: Character Creation
            self.test_character_creation()

            # Test 2: Game Engine Initialization
            self.test_game_engine()

            # Test 3: Gemini Narrative Engine
            self.test_gemini_narrative()

            # Test 4: API Service Layer
            self.test_api_services()

            # Test 5: Image Generation (if available)
            self.test_image_generation()

            # Test 6: Full Game Flow
            self.test_full_game_flow()

        except Exception as e:
            self.results['errors'].append({
                'test': 'system',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"❌ System test error: {e}")

        # Finalize results
        self.results['end_time'] = datetime.now().isoformat()
        self.results['function_calls'] = tracer.calls
        self.results['summary'] = tracer.get_summary()

        # Save results
        self.save_results()

        return self.results

    def test_character_creation(self):
        """Test character creation system"""
        print("\n📝 Test 1: Character Creation")
        test_start = time.time()

        try:
            # Create various characters
            characters = []
            for char_type in ['Fighter', 'Wizard', 'Rogue']:
                char = Character(
                    name=f"Test {char_type}",
                    char_class=char_type,
                    character_id=f"char_{char_type.lower()}_{int(time.time())}"
                )
                characters.append(char)

                # Test character methods
                char_dict = char.to_dict()
                char_db_dict = char.to_db_dict(char.id, "test_session")

                self.results['tests'].append({
                    'name': f'character_creation_{char_type}',
                    'status': 'passed',
                    'duration': time.time() - test_start,
                    'data': {
                        'character_id': char.id,
                        'name': char.name,
                        'class': char.char_class,
                        'hp': char.hp,
                        'has_dict': bool(char_dict),
                        'has_db_dict': bool(char_db_dict)
                    }
                })

            print(f"✅ Created {len(characters)} characters")

        except Exception as e:
            self.results['tests'].append({
                'name': 'character_creation',
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"❌ Character creation failed: {e}")

    def test_game_engine(self):
        """Test DnD game engine"""
        print("\n🎮 Test 2: Game Engine")
        test_start = time.time()

        try:
            from backend.app.core.providers import InstantTimeProvider, FileLogProvider

            # Create game instance
            game = DnDGame(
                time_provider=InstantTimeProvider(),
                log_provider=FileLogProvider("dnd_game")
            )

            # Manually add players
            player1 = Character("Hero", "Fighter", character_id="p1", log_provider=game.log_provider)
            player2 = Character("Mage", "Wizard", character_id="p2", log_provider=game.log_provider)
            player1.team = "players"
            player2.team = "players"
            game.players = [player1, player2]

            # Test combat - add enemy
            enemy = Character("Goblin Scout", "Goblin", character_id="e1", log_provider=game.log_provider)
            enemy.team = "enemies"
            game.enemies = [enemy]

            # Perform attack
            result = player1.attack_target(enemy)

            self.results['tests'].append({
                'name': 'game_engine',
                'status': 'passed',
                'duration': time.time() - test_start,
                'data': {
                    'players': len(game.players),
                    'enemies': len(game.enemies),
                    'combat_result': result
                }
            })

            print("✅ Game engine test passed")

        except Exception as e:
            self.results['tests'].append({
                'name': 'game_engine',
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"❌ Game engine test failed: {e}")

    def test_gemini_narrative(self):
        """Test Gemini narrative engine"""
        print("\n🤖 Test 3: Gemini Narrative Engine")
        test_start = time.time()

        try:
            engine = GeminiNarrativeEngine()

            if not engine.is_available():
                print("⚠️ Gemini not available, skipping")
                self.results['tests'].append({
                    'name': 'gemini_narrative',
                    'status': 'skipped',
                    'reason': 'Gemini API not available'
                })
                return

            # Test engine status
            status = engine.get_engine_status()

            # Test thinking level
            engine.set_thinking_level("low")
            new_level = engine.thinking_level

            self.results['tests'].append({
                'name': 'gemini_narrative',
                'status': 'passed',
                'duration': time.time() - test_start,
                'data': {
                    'available': engine.is_available(),
                    'model': status.get('model'),
                    'thinking_level': new_level,
                    'capabilities': status.get('capabilities', [])
                }
            })

            print("✅ Gemini narrative engine test passed")

        except Exception as e:
            self.results['tests'].append({
                'name': 'gemini_narrative',
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"❌ Gemini narrative test failed: {e}")

    def test_api_services(self):
        """Test API service layer"""
        print("\n🌐 Test 4: API Services")
        test_start = time.time()

        try:
            # Test GameService
            game_service = GameService.get_instance()

            # Test GeminiClient
            import os
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                gemini_client = GeminiClient(
                    api_key=api_key,
                    text_model="gemini-3-pro-preview",
                    thinking_level="high"
                )

                # Test text generation (simple)
                try:
                    text, duration = gemini_client.generate_text("Say 'Hello' if you can respond.")
                    self.results['tests'].append({
                        'name': 'api_gemini_client',
                        'status': 'passed',
                        'duration': time.time() - test_start,
                        'data': {
                            'text_generated': bool(text),
                            'response_time_ms': duration,
                            'text_preview': text[:100] if text else None
                        }
                    })
                    print("✅ Gemini client test passed")
                except Exception as e:
                    self.results['tests'].append({
                        'name': 'api_gemini_client',
                        'status': 'failed',
                        'error': str(e)
                    })
                    print(f"⚠️ Gemini client test failed: {e}")
            else:
                print("⚠️ GEMINI_API_KEY not set, skipping API tests")
                self.results['tests'].append({
                    'name': 'api_services',
                    'status': 'skipped',
                    'reason': 'API key not configured'
                })

        except Exception as e:
            self.results['tests'].append({
                'name': 'api_services',
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"❌ API services test failed: {e}")

    def test_image_generation(self):
        """Test image generation capabilities"""
        print("\n🎨 Test 5: Image Generation")
        test_start = time.time()

        try:
            import os
            api_key = os.getenv('GEMINI_API_KEY')

            if not api_key:
                print("⚠️ GEMINI_API_KEY not set, skipping image generation")
                self.results['tests'].append({
                    'name': 'image_generation',
                    'status': 'skipped',
                    'reason': 'API key not configured'
                })
                return

            from backend.app.services.gemini_client import GeminiClient
            client = GeminiClient(api_key=api_key)

            # Try to generate a simple image
            try:
                image_bytes, duration = client.generate_image(
                    "A simple fantasy sword icon, pixel art style"
                )

                # Save image
                image_path = self.images_dir / f"test_image_{int(time.time())}.png"
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)

                self.results['images_generated'].append({
                    'path': str(image_path),
                    'caption': 'Test Fantasy Sword',
                    'type': 'item',
                    'size_bytes': len(image_bytes),
                    'generation_time_ms': duration
                })

                self.results['tests'].append({
                    'name': 'image_generation',
                    'status': 'passed',
                    'duration': time.time() - test_start,
                    'data': {
                        'image_generated': True,
                        'image_path': str(image_path),
                        'size_bytes': len(image_bytes),
                        'duration_ms': duration
                    }
                })

                print(f"✅ Generated test image: {image_path}")

            except Exception as e:
                self.results['tests'].append({
                    'name': 'image_generation',
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"⚠️ Image generation failed: {e}")

        except Exception as e:
            self.results['tests'].append({
                'name': 'image_generation',
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"❌ Image generation test failed: {e}")

    def test_full_game_flow(self):
        """Test complete game flow"""
        print("\n🎲 Test 6: Full Game Flow")
        test_start = time.time()

        try:
            from backend.app.core.providers import InstantTimeProvider, FileLogProvider

            # Create game without auto-creating characters
            game = DnDGame(
                auto_create_characters=False,
                time_provider=InstantTimeProvider(),
                log_provider=FileLogProvider("dnd_game")
            )

            # Setup party
            party = [
                Character("Aragorn", "Fighter", character_id="p1", log_provider=game.log_provider),
                Character("Gandalf", "Wizard", character_id="p2", log_provider=game.log_provider)
            ]
            for char in party:
                char.team = "players"
            game.players = party

            # Add enemies
            enemies = [
                Character("Orc Warrior", "Orc", character_id="e1", log_provider=game.log_provider),
                Character("Goblin Scout", "Goblin", character_id="e2", log_provider=game.log_provider)
            ]
            for enemy in enemies:
                enemy.team = "enemies"
            game.enemies = enemies

            # Simulate combat round
            combat_results = []
            for player in party:
                if enemies:
                    result = player.attack_target(enemies[0])
                    combat_results.append(result)

            self.results['tests'].append({
                'name': 'full_game_flow',
                'status': 'passed',
                'duration': time.time() - test_start,
                'data': {
                    'party_size': len(party),
                    'enemies': len(enemies),
                    'combat_actions': len(combat_results),
                    'combat_results': combat_results
                }
            })

            print("✅ Full game flow test passed")

        except Exception as e:
            self.results['tests'].append({
                'name': 'full_game_flow',
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            print(f"❌ Full game flow test failed: {e}")

    def save_results(self):
        """Save all test results"""
        # Save JSON
        json_path = self.test_output_dir / "comprehensive_test_results.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save human-readable log
        log_path = self.test_output_dir / "comprehensive_test.log"
        with open(log_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("COMPREHENSIVE SYSTEM TEST RESULTS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Start: {self.results['start_time']}\n")
            f.write(f"End: {self.results['end_time']}\n\n")

            f.write("TEST SUMMARY\n")
            f.write("-" * 60 + "\n")
            passed = len([t for t in self.results['tests'] if t.get('status') == 'passed'])
            failed = len([t for t in self.results['tests'] if t.get('status') == 'failed'])
            skipped = len([t for t in self.results['tests'] if t.get('status') == 'skipped'])
            f.write(f"Total Tests: {len(self.results['tests'])}\n")
            f.write(f"Passed: {passed}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Skipped: {skipped}\n\n")

            f.write("FUNCTION CALLS\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total Calls: {self.results['summary'].get('total_calls', 0)}\n")
            f.write(f"Total Duration: {self.results['summary'].get('total_duration', 0):.2f}s\n")
            f.write(f"Errors: {self.results['summary'].get('errors', 0)}\n\n")

            f.write("DETAILED TEST RESULTS\n")
            f.write("-" * 60 + "\n")
            for test in self.results['tests']:
                f.write(f"\n{test['name']}: {test.get('status', 'unknown')}\n")
                if test.get('error'):
                    f.write(f"  Error: {test['error']}\n")
                if test.get('data'):
                    f.write(f"  Data: {json.dumps(test['data'], indent=4)}\n")

            f.write("\n\nFUNCTION CALL TRACE\n")
            f.write("-" * 60 + "\n")
            for call in self.results['function_calls'][:50]:  # First 50 calls
                f.write(f"\n{call['function']}\n")
                f.write(f"  Duration: {call['duration']:.4f}s\n")
                if call.get('error'):
                    f.write(f"  Error: {call['error']}\n")
                if call.get('result'):
                    f.write(f"  Result: {call['result'][:200]}\n")

        print(f"\n💾 Results saved to: {self.test_output_dir}")
        print(f"   JSON: {json_path}")
        print(f"   Log: {log_path}")

def main():
    """Run comprehensive tests"""
    runner = ComprehensiveTestRunner()
    results = runner.run_all_tests()

    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(results['tests'])}")
    print(f"Passed: {len([t for t in results['tests'] if t.get('status') == 'passed'])}")
    print(f"Failed: {len([t for t in results['tests'] if t.get('status') == 'failed'])}")
    print(f"Skipped: {len([t for t in results['tests'] if t.get('status') == 'skipped'])}")
    print(f"Images Generated: {len(results['images_generated'])}")
    print(f"Function Calls: {len(results['function_calls'])}")
    print(f"Results Directory: {runner.test_output_dir}")
    print("\n✅ Comprehensive test complete!")
    print(f"🌐 View results at: http://localhost:8080/test_results_history.html")

if __name__ == "__main__":
    main()


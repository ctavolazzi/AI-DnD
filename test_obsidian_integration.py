#!/usr/bin/env python3
"""
Test script for Obsidian Vault Integration

This script tests the bidirectional sync functionality between the D&D game
and Obsidian vault. It creates sample characters, syncs them to the vault,
reads them back, and verifies the data integrity.

Usage:
    python3 test_obsidian_integration.py
"""

import os
import sys
import tempfile
import shutil
import logging
from typing import Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from obsidian_logger import ObsidianLogger
from dnd_game import Character

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_obsidian_integration")

class ObsidianIntegrationTester:
    """
    Test suite for Obsidian vault integration.
    """

    def __init__(self):
        """Initialize the tester with a temporary vault."""
        self.temp_vault = tempfile.mkdtemp(prefix="obsidian_test_")
        self.obsidian_logger = ObsidianLogger(self.temp_vault)
        self.test_results = []

        logger.info(f"Created temporary vault at: {self.temp_vault}")

    def cleanup(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_vault):
            shutil.rmtree(self.temp_vault)
            logger.info(f"Cleaned up temporary vault: {self.temp_vault}")

    def run_test(self, test_name: str, test_func) -> bool:
        """
        Run a single test and record the result.

        Args:
            test_name: Name of the test
            test_func: Function to run for the test

        Returns:
            True if test passed, False otherwise
        """
        logger.info(f"Running test: {test_name}")

        try:
            result = test_func()
            if result:
                logger.info(f"✅ PASSED: {test_name}")
                self.test_results.append((test_name, True, "Passed"))
            else:
                logger.error(f"❌ FAILED: {test_name}")
                self.test_results.append((test_name, False, "Failed"))
            return result
        except Exception as e:
            logger.error(f"❌ ERROR in {test_name}: {e}")
            self.test_results.append((test_name, False, f"Error: {e}"))
            return False

    def test_vault_creation(self) -> bool:
        """Test that vault directories are created properly."""
        # Check that all required directories exist
        required_dirs = ["Characters", "Locations", "Events", "Sessions", "Quests", "Items", "Journals"]

        for dir_name in required_dirs:
            dir_path = os.path.join(self.temp_vault, dir_name)
            if not os.path.exists(dir_path):
                logger.error(f"Directory not created: {dir_path}")
                return False

        # Check that index file exists
        index_path = os.path.join(self.temp_vault, "Index.md")
        if not os.path.exists(index_path):
            logger.error(f"Index file not created: {index_path}")
            return False

        return True

    def test_character_logging(self) -> bool:
        """Test logging a character to the vault."""
        character_data = {
            "name": "Test Hero",
            "char_class": "Fighter",
            "hp": 20,
            "max_hp": 20,
            "attack": 5,
            "defense": 3,
            "alive": True,
            "status": "Active",
            "status_summary": "Active - HP: 20/20",
            "bio": "A brave test character for integration testing."
        }

        # Log the character
        self.obsidian_logger.log_character(character_data)

        # Check that the file was created
        char_file = os.path.join(self.temp_vault, "Characters", "Test Hero.md")
        if not os.path.exists(char_file):
            logger.error(f"Character file not created: {char_file}")
            return False

        # Check that the file contains expected content
        with open(char_file, 'r') as f:
            content = f.read()

        if "Test Hero" not in content:
            logger.error("Character name not found in file content")
            return False

        if "Fighter" not in content:
            logger.error("Character class not found in file content")
            return False

        return True

    def test_character_reading(self) -> bool:
        """Test reading a character from the vault."""
        # First, create a character
        character_data = {
            "name": "Test Reader",
            "char_class": "Wizard",
            "hp": 15,
            "max_hp": 15,
            "attack": 3,
            "defense": 2,
            "alive": True,
            "status": "Active",
            "status_summary": "Active - HP: 15/15",
            "bio": "A test character for reading tests."
        }

        self.obsidian_logger.log_character(character_data)

        # Now read it back
        read_data = self.obsidian_logger.read_character_from_vault("Test Reader")

        if not read_data:
            logger.error("Failed to read character from vault")
            return False

        # Verify the data matches
        if read_data.get("name") != "Test Reader":
            logger.error(f"Name mismatch: expected 'Test Reader', got '{read_data.get('name')}'")
            return False

        if read_data.get("char_class") != "Wizard":
            logger.error(f"Class mismatch: expected 'Wizard', got '{read_data.get('char_class')}'")
            return False

        return True

    def test_bidirectional_sync(self) -> bool:
        """Test bidirectional sync between game and vault."""
        # Create a game character
        game_char = Character(
            name="Sync Test",
            char_class="Rogue",
            hp=18,
            max_hp=18,
            attack=4,
            defense=2
        )

        # Sync to vault
        if not self.obsidian_logger.sync_game_to_vault(game_char):
            logger.error("Failed to sync game character to vault")
            return False

        # Read from vault
        vault_data = self.obsidian_logger.read_character_from_vault("Sync Test")
        if not vault_data:
            logger.error("Failed to read character from vault after sync")
            return False

        # Verify data matches
        if vault_data.get("hp") != game_char.hp:
            logger.error(f"HP mismatch: expected {game_char.hp}, got {vault_data.get('hp')}")
            return False

        if vault_data.get("char_class") != game_char.char_class:
            logger.error(f"Class mismatch: expected {game_char.char_class}, got {vault_data.get('char_class')}")
            return False

        # Test sync from vault to game
        # First, update the character in the vault with new HP
        updated_char_data = vault_data.copy()
        updated_char_data["hp"] = 10
        updated_char_data["max_hp"] = 15
        updated_char_data["status_summary"] = f"Active - HP: 10/15"

        # Update the character in the vault
        self.obsidian_logger.update_character_status("Sync Test", updated_char_data)

        # Create a new game character and sync from vault
        new_game_char = Character(
            name="Sync Test",
            char_class="Rogue",
            hp=20,  # Different initial values
            max_hp=20,
            attack=5,
            defense=3
        )

        # Sync from vault to game
        if not self.obsidian_logger.sync_character_to_game("Sync Test", new_game_char):
            logger.error("Failed to sync character from vault to game")
            return False

        # Verify the game character was updated
        if new_game_char.hp != 10:
            logger.error(f"Game character HP not updated: expected 10, got {new_game_char.hp}")
            return False

        if new_game_char.max_hp != 15:
            logger.error(f"Game character max HP not updated: expected 15, got {new_game_char.max_hp}")
            return False

        return True

    def test_vault_status(self) -> bool:
        """Test vault status functionality."""
        # Add some test data
        test_characters = [
            {"name": "Status Test 1", "char_class": "Fighter", "hp": 20, "max_hp": 20, "attack": 5, "defense": 3, "alive": True},
            {"name": "Status Test 2", "char_class": "Wizard", "hp": 15, "max_hp": 15, "attack": 3, "defense": 2, "alive": True}
        ]

        for char_data in test_characters:
            self.obsidian_logger.log_character(char_data)

        # Get vault status
        status = self.obsidian_logger.get_vault_status()

        # Verify status data
        if status.get("characters") < 2:  # Should be at least 2, but might include reference files
            logger.error(f"Character count too low: expected at least 2, got {status.get('characters')}")
            return False

        if status.get("total_files") < 2:
            logger.error(f"Total files too low: expected at least 2, got {status.get('total_files')}")
            return False

        if not status.get("vault_path"):
            logger.error("Vault path not set in status")
            return False

        return True

    def test_quest_logging(self) -> bool:
        """Test quest logging functionality."""
        quest_data = {
            "name": "Test Quest",
            "description": "A test quest for integration testing",
            "difficulty": "Easy",
            "status": "Active",
            "objectives": [
                {"description": "Find the test item", "completed": False},
                {"description": "Defeat the test monster", "completed": True}
            ]
        }

        # Log the quest
        self.obsidian_logger.log_quest(quest_data)

        # Check that the file was created
        quest_file = os.path.join(self.temp_vault, "Quests", "Test Quest.md")
        if not os.path.exists(quest_file):
            logger.error(f"Quest file not created: {quest_file}")
            return False

        # Read the quest back
        read_quest = self.obsidian_logger.read_quest_from_vault("Test Quest")
        if not read_quest:
            logger.error("Failed to read quest from vault")
            return False

        # Verify objectives
        if len(read_quest.get("objectives", [])) != 2:
            logger.error(f"Objective count mismatch: expected 2, got {len(read_quest.get('objectives', []))}")
            return False

        return True

    def run_all_tests(self) -> bool:
        """Run all tests and return overall success."""
        logger.info("Starting Obsidian Integration Test Suite")
        logger.info("=" * 50)

        tests = [
            ("Vault Creation", self.test_vault_creation),
            ("Character Logging", self.test_character_logging),
            ("Character Reading", self.test_character_reading),
            ("Bidirectional Sync", self.test_bidirectional_sync),
            ("Vault Status", self.test_vault_status),
            ("Quest Logging", self.test_quest_logging)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1

        logger.info("=" * 50)
        logger.info(f"Test Results: {passed}/{total} tests passed")

        if passed == total:
            logger.info("🎉 All tests passed! Obsidian integration is working correctly.")
        else:
            logger.error(f"❌ {total - passed} tests failed. Check the logs above for details.")

        return passed == total

    def print_summary(self):
        """Print a summary of test results."""
        print("\n" + "=" * 60)
        print("OBSIDIAN INTEGRATION TEST SUMMARY")
        print("=" * 60)

        for test_name, passed, message in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}: {message}")

        passed_count = sum(1 for _, passed, _ in self.test_results if passed)
        total_count = len(self.test_results)

        print(f"\nOverall: {passed_count}/{total_count} tests passed")

        if passed_count == total_count:
            print("🎉 All tests passed! Your Obsidian integration is ready to use.")
        else:
            print("❌ Some tests failed. Please check the logs for details.")

        print("=" * 60)

def main():
    """Main entry point for the test script."""
    tester = ObsidianIntegrationTester()

    try:
        success = tester.run_all_tests()
        tester.print_summary()

        if success:
            print("\n🚀 Next steps:")
            print("1. Run: python3 obsidian_sync.py --status")
            print("2. Run: python3 obsidian_sync.py --interactive")
            print("3. Open: obsidian_vault_dashboard.html in your browser")
            print("4. Start your D&D game and watch it sync to Obsidian!")

        return 0 if success else 1

    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())

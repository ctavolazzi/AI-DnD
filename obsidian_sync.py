#!/usr/bin/env python3
"""
Obsidian Sync Tool for AI-DnD System

This script provides easy bidirectional synchronization between your D&D game
and Obsidian vault. It allows you to:
- Sync character data from game to vault
- Sync character data from vault to game
- Monitor vault status
- Perform bulk sync operations

Usage:
    python3 obsidian_sync.py --help
    python3 obsidian_sync.py --status
    python3 obsidian_sync.py --sync-to-vault --character "Thorin"
    python3 obsidian_sync.py --sync-from-vault --character "Thorin"
    python3 obsidian_sync.py --sync-all
"""

import argparse
import logging
import sys
import os
from typing import Dict, List, Optional, Any

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from obsidian_logger import ObsidianLogger
from dnd_game import Character

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("obsidian_sync")

class ObsidianSyncTool:
    """
    Tool for synchronizing D&D game data with Obsidian vault.
    """

    def __init__(self, vault_path: str = "ai-dnd-test-vault"):
        """
        Initialize the sync tool.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = vault_path
        self.obsidian_logger = ObsidianLogger(vault_path)
        self.logger = logging.getLogger("obsidian_sync")

    def get_vault_status(self) -> Dict[str, Any]:
        """
        Get comprehensive vault status.

        Returns:
            Dictionary with vault statistics
        """
        status = self.obsidian_logger.get_vault_status()

        # Add additional information
        status["vault_exists"] = os.path.exists(self.vault_path)
        status["vault_writable"] = os.access(self.vault_path, os.W_OK) if status["vault_exists"] else False

        return status

    def print_vault_status(self):
        """Print formatted vault status."""
        status = self.get_vault_status()

        print("\n" + "="*60)
        print("📚 OBSIDIAN VAULT STATUS")
        print("="*60)
        print(f"Vault Path: {status['vault_path']}")
        print(f"Vault Exists: {'✅ Yes' if status['vault_exists'] else '❌ No'}")
        print(f"Vault Writable: {'✅ Yes' if status['vault_writable'] else '❌ No'}")
        print(f"Last Updated: {status['last_updated'] or 'Never'}")
        print(f"Total Files: {status['total_files']}")
        print("\n📊 File Counts:")
        print(f"  Characters: {status['characters']}")
        print(f"  Locations: {status['locations']}")
        print(f"  Events: {status['events']}")
        print(f"  Quests: {status['quests']}")
        print(f"  Items: {status['items']}")
        print(f"  Sessions: {status['sessions']}")
        print(f"  Journals: {status['journals']}")
        print("="*60)

    def list_characters_in_vault(self) -> List[str]:
        """
        List all characters found in the vault.

        Returns:
            List of character names
        """
        characters_dir = os.path.join(self.vault_path, "Characters")
        if not os.path.exists(characters_dir):
            return []

        characters = []
        for file in os.listdir(characters_dir):
            if file.endswith('.md') and file != 'Characters.md':
                # Remove .md extension and convert back to original name
                character_name = file[:-3]
                characters.append(character_name)

        return sorted(characters)

    def print_characters_in_vault(self):
        """Print formatted list of characters in vault."""
        characters = self.list_characters_in_vault()

        print("\n" + "="*60)
        print("👥 CHARACTERS IN VAULT")
        print("="*60)

        if not characters:
            print("No characters found in vault.")
        else:
            for i, char in enumerate(characters, 1):
                print(f"{i:2d}. {char}")

        print("="*60)

    def sync_character_to_vault(self, character_name: str, game_character: Optional[Character] = None) -> bool:
        """
        Sync a character from game to vault.

        Args:
            character_name: Name of the character to sync
            game_character: Game character object (if None, will try to find it)

        Returns:
            True if sync was successful
        """
        if game_character is None:
            # Try to find the character in a running game
            # This is a simplified approach - in practice you'd want to load from save file
            self.logger.warning(f"No game character provided for {character_name}")
            return False

        try:
            success = self.obsidian_logger.sync_game_to_vault(game_character)
            if success:
                print(f"✅ Successfully synced {character_name} to vault")
            else:
                print(f"❌ Failed to sync {character_name} to vault")
            return success
        except Exception as e:
            self.logger.error(f"Error syncing {character_name} to vault: {e}")
            print(f"❌ Error syncing {character_name} to vault: {e}")
            return False

    def sync_character_from_vault(self, character_name: str) -> Optional[Dict[str, Any]]:
        """
        Read character data from vault.

        Args:
            character_name: Name of the character to read

        Returns:
            Character data dictionary, or None if not found
        """
        try:
            character_data = self.obsidian_logger.read_character_from_vault(character_name)
            if character_data:
                print(f"✅ Successfully read {character_name} from vault")
                print(f"   HP: {character_data.get('hp', 'N/A')}/{character_data.get('max_hp', 'N/A')}")
                print(f"   Status: {character_data.get('status', 'N/A')}")
            else:
                print(f"❌ Character {character_name} not found in vault")
            return character_data
        except Exception as e:
            self.logger.error(f"Error reading {character_name} from vault: {e}")
            print(f"❌ Error reading {character_name} from vault: {e}")
            return None

    def create_sample_character(self, name: str = "Sample Hero") -> Character:
        """
        Create a sample character for testing purposes.

        Args:
            name: Name of the character

        Returns:
            Character object
        """
        return Character(
            name=name,
            char_class="Fighter",
            hp=20,
            max_hp=20,
            attack=5,
            defense=3,
            alive=True
        )

    def sync_all_characters_to_vault(self):
        """
        Sync all characters from a sample game to vault.
        This is a demo function - in practice you'd load from your actual game state.
        """
        print("\n🔄 Syncing all characters to vault...")

        # Create some sample characters
        sample_characters = [
            self.create_sample_character("Thorin Ironbeard"),
            self.create_sample_character("Luna Starshine"),
            self.create_sample_character("Grimlock the Bold")
        ]

        success_count = 0
        for char in sample_characters:
            if self.sync_character_to_vault(char.name, char):
                success_count += 1

        print(f"\n📊 Sync Results: {success_count}/{len(sample_characters)} characters synced successfully")

    def interactive_sync(self):
        """
        Interactive sync mode for user-friendly operation.
        """
        print("\n" + "="*60)
        print("🎮 INTERACTIVE OBSIDIAN SYNC")
        print("="*60)

        while True:
            print("\nOptions:")
            print("1. Show vault status")
            print("2. List characters in vault")
            print("3. Sync character from vault")
            print("4. Sync character to vault")
            print("5. Sync all sample characters")
            print("6. Exit")

            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self.print_vault_status()
            elif choice == "2":
                self.print_characters_in_vault()
            elif choice == "3":
                characters = self.list_characters_in_vault()
                if not characters:
                    print("No characters found in vault.")
                    continue

                print("\nAvailable characters:")
                for i, char in enumerate(characters, 1):
                    print(f"{i}. {char}")

                try:
                    char_choice = int(input("Select character number: ")) - 1
                    if 0 <= char_choice < len(characters):
                        self.sync_character_from_vault(characters[char_choice])
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a valid number.")
            elif choice == "4":
                name = input("Enter character name: ").strip()
                if name:
                    # Create a sample character for demo
                    sample_char = self.create_sample_character(name)
                    self.sync_character_to_vault(name, sample_char)
            elif choice == "5":
                self.sync_all_characters_to_vault()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-6.")

def main():
    """Main entry point for the sync tool."""
    parser = argparse.ArgumentParser(
        description="Obsidian Sync Tool for AI-DnD System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 obsidian_sync.py --status
  python3 obsidian_sync.py --list-characters
  python3 obsidian_sync.py --sync-to-vault --character "Thorin"
  python3 obsidian_sync.py --sync-from-vault --character "Thorin"
  python3 obsidian_sync.py --sync-all
  python3 obsidian_sync.py --interactive
        """
    )

    parser.add_argument(
        "--vault-path",
        default="ai-dnd-test-vault",
        help="Path to Obsidian vault (default: ai-dnd-test-vault)"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Show vault status"
    )

    parser.add_argument(
        "--list-characters",
        action="store_true",
        help="List all characters in vault"
    )

    parser.add_argument(
        "--sync-to-vault",
        action="store_true",
        help="Sync character from game to vault"
    )

    parser.add_argument(
        "--sync-from-vault",
        action="store_true",
        help="Sync character from vault to game"
    )

    parser.add_argument(
        "--character",
        help="Character name for sync operations"
    )

    parser.add_argument(
        "--sync-all",
        action="store_true",
        help="Sync all sample characters to vault"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )

    args = parser.parse_args()

    # Initialize sync tool
    sync_tool = ObsidianSyncTool(args.vault_path)

    # Execute requested operations
    if args.status:
        sync_tool.print_vault_status()

    if args.list_characters:
        sync_tool.print_characters_in_vault()

    if args.sync_to_vault:
        if not args.character:
            print("❌ Error: --character required for sync-to-vault")
            sys.exit(1)

        # Create sample character for demo
        sample_char = sync_tool.create_sample_character(args.character)
        sync_tool.sync_character_to_vault(args.character, sample_char)

    if args.sync_from_vault:
        if not args.character:
            print("❌ Error: --character required for sync-from-vault")
            sys.exit(1)

        sync_tool.sync_character_from_vault(args.character)

    if args.sync_all:
        sync_tool.sync_all_characters_to_vault()

    if args.interactive:
        sync_tool.interactive_sync()

    # If no specific action was requested, show help
    if not any([args.status, args.list_characters, args.sync_to_vault,
                args.sync_from_vault, args.sync_all, args.interactive]):
        parser.print_help()

if __name__ == "__main__":
    main()

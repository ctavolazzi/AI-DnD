#!/usr/bin/env python3
"""
AI D&D Game Runner

This module serves as the main entry point for the AI-driven Dungeons & Dragons game.
It handles command-line arguments, initializes the game environment, and manages the overall
execution flow. The module coordinates between the Dungeon Master, the game world,
and the error logging systems.

Usage:
    python3 main.py [--vault VAULT_PATH] [--reset] [--turns N] [--model MODEL_NAME] [--force-error] [--no-run] [--verbose]

Examples:
    python3 main.py --vault=character-journal-test-vault --turns=5 --model=mistral
    python3 main.py --reset --turns=10
    python3 main.py --reset --no-run
"""
import os
import argparse
import logging
import shutil
import sys

from dungeon_master import DungeonMaster
from error_logger import log_exception, log_error
from backend.app.core.providers import RealTimeProvider, FileLogProvider


def main():
    """
    Main entry point for the AI-DnD game application.

    This function:
    1. Parses command line arguments
    2. Sets up logging
    3. Initializes the game environment and vault
    4. Creates and runs a Dungeon Master instance
    5. Handles any errors that occur during execution

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run AI D&D game')
    parser.add_argument('--vault', type=str, default='character-journal-test-vault',
                      help='Path to Obsidian vault')
    parser.add_argument('--reset', action='store_true',
                      help='Reset the vault before running')
    parser.add_argument('--turns', type=int, default=5,
                      help='Number of turns to run')
    parser.add_argument('--model', type=str, default='mistral',
                      help='Model to use for generation (mistral, ollama, etc.)')
    parser.add_argument('--force-error', action='store_true',
                      help='Force an error to test error logging')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    parser.add_argument('--no-run', action='store_true',
                      help='Reset the vault without running the game')
    args = parser.parse_args()

    # Set up basic logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print(f"\n{'='*60}")
    print(f"AI D&D Game Runner Starting...")
    print(f"{'='*60}\n")

    logging.info("AI D&D Game Runner initialized")
    if args.verbose:
        logging.debug(f"Command line arguments: {vars(args)}")

    try:
        # Artificial error for demonstration if --force-error is specified
        if args.force_error:
            print("⚠️  Forcing an error for demonstration purposes...")
            logging.info("Forcing an error for demonstration purposes...")
            # This will cause an AttributeError
            nonexistent_object = None
            nonexistent_object.some_method()

        # Create vault directory if it doesn't exist
        os.makedirs(args.vault, exist_ok=True)

        # Reset vault if requested
        if args.reset:
            print(f"🔄 Resetting vault at {args.vault}...")
            logging.info(f"Resetting vault at {args.vault}...")
            try:
                # Clear directory except for .gitignore and .obsidian
                for item in os.listdir(args.vault):
                    if item not in ['.gitignore', '.obsidian']:
                        item_path = os.path.join(args.vault, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                logging.info("Vault reset complete.")
                print("✅ Vault reset complete.")
            except Exception as e:
                log_exception(e, {"context": "Vault reset", "vault_path": args.vault})
                logging.error(f"Failed to reset vault: {e}")
                print(f"❌ Failed to reset vault: {e}")

        # Check if vault exists
        if not os.path.isdir(args.vault):
            error_msg = f"Vault not found at {args.vault}. Run with --reset to create it."
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            return 1

        print(f"📂 Using vault at {args.vault}")
        print(f"🎲 Running for {args.turns} turns with model '{args.model}'")
        logging.info(f"Using vault at {args.vault}")
        logging.info(f"Running for {args.turns} turns with model {args.model}")

        # Skip game execution if --no-run flag is set
        if args.no_run:
            print("🛑 Skipping game execution due to --no-run flag")
            logging.info("Skipping game execution due to --no-run flag")
            return 0

        print(f"🧙 Initializing Dungeon Master with model '{args.model}'...")
        logging.info(f"Initializing Dungeon Master with model {args.model}...")

        # Inject Providers for CLI
        time_provider = RealTimeProvider()
        log_provider = FileLogProvider()

        dm = DungeonMaster(
            vault_path=args.vault,
            model=args.model,
            time_provider=time_provider,
            log_provider=log_provider
        )

        print(f"\n📜 Running game for {args.turns} turns...\n")
        logging.info(f"Running game for {args.turns} turns...")
        success = dm.run_game(max_turns=args.turns)

        if success:
            print("\n✅ Game completed successfully!")
            logging.info("Game completed successfully!")
            return 0
        else:
            print("\n⚠️ Game completed with errors. Check logs for details.")
            logging.warning("Game completed with errors.")
            return 1

    except KeyboardInterrupt:
        print("\n\n⛔ Game interrupted by user. Exiting...")
        logging.info("Game interrupted by user")
        return 1
    except Exception as e:
        error_details = log_exception(e, {"context": "Main game execution", "args": vars(args)})
        logging.error(f"Critical error: {e}")

        print(f"\n❌ Critical error: {e}")
        print(f"🔍 Error occurred in {error_details.get('file', 'unknown')}, line {error_details.get('line', 'unknown')}")
        print("   Check logs/ai_dnd_errors_*.log for detailed information")
        return 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\n{'='*60}")
    print(f"AI D&D Game Runner Exiting with code {exit_code}")
    print(f"{'='*60}\n")
    sys.exit(exit_code)

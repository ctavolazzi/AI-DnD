#!/usr/bin/env python3
import argparse
import logging
import sys
import os
from dungeon_master import DungeonMaster

def setup_logging(debug=False):
    """Set up logging for the application."""
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("ai_dnd.log", mode='w')
        ]
    )

def main():
    """Main entry point for the AI-DnD application."""
    parser = argparse.ArgumentParser(description='AI-DnD: AI-driven Dungeons & Dragons game')
    parser.add_argument('--reset', action='store_true', help='Reset the game vault before starting')
    parser.add_argument('--no-run', action='store_true', help='Do not run the game (useful with --reset)')
    parser.add_argument('--turns', type=int, default=10, help='Number of turns to run (default: 10)')
    parser.add_argument('--model', type=str, default='mistral', help='LLM model to use (default: mistral)')
    parser.add_argument('--vault', type=str, default='ai-dnd-test-vault', help='Path to Obsidian vault')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.debug)

    # Reset the vault if requested
    if args.reset:
        try:
            logging.info("Resetting vault...")
            from reset_game import reset_vault

            # Only create the Current-Run.md file if we're actually running the game
            create_current_run = not args.no_run
            result = reset_vault(create_current_run=create_current_run)

            # Log the result
            if isinstance(result, str):
                logging.info(f"Vault reset complete. New run ID: {result}")
            else:
                logging.info("Vault reset complete. No run_id created.")
        except Exception as e:
            logging.error(f"Failed to reset vault: {e}", exc_info=True)
            return 1

    # Exit if --no-run was specified
    if args.no_run:
        logging.info("--no-run specified. Exiting without running the game.")
        return 0

    # Check if vault exists
    if not os.path.exists(args.vault):
        logging.error(f"Vault not found at {args.vault}. Run with --reset to create it.")
        return 1

    # Initialize and run the Dungeon Master
    try:
        logging.info(f"Initializing Dungeon Master with model {args.model}...")
        dm = DungeonMaster(vault_path=args.vault, model=args.model)

        logging.info(f"Running game for {args.turns} turns...")
        success = dm.run_game(max_turns=args.turns)

        if success:
            logging.info("Game completed successfully!")
            return 0
        else:
            logging.warning("Game completed with errors.")
            return 1

    except Exception as e:
        logging.error(f"Critical error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
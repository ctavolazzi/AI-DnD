#!/usr/bin/env python3
import time
import logging
from dnd_game import DnDGame, GameError
from log_aggregator import LogAggregator

def setup_logging():
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with a simple format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create and configure the LogAggregator
    aggregator = LogAggregator()
    aggregator.setLevel(logging.INFO)
    aggregator.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(aggregator)

    return aggregator

def self_playing_game_with_narrative():
    # Set up logging and get aggregator
    aggregator = setup_logging()

    # Initialize game
    print("Initializing self-playing game with integrated narrative...")
    game = DnDGame(model="mistral")

    # Start with just ONE turn to test the integration
    print("\nExecuting first turn...")

    # Clear the aggregator
    aggregator.clear()

    # Describe initial scene
    alive_characters = [char.name for char in game.players + game.enemies if char.alive]
    scene_description = game.narrative_engine.describe_scene("Starting Tavern", alive_characters)
    print("\nScene Description:")
    print(scene_description)

    # Execute one combat turn
    game.play_turn()

    # Get and display the combat log
    combat_log = aggregator.get_logs()
    print("\nCombat Log:")
    print(combat_log)

    # Generate and display narrative summary
    summary = game.narrative_engine.summarize_combat(combat_log)
    print("\nTurn Summary:")
    print(summary)

if __name__ == "__main__":
    try:
        self_playing_game_with_narrative()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except GameError as ge:
        print(f"\nGame error: {ge}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise
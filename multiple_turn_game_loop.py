#!/usr/bin/env python3
import time
import logging
from dnd_game import DnDGame, GameError
from log_aggregator import LogAggregator

def multiple_turn_game_loop():
    # Obtain the root logger and clear existing handlers to avoid duplicates
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    # Set up a console handler for real-time output
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Create and configure the LogAggregator for combat events
    aggregator = LogAggregator()
    aggregator.setLevel(logging.INFO)
    aggregator.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(aggregator)

    # Disable propagation on module-specific loggers
    dnd_logger = logging.getLogger("dnd_game")
    dnd_logger.propagate = False

    logging.info("Initializing multiple-turn self-playing game...")
    game = DnDGame(model="mistral")

    # Generate an initial quest narrative
    quest_intro = game.narrative_engine.generate_quest(difficulty="medium", theme="epic battle")
    logging.info("Quest: " + quest_intro)

    turn_count = 0
    max_turns = 10  # Set a limit for demonstration purposes

    while not game.is_game_over() and turn_count < max_turns:
        # Clear previous logs so only current turn events are captured
        aggregator.clear()

        # Generate and log a scene description based on current location and alive characters
        alive_characters = [char.name for char in game.players + game.enemies if char.alive]
        scene_desc = game.narrative_engine.describe_scene(game.current_location, alive_characters)
        logging.info("Scene: " + scene_desc)

        # Every 3 turns, add a random encounter narrative to spice things up
        if turn_count % 3 == 0:
            encounter = game.narrative_engine.generate_random_encounter(party_level=1, environment=game.current_location)
            logging.info("Encounter: " + encounter)

        # Execute one combat turn, which logs combat actions internally
        game.play_turn()

        # Retrieve the combat log for this turn from the aggregator
        combat_log = aggregator.get_logs()
        logging.info("Combat Log for Turn {}:\n{}".format(turn_count + 1, combat_log))

        # Generate a narrative summary using the combat log
        turn_summary = game.narrative_engine.summarize_combat(combat_log)
        logging.info("Turn Summary: " + turn_summary)

        turn_count += 1
        time.sleep(1)  # Brief pause between turns for pacing

    # Generate a final narrative based on the outcome of the battle
    if any(player.alive for player in game.players):
        conclusion = game.narrative_engine.handle_player_action("The party", "emerges victorious",
            "The battle ends with heroic triumph!")
        logging.info("Conclusion: " + conclusion)
    else:
        conclusion = game.narrative_engine.handle_player_action("The party", "has fallen",
            "Darkness claims the battlefield as all heroes are defeated.")
        logging.info("Conclusion: " + conclusion)

if __name__ == "__main__":
    try:
        multiple_turn_game_loop()
    except KeyboardInterrupt:
        logging.info("Game interrupted by user.")
    except GameError as ge:
        logging.error("Game error: " + str(ge))
    except Exception as e:
        logging.exception("Unexpected error: " + str(e))
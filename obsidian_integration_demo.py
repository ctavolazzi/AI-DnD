#!/usr/bin/env python3
import time
import logging
import sys
import os
import datetime
import re
from dnd_game import DnDGame, GameError, Character
from log_aggregator import LogAggregator
from obsidian_logger import ObsidianLogger

def setup_logging():
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    logger.handlers.clear()

    # Set up console handler for real-time output
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Set up log aggregator for combat events
    aggregator = LogAggregator()
    aggregator.setLevel(logging.INFO)
    aggregator.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(aggregator)

    # Configure game logger
    dnd_logger = logging.getLogger("dnd_game")
    dnd_logger.propagate = False

    return aggregator

def extract_run_id():
    """Extract run ID from Current Run.md."""
    current_run_path = os.path.join("ai-dnd-test-vault", "Current Run.md")
    if not os.path.exists(current_run_path):
        return None

    try:
        with open(current_run_path, 'r') as f:
            content = f.read()
            match = re.search(r"run_id: ([^\n]+)", content)
            if match:
                return match.group(1)
    except Exception as e:
        logging.warning(f"Error extracting run ID: {e}")

    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def update_current_run(obsidian, run_data):
    """Update the Current Run.md file with the latest game state."""
    run_id = extract_run_id()
    if not run_id:
        run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Build content with YAML frontmatter
    content = f"""---
run_id: {run_id}
timestamp: {run_data.get('start_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
status: {run_data.get('status', 'active')}
turn_count: {run_data.get('turn_count', 0)}
---

# Current Game Run: {run_id}

Started: {run_data.get('start_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
Last Updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Current Turn: {run_data.get('turn_count', 0)}

## Active Quest
"""

    # Add quest information
    if 'quest' in run_data and run_data['quest']:
        content += f"[[{run_data['quest']}]]\n\n"
    else:
        content += "No quests started yet.\n\n"

    # Add character information
    content += "## Characters\n\n"
    if 'characters' in run_data and run_data['characters']:
        for character in run_data['characters']:
            content += f"- [[{character}]]\n"
    else:
        content += "No characters created yet.\n\n"

    # Add events information
    content += "## Events\n\n"
    if 'events' in run_data and run_data['events']:
        # Show last 5 events
        for event in run_data['events'][-5:]:
            if isinstance(event, dict):
                event_name = event.get('name', 'Unknown Event')
                content += f"- [[{event_name}]]\n"
            else:
                content += f"- [[{event}]]\n"
    else:
        content += "No events have occurred yet.\n\n"

    # Add combat information
    content += "## Combat\n\n"
    if 'combat' in run_data and run_data['combat']:
        # Show last 3 combats
        for combat in run_data['combat'][-3:]:
            if isinstance(combat, dict):
                combat_name = combat.get('name', 'Unknown Combat')
                content += f"- [[{combat_name}]]\n"
            else:
                content += f"- [[{combat}]]\n"
    else:
        content += "No combat has occurred yet.\n\n"

    # Add sessions information
    content += "## Sessions\n\n"
    if 'session' in run_data and run_data['session']:
        content += f"- [[{run_data['session']}]]\n\n"
    else:
        content += "No sessions recorded yet.\n\n"

    # Add conclusion if available
    if 'conclusion' in run_data and run_data['conclusion']:
        content += f"## Conclusion\n\n{run_data['conclusion']}\n\n"

    # Add footer
    content += "*This run is currently in progress. Content will be updated as the game progresses.*\n"

    # Write the updated file
    current_run_path = os.path.join(obsidian.vault_path, "Current Run.md")
    with open(current_run_path, 'w') as f:
        f.write(content)

    logging.info(f"Updated Current Run.md (Run ID: {run_id}, Turn: {run_data.get('turn_count', 0)})")

def main():
    # Set up logging
    aggregator = setup_logging()

    # Initialize Obsidian logger
    obsidian = ObsidianLogger("ai-dnd-test-vault")
    logging.info("Initialized Obsidian logger for the game.")

    # Extract run ID from Current Run.md
    run_id = extract_run_id()
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Initialize run data
    run_data = {
        "run_id": run_id,
        "start_time": start_time,
        "status": "active",
        "turn_count": 0,
        "characters": [],
        "events": [],
        "combat": [],
        "locations": []
    }

    # Create or update the Start.md file to ensure it exists
    if not os.path.exists("ai-dnd-test-vault/Start.md"):
        # We'll assume the Start.md file has already been created with the proper structure
        logging.info("Start.md file already exists.")

    # Initialize game
    logging.info("\nInitializing D&D Game...")
    game = DnDGame(model="mistral")

    # Log initial world locations to Obsidian
    if hasattr(game, 'current_location'):
        location_data = {
            "name": game.current_location,
            "description": f"The starting location of the adventure.",
            "connections": {}  # Will be populated as game progresses
        }
        obsidian.log_location(location_data)
        logging.info(f"Logged starting location: {game.current_location}")
        run_data["locations"].append(game.current_location)

    # Log player characters to Obsidian
    for player in game.players:
        character_data = {
            "name": player.name,
            "char_class": player.char_class,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "attack": player.attack,
            "defense": player.defense,
            "alive": player.alive,
            "abilities": list(player.abilities.keys()) if hasattr(player, 'abilities') else [],
            "status_effects": player.status_effects if hasattr(player, 'status_effects') else [],
            "team": "Player"
        }
        obsidian.log_character(character_data)
        logging.info(f"Logged player character: {player.name}")
        run_data["characters"].append(player.name)

    # Generate initial quest
    quest_intro = game.narrative_engine.generate_quest(difficulty="medium", theme="epic battle")
    logging.info("\nQuest: " + quest_intro)

    # Log the quest to Obsidian
    quest_data = {
        "name": "Main Quest",
        "description": quest_intro,
        "status": "Active",
        "difficulty": "Medium",
        "objectives": ["Complete the adventure"]
    }
    obsidian.log_quest(quest_data)
    print(f"Quest logged to Obsidian: {quest_data['name']}")
    run_data["quest"] = "Main Quest"

    # Create session data
    session_name = f"Session {time.strftime('%Y%m%d')}"
    session_data = {
        "name": session_name,
        "summary": f"The party embarks on a new adventure: {quest_intro}",
        "characters": [player.name for player in game.players],
        "events": [],
        "combat": []
    }
    run_data["session"] = session_name

    if hasattr(game, 'current_location'):
        session_data["locations"] = [game.current_location]

    # Update Current Run.md with initial state
    update_current_run(obsidian, run_data)

    turn_count = 0
    max_turns = 10

    try:
        while not game.is_game_over() and turn_count < max_turns:
            # Clear previous turn's logs
            aggregator.clear()

            # Describe current scene
            alive_characters = [char.name for char in game.players + game.enemies if char.alive]
            scene_desc = game.narrative_engine.describe_scene(game.current_location, alive_characters)
            logging.info("\nScene: " + scene_desc)

            # Update run data with turn count
            turn_count += 1
            run_data["turn_count"] = turn_count

            # Random encounter every 3 turns
            if turn_count % 3 == 0 and turn_count > 0:
                encounter = game.narrative_engine.generate_random_encounter(party_level=1, environment=game.current_location)
                logging.info("\nEncounter: " + encounter)

                # Log encounter as event in Obsidian
                event_data = {
                    "name": f"Encounter {game.current_location} {turn_count}",
                    "type": "Encounter",
                    "description": encounter,
                    "location": game.current_location,
                    "participants": alive_characters
                }
                event_name = obsidian.log_event(event_data)
                session_data["events"].append(event_name)
                run_data["events"].append(event_name)

            # Play turn
            game.play_turn()

            # Show combat log
            combat_log = aggregator.get_logs()
            logging.info(f"\nCombat Log for Turn {turn_count}:\n{combat_log}")

            # Log combat to Obsidian with detailed parsing
            combat_data = {
                "name": f"Combat Turn {turn_count}",
                "description": f"Combat during turn {turn_count}\n\n## Scene\n\n{scene_desc}",
                "location": game.current_location,
                "participants": alive_characters,
                "combat_log": combat_log,
                "turn_number": turn_count
            }
            combat_name = obsidian.log_combat(combat_data)
            session_data["combat"].append(combat_name)
            run_data["combat"].append(combat_name)

            # Extract individual actions from combat log for more detailed recording
            combat_actions = []
            for line in combat_log.split('\n'):
                if line.strip():
                    # Check if line contains an attack or ability use
                    for character in alive_characters:
                        if character in line and any(action in line.lower() for action in
                                                  ["attack", "strike", "hit", "cast", "use", "damage", "heal"]):
                            action_data = {
                                "name": f"Action {character} Turn {turn_count} {len(combat_actions)+1}",
                                "type": "Combat Action",
                                "description": line,
                                "location": game.current_location,
                                "participants": [character],
                                "parent_combat": combat_name
                            }
                            # Associate the action with a specific character and combat turn
                            combat_actions.append(action_data)

            # Log significant combat actions as separate events
            for action_data in combat_actions:
                action_name = obsidian.log_event(action_data)
                session_data["events"].append(action_name)
                run_data["events"].append(action_name)

            # Update character statuses in Obsidian
            for player in game.players:
                new_status = {
                    "hp": player.hp,
                    "max_hp": player.max_hp,
                    "alive": player.alive,
                    "status_effects": player.status_effects if hasattr(player, 'status_effects') else []
                }
                obsidian.update_character_status(player.name, new_status)

            for enemy in game.enemies:
                if enemy.alive or turn_count == 0:  # Log new enemies or update existing ones
                    character_data = {
                        "name": enemy.name,
                        "char_class": enemy.char_class,
                        "hp": enemy.hp,
                        "max_hp": enemy.max_hp,
                        "attack": enemy.attack,
                        "defense": enemy.defense,
                        "alive": enemy.alive,
                        "abilities": list(enemy.abilities.keys()) if hasattr(enemy, 'abilities') else [],
                        "status_effects": enemy.status_effects if hasattr(enemy, 'status_effects') else [],
                        "team": "Enemy"
                    }
                    obsidian.log_character(character_data)
                    if enemy.name not in run_data["characters"]:
                        run_data["characters"].append(enemy.name)

            # Show turn summary
            turn_summary = game.narrative_engine.summarize_combat(combat_log)
            logging.info("\nTurn Summary: " + turn_summary)

            # Add summary to session events
            summary_data = {
                "name": f"Summary Turn {turn_count}",
                "type": "Turn Summary",
                "description": turn_summary,
                "location": game.current_location,
                "participants": alive_characters,
                "related_combat": combat_name
            }
            summary_name = obsidian.log_event(summary_data)
            session_data["events"].append(summary_name)
            run_data["events"].append(summary_name)

            # Update Current Run.md to show the latest state of the game
            update_current_run(obsidian, run_data)

            time.sleep(1)  # Pause between turns

        # Show game conclusion
        if any(player.alive for player in game.players):
            conclusion = game.narrative_engine.handle_player_action(
                "The party", "emerges victorious",
                "The battle ends with heroic triumph!"
            )

            # Mark quest as completed
            obsidian.update_quest_objective("Main Quest", 0, True)

        else:
            conclusion = game.narrative_engine.handle_player_action(
                "The party", "has fallen",
                "Darkness claims the battlefield as all heroes are defeated."
            )
        logging.info("\nConclusion: " + conclusion)

        # Add conclusion to session
        session_data["summary"] += f"\n\n## Conclusion\n\n{conclusion}"

        # Add conclusion to run data
        run_data["conclusion"] = conclusion
        run_data["status"] = "completed"

        # Log conclusion as a final event
        conclusion_data = {
            "name": "Adventure Conclusion",
            "type": "Conclusion",
            "description": conclusion,
            "location": game.current_location,
            "participants": [char.name for char in game.players + game.enemies if char.alive]
        }
        conclusion_name = obsidian.log_event(conclusion_data)
        session_data["events"].append(conclusion_name)
        run_data["events"].append(conclusion_name)

        # Log the final session
        obsidian.log_session(session_data)
        logging.info("Logged complete session to Obsidian.")

        # Final update to Current Run.md
        update_current_run(obsidian, run_data)

    except KeyboardInterrupt:
        logging.info("\nGame interrupted by user.")

        # Still log the session with what we have
        session_data["summary"] += "\n\n## Interrupted\n\nThe game was interrupted by the user."
        run_data["status"] = "interrupted"
        run_data["conclusion"] = "The game was interrupted by the user."

        # Update Current Run.md with interrupted status
        update_current_run(obsidian, run_data)

        obsidian.log_session(session_data)

    except GameError as ge:
        logging.error("\nGame error: " + str(ge))
        run_data["status"] = "error"
        run_data["conclusion"] = f"Error: {str(ge)}"
        update_current_run(obsidian, run_data)

    except Exception as e:
        logging.error("\nUnexpected error: " + str(e))
        run_data["status"] = "error"
        run_data["conclusion"] = f"Unexpected error: {str(e)}"
        update_current_run(obsidian, run_data)

if __name__ == "__main__":
    main()
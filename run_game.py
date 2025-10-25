#!/usr/bin/env python3
import os
import time
import datetime
import logging
import re
import sys
import random
import argparse
from dnd_game import DnDGame, GameError, Character
from obsidian_logger import ObsidianLogger
from game_event_manager import GameEventManager
from save_state import save_game_to_file, load_game_from_file, list_save_files

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up file handler for logging to a file
log_file = "dnd_game_debug.log"
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Configure event manager logger
event_logger = logging.getLogger("game_event_manager")
event_logger.setLevel(logging.DEBUG)
event_logger.addHandler(file_handler)

def reconstruct_character(char_data: dict) -> Character:
    """
    Reconstruct a Character object from saved dictionary data.

    NOTE: This creates a new Character with saved combat stats but
    fresh inventory/spells. For short demo games, this is acceptable.
    For longer campaigns, extend the schema to save inventory.
    """
    char = Character(
        name=char_data["name"],
        char_class=char_data.get("char_class", "Fighter"),
        hp=char_data["hp"],
        max_hp=char_data["max_hp"],
        attack=char_data["attack"],
        defense=char_data["defense"]
    )
    char.alive = char_data.get("alive", True)
    char.status_effects = char_data.get("status_effects", [])
    return char

def extract_run_id():
    """Extract run ID from Current Run.md."""
    current_run_path = os.path.join("ai-dnd-test-vault", "Current Run.md")
    if not os.path.exists(current_run_path):
        return None

    try:
        with open(current_run_path, 'r') as f:
            content = f.read()
            # Look for run_id in YAML frontmatter
            match = re.search(r"run_id: ([^\n{]+)", content)
            if match and not match.group(1).strip().startswith("{{"):
                return match.group(1).strip()

            # If we found a template variable instead of a real run_id, generate a new one
            return datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    except Exception as e:
        logging.warning(f"Error extracting run ID: {e}")

    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def update_current_run(obsidian, run_data):
    """Update the Current Run.md file with the latest game state."""
    run_id = run_data.get('run_id')
    if not run_id:
        run_id = extract_run_id()
    if not run_id or "{{" in run_id:
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

    # Add session information
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

    # Log at debug level instead of info to reduce noise during frequent updates
    logging.debug(f"Updated Current Run.md (Run ID: {run_id}, Turn: {run_data.get('turn_count', 0)})")

def update_dashboard(obsidian, run_data):
    """Update the Dashboard.md file with the latest game state."""
    run_id = extract_run_id()
    if not run_id:
        run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Build content with updated game state
    content = f"""# Game Dashboard

*Last Updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## Current Game Status

**Run ID**: {run_id}
**Status**: {run_data.get('status', 'active')}
**Turn Count**: {run_data.get('turn_count', 0)}

## Active Quest
"""

    # Add quest information
    if 'quest' in run_data and run_data['quest']:
        content += f"[[{run_data['quest']}]]\n\n"
    else:
        content += "No quests started yet.\n\n"

    # Add character information
    content += "## Current Party\n\n"
    if 'characters' in run_data and run_data['characters']:
        for character in run_data['characters']:
            content += f"- [[{character}]]\n"
    else:
        content += "No characters created yet.\n\n"

    # Add recent events information
    content += "## Recent Events\n\n"
    if 'events' in run_data and run_data['events']:
        # Show last 3 events
        for event in run_data['events'][-3:]:
            if isinstance(event, dict):
                event_name = event.get('name', 'Unknown Event')
                content += f"- [[{event_name}]]\n"
            else:
                content += f"- [[{event}]]\n"
    else:
        content += "No events have occurred yet.\n\n"

    # Add navigation links
    content += """## Navigation
- [[Current Run|🎲 Current Game Session]]
- [[Index|📑 Game Index]]
- [[Characters/|👤 Characters]]
- [[Locations/|🗺️ Locations]]
- [[Events/|📜 Events]]
- [[Quests/|⚔️ Quests]]
- [[Items/|💎 Items]]
- [[Sessions/|📝 Sessions]]
"""

    # Write the updated file
    dashboard_path = os.path.join(obsidian.vault_path, "Dashboard.md")
    with open(dashboard_path, 'w') as f:
        f.write(content)

    logging.info(f"Updated Dashboard.md")

def run_game(resume_from: str = None, save_file: str = "saves/game_autosave.json"):
    """
    Run the D&D game with Obsidian integration.

    Args:
        resume_from: Path to save file to resume from (None = new game)
        save_file: Where to save game state (default: saves/game_autosave.json)
    """
    vault_path = "ai-dnd-test-vault"

    # Check if the vault exists
    if not os.path.exists(vault_path):
        logger.error(f"Vault not found at {vault_path}. Run reset_game.py first to set up the vault.")
        sys.exit(1)

    # Check if Current Run.md exists (indicating game is ready)
    if not os.path.exists(os.path.join(vault_path, "Current Run.md")):
        logger.error(f"Current Run.md not found. Run reset_game.py first to set up the vault.")
        sys.exit(1)

    # Handle resume logic
    if resume_from:
        try:
            logging.info(f"\n📂 Resuming game from {resume_from}...")
            saved_state = load_game_from_file(resume_from)

            # Extract saved data
            run_id = saved_state["run_id"]
            start_time = saved_state["start_time"]
            turn_count = saved_state["current_turn"]
            max_turns = saved_state["turn_limit"]
            current_location = saved_state["location"]

            logging.info(f"✅ Loaded: Run ID {run_id}, Turn {turn_count}/{max_turns}")

        except (FileNotFoundError, ValueError) as e:
            logging.error(f"❌ Failed to load save: {e}")
            sys.exit(1)
    else:
        # New game - these will be initialized below
        saved_state = None
        turn_count = 0
        max_turns = 10

    # Initialize Obsidian logger
    obsidian = ObsidianLogger(vault_path)
    logging.info("Initialized Obsidian logger for the game.")

    # Setup run_id and start_time based on new game or resume
    if not saved_state:
        # New game - generate fresh IDs
        run_id = extract_run_id()
        if not run_id or "{{" in run_id:
            run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            logging.info(f"Generated new run ID: {run_id}")
        else:
            logging.info(f"Using existing run ID: {run_id}")

        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # else: run_id, start_time already set from saved_state above

    # Initialize run data
    run_data = {
        "run_id": run_id,
        "start_time": start_time,
        "status": "active",
        "turn_count": turn_count,
        "characters": [],
        "events": [],
        "combat": [],
        "locations": []
    }

    # If resuming, restore Obsidian data
    if saved_state and saved_state.get("obsidian_data"):
        obs_data = saved_state["obsidian_data"]
        run_data["characters"] = obs_data.get("characters", [])
        run_data["events"] = obs_data.get("events", [])
        run_data["locations"] = obs_data.get("locations", [])
        if obs_data.get("session"):
            run_data["session"] = obs_data["session"]

    # Initialize the event manager for real-time updates
    event_manager = GameEventManager(obsidian, run_data)
    logging.info("Initialized event manager for real-time updates.")

    # Update the Current Run.md file immediately with the valid run_id
    update_current_run(obsidian, run_data)
    logging.info(f"Updated Current Run.md with run ID: {run_id}")

    # Initialize game
    logging.info("\nInitializing D&D Game...")
    if saved_state:
        # Resume: Create game without auto-creating characters
        game = DnDGame(auto_create_characters=False, model="mistral")

        # Reconstruct players
        game.players = [reconstruct_character(p) for p in saved_state["players"]]
        for player in game.players:
            player.team = "players"

        # Reconstruct enemies
        game.enemies = [reconstruct_character(e) for e in saved_state["enemies"]]
        for enemy in game.enemies:
            enemy.team = "enemies"

        # Restore location
        game.current_location = saved_state["location"]

        logging.info(f"✅ Resumed with {len(game.players)} players, {len(game.enemies)} enemies")
        logging.info(f"   Location: {game.current_location}")
    else:
        # New game: Auto-create characters
        game = DnDGame(model="mistral")

    # Log initial setup (skip if resuming - already logged)
    if not saved_state:
        # Log initial world locations to Obsidian
        if hasattr(game, 'current_location'):
            location_data = {
                "name": game.current_location,
                "description": f"The starting location of the adventure.",
                "connections": {},  # Will be populated as game progresses
                "type": "Starting Area"
            }
            # Use event-aware logging for real-time updates
            obsidian.log_location_with_event(location_data, event_manager)
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
                "status": "Active",
                "status_summary": f"Active - HP: {player.hp}/{player.max_hp}",
                "bio": f"A brave {player.char_class} on a grand adventure.",
                "abilities": list(player.abilities.keys()) if hasattr(player, 'abilities') else [],
                "status_effects": player.status_effects if hasattr(player, 'status_effects') else [],
                "team": "Player"
            }
            # Use event-aware logging for real-time updates
            obsidian.log_character_with_event(character_data, event_manager)
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
            "overview": f"A grand adventure awaits: {quest_intro}",
            "objectives": ["Complete the adventure"],
            "start_date": start_time
        }
        obsidian.log_quest_with_event(quest_data, event_manager)
        logging.info(f"Quest logged to Obsidian: {quest_data['name']}")
        run_data["quest"] = "Main Quest"

        # Create session data
        session_name = f"Session {time.strftime('%Y%m%d')}"
        session_data = {
            "name": session_name,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "run_id": run_id,
            "summary": f"The party embarks on a new adventure: {quest_intro}",
            "characters": [player.name for player in game.players],
            "events": [],
            "combat": [],
            "next_steps": "The adventure begins..."
        }

        # Add locations if available
        if hasattr(game, 'current_location'):
            session_data["locations"] = [game.current_location]

        # Log the session
        obsidian.log_session(session_data)
        run_data["session"] = session_name

        # Update Current Run.md with initial state
        update_current_run(obsidian, run_data)

        # Update Dashboard.md
        update_dashboard(obsidian, run_data)
    else:
        logging.info(f"📝 Skipping initial setup (resuming from turn {turn_count})")

    # turn_count and max_turns already set above (from saved_state or defaults)

    try:
        while not game.is_game_over() and turn_count < max_turns:
            # Increment turn count
            turn_count += 1
            run_data["turn_count"] = turn_count

            # Log turn start
            logging.info(f"\n==== TURN {turn_count} ====")

            # Describe current scene
            alive_characters = [char.name for char in game.players + game.enemies if char.alive]
            scene_desc = game.narrative_engine.describe_scene(game.current_location, alive_characters)
            logging.info("\nScene: " + scene_desc)

            # Log the scene as an event
            event_data = {
                "name": f"Scene Turn {turn_count}",
                "type": "Scene",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": game.current_location,
                "summary": f"Turn {turn_count} scene at {game.current_location}",
                "description": scene_desc,
                "participants": alive_characters
            }
            obsidian.log_event(event_data)
            run_data["events"].append(event_data["name"])

            # Execute player actions
            for player in [p for p in game.players if p.alive]:
                action = game.generate_player_action(player)
                logging.info(f"\n{player.name}'s Action: {action}")

                # Update character status with their action
                obsidian.update_character_status(player.name, {
                    "actions": [f"[Turn {turn_count}] {action}"]
                })

                # If the action introduces a new location, log it
                if hasattr(game, 'current_location') and "goes to" in action.lower():
                    # Try to extract a new location name
                    location_match = re.search(r"goes to (.+?)\.?$", action, re.IGNORECASE)
                    if location_match:
                        new_location = location_match.group(1).strip()

                        # Check if this is actually a new location
                        if new_location != game.current_location:
                            # Log the new location
                            location_data = {
                                "name": new_location,
                                "description": f"A location discovered during the adventure.",
                                "connections": {game.current_location: "Connected from"},
                                "type": "Discovered Area",
                                "discovered_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            obsidian.log_location(location_data)

                            # Update original location with connection to new location
                            # (This would ideally come from a more robust location tracking system)
                            game.current_location = new_location
                            run_data["locations"].append(new_location)

            # Check for combat
            enemy_spawn_chance = 0.4  # 40% chance to spawn enemies each turn
            if not game.enemies and random.random() < enemy_spawn_chance:
                game.spawn_enemies()

                # If enemies spawned, log them
                if game.enemies:
                    enemies_desc = ", ".join([f"{e.name} (HP: {e.hp}/{e.max_hp})" for e in game.enemies])
                    logging.info(f"\nEnemies appear: {enemies_desc}")

                    # Log enemy characters
                    for enemy in game.enemies:
                        enemy_data = {
                            "name": enemy.name,
                            "char_class": "Enemy",
                            "hp": enemy.hp,
                            "max_hp": enemy.max_hp,
                            "attack": enemy.attack,
                            "defense": enemy.defense,
                            "alive": enemy.alive,
                            "status": "Hostile",
                            "status_summary": f"Hostile - HP: {enemy.hp}/{enemy.max_hp}",
                            "bio": f"An enemy encountered at {game.current_location}.",
                            "abilities": [],
                            "status_effects": [],
                            "team": "Enemy"
                        }
                        obsidian.log_character(enemy_data)

                    # Log the encounter as an event
                    encounter_data = {
                        "name": f"Encounter Turn {turn_count}",
                        "type": "Encounter",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "location": game.current_location,
                        "summary": f"Enemies appeared at {game.current_location}",
                        "description": f"The party encountered enemies: {enemies_desc}",
                        "participants": alive_characters + [e.name for e in game.enemies]
                    }
                    obsidian.log_event(encounter_data)
                    run_data["events"].append(encounter_data["name"])

            # If enemies are present, conduct combat
            if game.enemies:
                combat_name = f"Combat Turn {turn_count}"
                combat_log = []

                # Log combat start
                combat_data = {
                    "name": combat_name,
                    "location": game.current_location,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "overview": f"Combat at {game.current_location}",
                    "player_team": [p.name for p in game.players if p.alive],
                    "enemy_team": [e.name for e in game.enemies if e.alive],
                    "combat_log": [],
                    "outcome": "In progress..."
                }

                logging.info("\n=== COMBAT ===")

                # Process combat rounds
                combat_round = 1
                while game.enemies and any(p.alive for p in game.players):
                    logging.info(f"\nCombat Round {combat_round}")
                    round_actions = []

                    # Player turns
                    for player in [p for p in game.players if p.alive]:
                        target = game.select_target(game.enemies)
                        if target:
                            damage = game.calculate_damage(player, target)
                            target.hp -= damage
                            if target.hp <= 0:
                                target.alive = False
                                target.hp = 0
                                action = f"{player.name} defeats {target.name} with {damage} damage!"
                            else:
                                action = f"{player.name} hits {target.name} for {damage} damage! {target.name} has {target.hp}/{target.max_hp} HP left."

                            logging.info(action)
                            round_actions.append(action)

                            # Update character statuses
                            obsidian.update_character_status(player.name, {
                                "actions": [f"[Combat {combat_round}] {action}"]
                            })

                            obsidian.update_character_status(target.name, {
                                "hp": target.hp,
                                "status": "Dead" if not target.alive else "Hostile",
                                "status_summary": f"{'Dead' if not target.alive else 'Hostile'} - HP: {target.hp}/{target.max_hp}"
                            })

                            # Check if all enemies defeated
                            if not any(e.alive for e in game.enemies):
                                victory_msg = f"All enemies defeated!"
                                logging.info(victory_msg)
                                round_actions.append(victory_msg)
                                combat_data["outcome"] = "Victory! All enemies defeated."
                                break

                    # Enemy turns (if still alive)
                    if any(e.alive for e in game.enemies):
                        for enemy in [e for e in game.enemies if e.alive]:
                            target = game.select_target(game.players)
                            if target:
                                damage = game.calculate_damage(enemy, target)
                                target.hp -= damage
                                if target.hp <= 0:
                                    target.alive = False
                                    target.hp = 0
                                    action = f"{enemy.name} defeats {target.name} with {damage} damage!"
                                else:
                                    action = f"{enemy.name} hits {target.name} for {damage} damage! {target.name} has {target.hp}/{target.max_hp} HP left."

                                logging.info(action)
                                round_actions.append(action)

                                # Update character statuses
                                obsidian.update_character_status(enemy.name, {
                                    "actions": [f"[Combat {combat_round}] {action}"]
                                })

                                obsidian.update_character_status(target.name, {
                                    "hp": target.hp,
                                    "status": "Dead" if not target.alive else "Active",
                                    "status_summary": f"{'Dead' if not target.alive else 'Active'} - HP: {target.hp}/{target.max_hp}"
                                })

                                # Check if all players defeated
                                if not any(p.alive for p in game.players):
                                    defeat_msg = f"All players defeated! Game over."
                                    logging.info(defeat_msg)
                                    round_actions.append(defeat_msg)
                                    combat_data["outcome"] = "Defeat! All players were defeated."
                                    break

                    # Add this round to the combat log
                    combat_log.append({
                        "number": combat_round,
                        "actions": round_actions
                    })

                    # Increment round counter
                    combat_round += 1

                    # Safety break in case combat goes too long
                    if combat_round > 10:
                        stalemate_msg = "Combat reached maximum rounds and ended in a stalemate."
                        logging.info(stalemate_msg)
                        combat_data["outcome"] = "Stalemate after 10 rounds."
                        break

                # Clean up any defeated enemies
                game.enemies = [e for e in game.enemies if e.alive]

                # Update combat data with the log
                combat_data["combat_log"] = combat_log

                # Log the combat
                obsidian.log_combat(combat_data)
                run_data["combat"].append(combat_name)

            # Update Current Run.md and Dashboard
            update_current_run(obsidian, run_data)
            update_dashboard(obsidian, run_data)

            # AUTOSAVE after each turn
            try:
                save_game_to_file(
                    players=game.players,
                    enemies=game.enemies,
                    location=game.current_location,
                    run_id=run_id,
                    current_turn=turn_count,
                    turn_limit=max_turns,
                    filepath=save_file,
                    start_time=start_time,
                    quest_data=run_data.get("quest"),
                    obsidian_data={
                        "characters": run_data.get("characters", []),
                        "events": run_data.get("events", []),
                        "locations": run_data.get("locations", []),
                        "session": run_data.get("session")
                    }
                )
            except Exception as e:
                logging.warning(f"⚠️  Failed to autosave: {e}")

            # Add a small delay between turns for readability
            time.sleep(1)

        # Game conclusion
        if turn_count >= max_turns:
            conclusion = "The adventure concludes after reaching the maximum number of turns."
        elif not any(p.alive for p in game.players):
            conclusion = "The adventure ends in tragedy as all players were defeated."
        else:
            conclusion = "The adventure concludes successfully!"

        logging.info(f"\nCONCLUSION: {conclusion}")

        # Update run data with conclusion
        run_data["status"] = "completed"
        run_data["conclusion"] = conclusion

        # Log the conclusion as an event
        conclusion_event = {
            "name": "Adventure Conclusion",
            "type": "Conclusion",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": game.current_location,
            "summary": "The adventure has concluded",
            "description": conclusion,
            "participants": [p.name for p in game.players]
        }
        obsidian.log_event(conclusion_event)
        run_data["events"].append(conclusion_event["name"])

        # Final updates to Current Run.md and Dashboard
        update_current_run(obsidian, run_data)
        update_dashboard(obsidian, run_data)

    except GameError as e:
        logging.error(f"Game error: {e}")
        run_data["status"] = "error"
        run_data["conclusion"] = f"The adventure ended unexpectedly due to an error: {e}"
        update_current_run(obsidian, run_data)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        run_data["status"] = "error"
        run_data["conclusion"] = f"The adventure ended unexpectedly due to an error: {e}"
        update_current_run(obsidian, run_data)

    logging.info("\nGame completed. Check your Obsidian vault for the adventure log.")
    return True

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run D&D game with Obsidian integration and save/load support"
    )
    parser.add_argument(
        "--resume",
        type=str,
        metavar="SAVE_FILE",
        help="Resume from a saved game file (e.g., saves/game_autosave.json)"
    )
    parser.add_argument(
        "--save-to",
        type=str,
        default="saves/game_autosave.json",
        metavar="SAVE_FILE",
        help="Where to save game state (default: saves/game_autosave.json)"
    )
    parser.add_argument(
        "--list-saves",
        action="store_true",
        help="List all available save files and exit"
    )

    args = parser.parse_args()

    # Handle --list-saves
    if args.list_saves:
        print("\n📁 Available save files:")
        saves = list_save_files("saves")
        if not saves:
            print("   No save files found in saves/ directory")
        else:
            for i, save_path in enumerate(saves, 1):
                try:
                    state = load_game_from_file(save_path)
                    print(f"\n{i}. {save_path}")
                    print(f"   Run ID: {state['run_id']}")
                    print(f"   Turn: {state['current_turn']}/{state['turn_limit']}")
                    print(f"   Location: {state['location']}")
                    print(f"   Players: {len(state['players'])} alive")
                except Exception as e:
                    print(f"\n{i}. {save_path} (corrupted: {e})")
        sys.exit(0)

    # Run the game
    run_game(resume_from=args.resume, save_file=args.save_to)
    logger.info("Game completed!")
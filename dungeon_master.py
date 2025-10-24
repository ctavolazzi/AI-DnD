import os
import logging
import datetime
import time
import random
import re
import sys
from typing import Dict, List, Any, Optional, Union, Tuple

from dnd_game import DnDGame, GameError, Character
from obsidian_logger import ObsidianLogger
from game_event_manager import GameEventManager
from game_manager import GameManager
from quest_system import QuestManager, QuestObjective
from world_builder import WorldManager

class DungeonMaster:
    """
    The central intelligence that manages a single Obsidian vault and runs D&D games.
    Currently handles one run at a time, but designed for future extension to multiple runs.
    """

    def __init__(self, vault_path: str = "ai-dnd-test-vault", model: str = "mistral"):
        """
        Initialize the Dungeon Master for a specific vault.

        Args:
            vault_path: Path to the Obsidian vault
            model: The LLM model to use for narrative generation
        """
        self.vault_path = vault_path
        self.model = model
        self.current_run_id = None
        self.current_run_data = None
        self.obsidian = None
        self.event_manager = None
        self.game_manager = None
        self.quest_manager = None
        self.world_manager = None
        self.game = None
        self.logger = logging.getLogger("dungeon_master")

        # Ensure the vault exists
        if not os.path.exists(vault_path):
            self.logger.error(f"Vault not found at {vault_path}. Please run reset_game.py first.")
            raise ValueError(f"Vault not found at {vault_path}")

        # Initialize logger
        self._setup_logging()

        # Initialize Obsidian integration
        self.obsidian = ObsidianLogger(vault_path)
        self.logger.info(f"Initialized Obsidian logger for vault: {vault_path}")

    def _setup_logging(self):
        """Set up logging for the Dungeon Master."""
        # Get the current logger
        self.logger = logging.getLogger('dungeon_master')

        # Check if handlers already exist to avoid duplicates
        if not self.logger.handlers:
            # File handler for detailed logging
            file_handler = logging.FileHandler("dungeon_master.log", mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.DEBUG)

            # Don't propagate to the root logger which already has console output
            self.logger.propagate = False

    def extract_run_id(self) -> Optional[str]:
        """Extract run ID from Current Run.md."""
        current_run_path = os.path.join(self.vault_path, "Current Run.md")
        if not os.path.exists(current_run_path):
            self.logger.info("No Current Run.md found. A new file will be created with a fresh run_id.")
            return None

        try:
            with open(current_run_path, 'r') as f:
                content = f.read()
                # Look for run_id in YAML frontmatter
                match = re.search(r"run_id: ([^\n{]+)", content)
                if match and not match.group(1).strip().startswith("{{"):
                    return match.group(1).strip()

                # If we found a template variable instead of a real run_id, generate a new one
                self.logger.warning("Current Run.md exists but contains template variables. Will generate new run_id.")
                return datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        except Exception as e:
            self.logger.warning(f"Error extracting run ID: {e}")

        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def initialize_run(self) -> str:
        """
        Initialize a new run, setting up all necessary components.
        Returns the run ID.
        """
        # Extract or generate run ID
        run_id = self.extract_run_id()
        if not run_id or "{{" in run_id:
            run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            self.logger.info(f"Generated new run ID: {run_id}")
        else:
            self.logger.info(f"Using existing run ID: {run_id}")

        # Initialize run data
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_run_id = run_id
        self.current_run_data = {
            "run_id": run_id,
            "start_time": start_time,
            "status": "active",
            "turn_count": 0,
            "characters": [],
            "events": [],
            "combat": [],
            "locations": [],
            "sessions": []
        }

        # Initialize event manager with a reference to this DungeonMaster instance
        self.event_manager = GameEventManager(self.obsidian, self.current_run_data, self)
        self.logger.info("Initialized event manager for real-time updates")

        # Initialize game manager
        self.game_manager = GameManager(self.obsidian, self.event_manager)
        self.logger.info("Initialized game manager for entity tracking and theory of mind")

        # Initialize quest manager
        self.quest_manager = QuestManager()
        self.logger.info("Initialized quest manager for quest tracking")

        # Initialize world manager
        self.world_manager = WorldManager()
        self.logger.info("Initialized world manager with Emberpeak Region")

        # Update Current Run.md immediately - ensure it exists
        self.update_current_run(force_create=True)
        self.logger.info(f"Updated Current Run.md with run ID: {run_id}")

        return run_id

    def update_current_run(self, force_create=False):
        """Update the Current Run.md file with the latest game state."""
        if not self.current_run_data:
            self.logger.warning("Attempted to update Current Run.md but no run data is available")
            return False

        run_id = self.current_run_data.get('run_id')
        if not run_id:
            run_id = self.extract_run_id()
        if not run_id or "{{" in run_id:
            run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Check if Current Run.md exists
        current_run_path = os.path.join(self.vault_path, "Current Run.md")
        if not os.path.exists(current_run_path) and not force_create:
            self.logger.warning("Current Run.md does not exist and force_create is False. Skipping update.")
            return False

        try:
            # Build content with YAML frontmatter
            content = f"""---
run_id: {run_id}
timestamp: {self.current_run_data.get('start_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
status: {self.current_run_data.get('status', 'active')}
turn_count: {self.current_run_data.get('turn_count', 0)}
---

# Current Game Run: {run_id}

Started: {self.current_run_data.get('start_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
Last Updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Current Turn: {self.current_run_data.get('turn_count', 0)}

## Active Quest
"""

            # Add quest information
            if 'quest' in self.current_run_data and self.current_run_data['quest']:
                content += f"[[{self.current_run_data['quest']}]]\n\n"
            else:
                content += "No quests started yet.\n\n"

            # Add character information
            content += "## Characters\n\n"
            if 'characters' in self.current_run_data and self.current_run_data['characters']:
                for character in self.current_run_data['characters']:
                    content += f"- [[{character}]]\n"
            else:
                content += "No characters created yet.\n\n"

            # Add events information
            content += "## Events\n\n"
            if 'events' in self.current_run_data and self.current_run_data['events']:
                # Show last 5 events
                for event in self.current_run_data['events'][-5:]:
                    if isinstance(event, dict):
                        event_name = event.get('name', 'Unknown Event')
                        content += f"- [[{event_name}]]\n"
                    else:
                        content += f"- [[{event}]]\n"
            else:
                content += "No events have occurred yet.\n\n"

            # Add combat information
            content += "## Combat\n\n"
            if 'combat' in self.current_run_data and self.current_run_data['combat']:
                # Show last 3 combats
                for combat in self.current_run_data['combat'][-3:]:
                    if isinstance(combat, dict):
                        combat_name = combat.get('name', 'Unknown Combat')
                        content += f"- [[{combat_name}]]\n"
                    else:
                        content += f"- [[{combat}]]\n"
            else:
                content += "No combat has occurred yet.\n\n"

            # Add session information
            content += "## Sessions\n\n"
            if 'session' in self.current_run_data and self.current_run_data['session']:
                content += f"- [[{self.current_run_data['session']}]]\n\n"
            else:
                content += "No sessions recorded yet.\n\n"

            # Add conclusion if available
            if 'conclusion' in self.current_run_data and self.current_run_data['conclusion']:
                content += f"## Conclusion\n\n{self.current_run_data['conclusion']}\n\n"

            # Add footer
            content += "*This run is currently in progress. Content will be updated as the game progresses.*\n"

            # Write the updated file
            with open(current_run_path, 'w') as f:
                f.write(content)

            self.logger.debug(f"Updated Current Run.md (Run ID: {run_id}, Turn: {self.current_run_data.get('turn_count', 0)})")

            # Log a detailed summary of what was updated
            char_count = len(self.current_run_data.get('characters', []))
            event_count = len(self.current_run_data.get('events', []))
            location_count = len(self.current_run_data.get('locations', []))
            self.logger.info(f"Current Run.md updated with: {char_count} characters, {event_count} events, {location_count} locations")

            return True

        except Exception as e:
            self.logger.error(f"Error updating Current Run.md: {e}")
            return False

    def update_dashboard(self):
        """Update the Dashboard.md file with the latest game info."""
        if not self.current_run_data:
            self.logger.warning("Attempted to update Dashboard.md but no run data is available")
            return

        # Content for Dashboard.md
        content = """---
aliases: [📊 Dashboard]
---

# Game Dashboard

> **Status**: Active Run in Progress
> **Last Updated**: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

## Current Game

[[Current Run|🎲 Current Game Session]]

## Statistics
- **Characters**: """ + str(len(self.current_run_data.get('characters', []))) + """
- **Locations Visited**: """ + str(len(self.current_run_data.get('locations', []))) + """
- **Events**: """ + str(len(self.current_run_data.get('events', []))) + """
- **Combat Encounters**: """ + str(len(self.current_run_data.get('combat', []))) + """

## Active Characters
"""

        # Add characters
        if 'characters' in self.current_run_data and self.current_run_data['characters']:
            for character in self.current_run_data['characters'][:5]:  # Show top 5
                content += f"- [[{character}]]\n"
        else:
            content += "- No active characters\n"

        content += "\n## Recent Events\n"

        # Add events
        if 'events' in self.current_run_data and self.current_run_data['events']:
            for event in self.current_run_data['events'][-3:]:  # Show last 3
                if isinstance(event, dict):
                    event_name = event.get('name', 'Unknown Event')
                    content += f"- [[{event_name}]]\n"
                else:
                    content += f"- [[{event}]]\n"
        else:
            content += "- No events recorded\n"

        content += """
## Navigation
- [[Start|📘 How to Follow]]
- [[Index|📑 Complete Index]]
- [[Characters/|👤 Characters]]
- [[Locations/|🗺️ Locations]]
- [[Events/|🎭 Events]]
- [[Quests/|⚔️ Quests]]
- [[Items/|💎 Items]]
- [[Sessions/|📝 Sessions]]
"""

        # Write the updated file
        dashboard_path = os.path.join(self.vault_path, "Dashboard.md")
        with open(dashboard_path, 'w') as f:
            f.write(content)

        self.logger.debug("Updated Dashboard.md")

    def initialize_game(self) -> None:
        """Initialize the D&D game engine."""
        try:
            self.logger.info("\nInitializing D&D Game...")
            self.game = DnDGame(model=self.model)

            # Set starting location from world manager
            if self.world_manager:
                self.game.current_location = self.world_manager.current_location_id
                current_loc = self.world_manager.get_current_location()
                self.logger.info(f"Starting location: {current_loc.name}")
            else:
                self.logger.warning("World manager not initialized, using default location")

            # Generate initial quest FIRST before any character processing
            self.logger.info("\nGenerating main quest...")
            quest_intro = self.game.narrative_engine.generate_quest(difficulty="medium", theme="epic battle")
            self.logger.info("\nQuest generated successfully: " + quest_intro)

            # Log the quest to Obsidian immediately (we'll update it with characters later)
            quest_data = {
                "name": "Main Quest",
                "description": quest_intro,
                "status": "Active",
                "difficulty": "Medium",
                "overview": f"A grand adventure awaits: {quest_intro}",
                "objectives": ["Complete the adventure"],
                "start_date": self.current_run_data.get('start_time')
            }
            self.obsidian.log_quest_with_event(quest_data, self.event_manager)
            self.logger.info("Quest logged to Obsidian: Main Quest")
            self.current_run_data["quest"] = "Main Quest"

            # Create structured quest in quest manager
            if self.quest_manager:
                starter_quest = self.quest_manager.generate_starter_quest(
                    location=self.game.current_location,
                    characters=[p.name for p in self.game.players]
                )
                self.current_run_data["quest_id"] = starter_quest.quest_id
                self.logger.info(f"Created structured quest: {starter_quest.title}")

            # After quest is created, now process locations and characters
            # Log initial world locations to Obsidian
            if hasattr(self.game, 'current_location'):
                # Get the character names for the starting location
                character_names = [player.name for player in self.game.players]

                # Get location details from world manager if available
                if self.world_manager:
                    current_loc = self.world_manager.get_current_location()
                    location_data = {
                        "name": current_loc.name,
                        "description": current_loc.description,
                        "connections": current_loc.connections,
                        "type": current_loc.location_type,
                        "characters": character_names,
                        "npcs": current_loc.npcs,
                        "services": current_loc.services
                    }
                else:
                    location_data = {
                        "name": self.game.current_location,
                        "description": f"The starting location of the adventure.",
                        "connections": {},
                        "type": "Starting Area",
                        "characters": character_names
                    }
                # Use event-aware logging for real-time updates
                self.obsidian.log_location_with_event(location_data, self.event_manager)
                self.logger.info(f"Logged starting location: {self.game.current_location}")

            # Log player characters to Obsidian
            character_names = []
            for player in self.game.players:
                character_names.append(player.name)
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
                    "team": "Player",
                    "location": self.game.current_location,  # Add location for theory of mind
                    "quests": ["Main Quest"]  # Associate character with the main quest
                }
                # Use event-aware logging for real-time updates
                self.obsidian.log_character_with_event(character_data, self.event_manager)
                self.logger.info(f"Logged player character: {player.name}")

                # Ensure the GameManager creates journals for each character
                # The character_created event should already trigger this via event listeners,
                # but we'll check if the journal exists and create it if needed
                if self.game_manager and hasattr(self.game_manager, 'journal_manager'):
                    journal_path = os.path.join(self.vault_path, "Journals",
                                               self.obsidian._sanitize_filename(player.name) + ".md")
                    if not os.path.exists(journal_path):
                        self.logger.info(f"Creating journal for {player.name}")
                        # Extract the player Character object data for rich journal content
                        self.game_manager.journal_manager.create_character_journal(player)

            # Now update the quest with the character associations
            updated_quest_data = quest_data.copy()
            updated_quest_data["characters"] = character_names
            updated_quest_data["locations"] = [self.game.current_location]
            self.obsidian.log_quest_with_event(updated_quest_data, self.event_manager)
            self.logger.info(f"Updated Main Quest with character associations: {', '.join(character_names)}")

            # Create session data with quest already established
            session_name = f"Session {time.strftime('%Y%m%d')}"
            session_data = {
                "name": session_name,
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "run_id": self.current_run_id,
                "summary": f"The party embarks on a new adventure: {quest_intro}",
                "characters": [player.name for player in self.game.players],
                "events": [],
                "combat": [],
                "next_steps": "The adventure begins..."
            }

            # Add locations if available
            if hasattr(self.game, 'current_location'):
                session_data["locations"] = [self.game.current_location]

            # Log the session
            self.obsidian.log_session_with_event(session_data, self.event_manager)
            self.logger.info(f"Logged session: {session_name}")
            self.current_run_data["session"] = session_name

            # Final updates to Current Run.md and Dashboard
            self.update_current_run()
            self.update_dashboard()

            # NOW generate character introductions after everything else is set up
            self.logger.info("\nGenerating character introductions...")
            self.game.generate_character_introductions()

            # Create journal entries for character introductions
            for player in self.game.players:
                if self.game_manager and hasattr(self.game_manager, 'journal_manager'):
                    # Create an introduction event for journal entries
                    intro_event = {
                        "name": f"{player.name}'s Introduction",
                        "description": f"{player.name} begins the adventure.",
                        "location": self.game.current_location,
                        "characters": [player.name],
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Character Introduction"
                    }

                    # Add entry to character journal for this introduction
                    self.game_manager._on_event_occurred(intro_event)
                    self.logger.info(f"Journal entry created for {player.name}'s introduction")

        except Exception as e:
            self.logger.error(f"Error initializing game: {e}", exc_info=True)
            raise

    def run_game_loop(self, max_turns: int = 10) -> bool:
        """
        Run the main game loop for a specified number of turns.

        Args:
            max_turns: Maximum number of turns to run

        Returns:
            True if game completed successfully, False otherwise
        """
        if not self.game:
            self.logger.error("Game not initialized. Call initialize_game() first.")
            return False

        try:
            # Main game loop
            for turn in range(max_turns):
                self.current_run_data["turn_count"] = turn + 1
                self.logger.info(f"\n==== TURN {turn + 1} ====")

                # Generate scene
                scene = self.game.narrative_engine.describe_scene(
                    location=self.game.current_location,
                    characters=self.game.players
                )
                self.logger.info(f"\nScene: {scene}")

                # Increment scene counter
                self.game.scene_counter += 1

                # Log the scene as an event
                scene_data = {
                    "name": f"Scene {self.game.scene_counter}",
                    "type": "Scene",
                    "location": self.game.current_location,
                    "summary": "A new scene unfolds",
                    "description": scene,
                    "participants": [player.name for player in self.game.players],
                    "related_quests": ["Main Quest"]  # Add Main Quest by default
                }
                self.obsidian.log_event_with_event(scene_data, self.event_manager)

                # Display active quest objectives
                if self.quest_manager:
                    active_objectives = self.quest_manager.get_all_active_objectives()
                    if active_objectives:
                        self.logger.info("\n=== ACTIVE OBJECTIVES ===")
                        for quest_title, objective in active_objectives:
                            progress_str = f"({objective.progress}/{objective.quantity})" if objective.quantity > 1 else ""
                            self.logger.info(f"  - {objective.description} {progress_str}")
                        self.logger.info("")

                # Process character actions with choices
                for player in self.game.players:
                    if not player.alive:
                        continue

                    self.logger.info(f"\n--- {player.name}'s Turn ---")

                    # Generate player choices
                    choices = self.game.narrative_engine.generate_player_choices(
                        player.name,
                        player.char_class,
                        self.game.current_location,
                        scene
                    )

                    # Display choices (in actual game, player would select)
                    self.logger.info(f"\n{player.name} considers the options:")
                    for i, choice in enumerate(choices, 1):
                        self.logger.info(f"  {i}. {choice['text']}")

                    # AI automatically selects a choice (for autonomous gameplay)
                    selected_choice = random.choice(choices)
                    self.logger.info(f"\n{player.name} chooses: {selected_choice['text']}")

                    # Resolve the choice
                    success = None
                    check_data = None

                    if selected_choice.get('requires_check'):
                        # Make ability check
                        ability = selected_choice.get('ability', 'WIS')
                        skill = selected_choice.get('skill')
                        dc = selected_choice.get('dc', 12)

                        check_data = player.ability_check(ability, dc, skill)
                        success = check_data['success']

                        # Log the skill check
                        if self.obsidian:
                            self.obsidian.log_skill_check(check_data, self.event_manager)

                    # Generate outcome narrative
                    outcome = self.game.narrative_engine.describe_choice_outcome(
                        player.name,
                        selected_choice,
                        success,
                        scene
                    )
                    self.logger.info(f"\nOutcome: {outcome}")

                    # Log the choice as an event
                    action_data = {
                        "name": f"{player.name}'s Choice - Turn {turn+1}",
                        "type": "Player Choice",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "location": self.game.current_location,
                        "summary": f"{player.name} makes a decision",
                        "description": f"Choice: {selected_choice['text']}\nOutcome: {outcome}",
                        "participants": [player.name],
                        "related_quests": ["Main Quest"],
                        "choice_data": selected_choice,
                        "skill_check": check_data
                    }
                    self.obsidian.log_event_with_event(action_data, self.event_manager)

                    # Update quest progress
                    if self.quest_manager:
                        quest_updated = self.quest_manager.check_objective_triggers(
                            "player_action",
                            {"player": player.name, "choice": selected_choice, "success": success}
                        )
                        if quest_updated:
                            self.logger.info(f"Quest objectives updated!")

                    # Theory of mind: Notify other characters at this location
                    self.game_manager.notify_entities_at_location(
                        self.game.current_location,
                        action_data,
                        exclude=[player.name]
                    )

                # Handle enemies and encounters
                if hasattr(self.game, 'process_encounter') and random.random() < 0.3:  # 30% chance per turn
                    self.logger.info("\n=== ENCOUNTER ===")
                    self.game.process_encounter()

                    # Update quest progress for combat
                    if self.quest_manager:
                        quest_updated = self.quest_manager.check_objective_triggers(
                            "combat_victory",
                            {"location": self.game.current_location}
                        )

                # Check quest completion
                if self.quest_manager:
                    for quest in self.quest_manager.get_active_quests():
                        if quest.check_completion():
                            self.logger.info(f"\n🎉 QUEST COMPLETED: {quest.title} 🎉")
                            self.logger.info(f"Rewards: {quest.rewards}")

                            # Log quest completion
                            quest_complete_data = {
                                "name": f"Quest Complete: {quest.title}",
                                "type": "Quest Completion",
                                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "location": self.game.current_location,
                                "summary": f"Quest '{quest.title}' has been completed!",
                                "description": f"The party has completed {quest.title}. Rewards: {quest.rewards}",
                                "participants": [p.name for p in self.game.players],
                                "quest_data": quest.to_dict()
                            }
                            self.obsidian.log_event_with_event(quest_complete_data, self.event_manager)

                # Update Current Run.md and Dashboard after each turn
                self.update_current_run()
                self.update_dashboard()

                # Sleep briefly to allow for LLM rate limits and human readability
                time.sleep(1)

            # Generate conclusion
            conclusion = self.game.narrative_engine.generate_conclusion()
            self.logger.info(f"\nCONCLUSION: {conclusion}")

            # Update run data with conclusion
            self.current_run_data["status"] = "completed"
            self.current_run_data["conclusion"] = conclusion

            # Log the conclusion as an event
            conclusion_event = {
                "name": "Adventure Conclusion",
                "type": "Conclusion",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": self.game.current_location,
                "summary": "The adventure has concluded",
                "description": conclusion,
                "participants": [p.name for p in self.game.players],
                "related_quests": ["Main Quest"]  # Add Main Quest by default
            }
            self.obsidian.log_event_with_event(conclusion_event, self.event_manager)

            # Final updates to Current Run.md and Dashboard
            self.update_current_run()
            self.update_dashboard()

            return True

        except GameError as e:
            import traceback
            error_tb = traceback.format_exc()
            self.logger.error(f"Game error: {e}")
            self.logger.error(f"Game error traceback:\n{error_tb}")

            # Log specific error context
            self.logger.error(f"Error occurred at turn: {self.current_run_data.get('turn_count', 'unknown')}")
            self.logger.error(f"Current location: {self.game.current_location if hasattr(self.game, 'current_location') else 'unknown'}")
            self.logger.error(f"Active characters: {[p.name for p in self.game.players if p.alive] if hasattr(self.game, 'players') else 'unknown'}")

            self.current_run_data["status"] = "error"
            self.current_run_data["conclusion"] = f"The adventure ended unexpectedly due to an error: {e}"
            self.current_run_data["error_details"] = error_tb
            self.update_current_run()
            return False
        except Exception as e:
            import traceback
            error_tb = traceback.format_exc()
            self.logger.error(f"Unexpected error: {e}")
            self.logger.error(f"Error traceback:\n{error_tb}")

            # Log specific error context
            self.logger.error(f"Error occurred at turn: {self.current_run_data.get('turn_count', 'unknown')}")
            self.logger.error(f"Current location: {self.game.current_location if hasattr(self.game, 'current_location') else 'unknown'}")
            self.logger.error(f"Active characters: {[p.name for p in self.game.players if hasattr(p, 'alive') and p.alive] if hasattr(self.game, 'players') else 'unknown'}")

            self.current_run_data["status"] = "error"
            self.current_run_data["conclusion"] = f"The adventure ended unexpectedly due to an error: {e}"
            self.current_run_data["error_details"] = error_tb
            self.update_current_run()
            return False

    def run_game(self, max_turns: int = 10) -> bool:
        """
        Complete game workflow from initialization to conclusion.

        Args:
            max_turns: Maximum number of turns to run

        Returns:
            True if game completed successfully, False otherwise
        """
        try:
            # Initialize the run
            self.initialize_run()

            # Initialize the game
            self.initialize_game()

            # Ensure journal directories exist
            journal_dir = os.path.join(self.vault_path, "Journals")
            entries_dir = os.path.join(journal_dir, "Entries")
            thoughts_dir = os.path.join(journal_dir, "Thoughts")

            os.makedirs(journal_dir, exist_ok=True)
            os.makedirs(entries_dir, exist_ok=True)
            os.makedirs(thoughts_dir, exist_ok=True)
            self.logger.info("Ensured journal directories exist")

            # Run the game loop
            success = self.run_game_loop(max_turns)

            self.logger.info("\nGame completed. Check your Obsidian vault for the adventure log.")
            return success

        except Exception as e:
            import traceback
            error_tb = traceback.format_exc()
            self.logger.error(f"Critical error running game: {e}")
            self.logger.error(f"Error traceback:\n{error_tb}")

            # Log specific details about the error context
            self.logger.error(f"Error context - Current run ID: {self.current_run_id}")
            self.logger.error(f"Error context - Game state: {self.game.__dict__ if hasattr(self, 'game') else 'Game not initialized'}")

            if self.current_run_data:
                self.current_run_data["status"] = "error"
                self.current_run_data["conclusion"] = f"The adventure ended unexpectedly due to a critical error: {e}"
                self.current_run_data["error_details"] = error_tb
                self.update_current_run()
            return False

    def handle_character_death(self, character_name: str, cause: str) -> None:
        """
        Handle the death of a character, updating all necessary records.

        Args:
            character_name: Name of the character who died
            cause: Cause of death
        """
        # Update character status
        status_update = {
            "status": "Dead",
            "alive": False,
            "status_summary": f"Dead - {cause}"
        }
        self.obsidian.update_character_status_with_event(character_name, status_update, self.event_manager)

        # Create a death event
        death_event = {
            "name": f"Death {character_name}",
            "type": "Character Death",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": self.game.current_location,
            "summary": f"{character_name} has died",
            "description": cause,
            "participants": [character_name],
            "related_quests": ["Main Quest"]  # Add Main Quest by default
        }
        self.obsidian.log_event_with_event(death_event, self.event_manager)

        self.logger.info(f"Character death processed: {character_name} - {cause}")

    def process_location_change(self, character_name: str, new_location: str, description: str = None) -> None:
        """
        Process a character changing location, updating all necessary records.

        Args:
            character_name: Name of the character who is moving
            new_location: Name of the new location
            description: Optional description of the movement
        """
        # Get current location
        old_location = None
        for player in self.game.players:
            if player.name == character_name:
                if hasattr(player, 'location'):
                    old_location = player.location
                # Update player location
                player.location = new_location
                break

        # Handle movement in the game manager
        self.game_manager.handle_character_movement(character_name, old_location, new_location)

        # Update the old location file to remove this character
        if old_location:
            # Get all characters at the old location excluding the moving character
            characters_at_old_location = [
                p.name for p in self.game.players
                if hasattr(p, 'location') and p.location == old_location and p.name != character_name
            ]

            old_location_data = {
                "name": old_location,
                "characters": characters_at_old_location
            }
            self.obsidian.log_location_with_event(old_location_data, self.event_manager)
            self.logger.info(f"Updated old location {old_location} after {character_name} left")

        # Update the new location file to add this character
        # Get all characters at the new location including the moving character
        characters_at_new_location = [
            p.name for p in self.game.players
            if hasattr(p, 'location') and p.location == new_location
        ]

        new_location_data = {
            "name": new_location,
            "characters": characters_at_new_location
        }
        self.obsidian.log_location_with_event(new_location_data, self.event_manager)
        self.logger.info(f"Updated new location {new_location} after {character_name} arrived")

        # Create a movement event if description provided
        if description:
            movement_event = {
                "name": f"Movement {character_name} {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "Movement",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": new_location,
                "summary": f"{character_name} travels to {new_location}",
                "description": description,
                "participants": [character_name],
                "related_quests": ["Main Quest"]  # Add Main Quest by default
            }
            self.obsidian.log_event_with_event(movement_event, self.event_manager)

        self.logger.info(f"Location change processed: {character_name} moved from {old_location} to {new_location}")

    def archive_current_run(self) -> None:
        """Archive the current run in the Runs/Archived directory."""
        if not self.current_run_id:
            self.logger.warning("No current run to archive")
            return

        # This would call functionality from reset_game.py
        # For now, just log that we would archive
        self.logger.info(f"Would archive run {self.current_run_id} here")


# Allow direct execution for testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Test the DungeonMaster
    dm = DungeonMaster()
    dm.run_game(max_turns=5)
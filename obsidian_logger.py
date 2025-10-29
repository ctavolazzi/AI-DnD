import os
import re
import logging
import datetime
import jinja2
from typing import Dict, List, Any, Optional, Union

class ObsidianLogger:
    """
    A class for logging game events, characters, locations, etc. to an Obsidian vault.
    Creates and updates markdown files with proper Obsidian-style [[internal links]].
    """

    def __init__(self, vault_path: str = "ai-dnd-test-vault"):
        """
        Initialize the Obsidian logger.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = vault_path
        self.logger = logging.getLogger("obsidian_logger")

        # Set up directories
        self.directories = {
            "characters": os.path.join(vault_path, "Characters"),
            "locations": os.path.join(vault_path, "Locations"),
            "events": os.path.join(vault_path, "Events"),
            "sessions": os.path.join(vault_path, "Sessions"),
            "quests": os.path.join(vault_path, "Quests"),
            "items": os.path.join(vault_path, "Items"),
            "runs": os.path.join(vault_path, "Runs"),
            "journals": os.path.join(vault_path, "Journals")
        }

        # Create directories if they don't exist
        for directory in self.directories.values():
            os.makedirs(directory, exist_ok=True)

        # Create subdirectories for journal entries and thoughts
        os.makedirs(os.path.join(self.directories["journals"], "Entries"), exist_ok=True)
        os.makedirs(os.path.join(self.directories["journals"], "Thoughts"), exist_ok=True)

        # Set up Jinja2 environment for templating
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Ensure the index file exists
        index_path = os.path.join(vault_path, "Index.md")
        if not os.path.exists(index_path):
            with open(index_path, 'w') as f:
                f.write("# Game Index\n\nThis file serves as an index for your game content.")

        # Create central reference files if they don't exist
        self._create_central_reference_files()

    def _sanitize_filename(self, name: str) -> str:
        """
        Convert a string to a valid filename.

        Args:
            name: The string to convert

        Returns:
            A sanitized filename
        """
        # Remove invalid characters but preserve spaces
        sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
        return sanitized

    def _create_internal_link(self, text: str, target: Optional[str] = None) -> str:
        """
        Create an Obsidian internal link.

        Args:
            text: The display text
            target: The target file (if different from text)

        Returns:
            An Obsidian internal link string [[target|text]] or [[text]]
        """
        if target and target != text:
            return f"[[{target}|{text}]]"
        return f"[[{text}]]"

    def _update_index(self):
        """Update the main index file of the vault."""
        index_path = os.path.join(self.vault_path, "Index.md")

        content = "# AI-DnD Game Index\n\n"
        content += f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Add sections for each category
        categories = {
            "Characters": "Characters encountered in the game",
            "Locations": "Places visited in the game world",
            "Events": "Notable events that have occurred",
            "Sessions": "Game sessions and summaries",
            "Quests": "Active and completed quests",
            "Items": "Items discovered during gameplay",
            "Journals": "Character journals and internal thoughts"
        }

        for category, description in categories.items():
            content += f"## {category}\n\n"
            content += f"{description}\n\n"

            # Get all files in this category and create links
            dir_path = self.directories[category.lower()]
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith('.md')]

                if files:
                    for file in sorted(files):
                        # Remove .md extension for the link text
                        link_text = file[:-3]
                        content += f"- {self._create_internal_link(link_text)}\n"
                else:
                    content += "No entries yet.\n"

            content += "\n"

        with open(index_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Updated index file at {index_path}")

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.

        Args:
            template_name: The name of the template file (without extension)
            context: The context data to render the template with

        Returns:
            The rendered template string
        """
        try:
            template = self.jinja_env.get_template(f"{template_name}.md")
            return template.render(**context)
        except jinja2.exceptions.TemplateNotFound:
            self.logger.warning(f"Template {template_name}.md not found. Using fallback.")
            return f"# {context.get('name', 'Untitled')}\n\n{context.get('description', '')}"
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            return f"# {context.get('name', 'Error')}\n\nError rendering template: {e}"

    def _create_central_reference_files(self):
        """
        Create central reference files for each entity type if they don't exist.
        These files serve as indices for each entity type.
        """
        reference_files = {
            "characters": "Characters.md",
            "locations": "Locations.md",
            "events": "Events.md",
            "sessions": "Sessions.md",
            "quests": "Quests.md",
            "items": "Items.md"
        }

        for entity_type, filename in reference_files.items():
            filepath = os.path.join(self.directories[entity_type], filename)
            if not os.path.exists(filepath):
                self.logger.info(f"Creating central reference file for {entity_type}: {filepath}")

                # Create basic template for central reference file
                content = f"""---
title: {entity_type.capitalize()}
created: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# {entity_type.capitalize()}

This is the central reference file for all {entity_type} in the game. This file is automatically updated when new {entity_type} are created or existing {entity_type} are modified.

## List of {entity_type.capitalize()}

*This section will be automatically populated as {entity_type} are created.*

## Tags
#{entity_type} #reference
"""
                with open(filepath, 'w') as f:
                    f.write(content)

    def _update_central_reference_file(self, entity_type: str, entity_name: str, action: str = "added"):
        """
        Update the central reference file for an entity type when a new entity is created or updated.

        Args:
            entity_type: Type of entity (characters, locations, etc.)
            entity_name: Name of the entity
            action: Action performed on the entity (added, updated, removed)
        """
        if entity_type not in self.directories:
            self.logger.warning(f"Unknown entity type: {entity_type}")
            return

        reference_file = os.path.join(self.directories[entity_type], f"{entity_type.capitalize()}.md")

        if not os.path.exists(reference_file):
            self.logger.warning(f"Central reference file for {entity_type} not found, creating it")
            self._create_central_reference_files()

        try:
            # Read current content
            with open(reference_file, 'r') as f:
                content = f.read()

            # Update the "updated" timestamp in frontmatter
            content = re.sub(
                r"updated: .*",
                f"updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                content
            )

            # Check if entity is already listed
            entity_link = self._create_internal_link(entity_name)
            list_section = f"## List of {entity_type.capitalize()}"

            if list_section in content:
                # Find the section
                section_pattern = f"{list_section}.*?(?=^#|$)"
                section_match = re.search(section_pattern, content, re.DOTALL | re.MULTILINE)

                if section_match:
                    section_content = section_match.group(0)

                    # Check if entity is already in the list
                    if entity_link in section_content:
                        # Entity already exists, nothing to do if just updating the list
                        pass
                    else:
                        # Add entity to the list
                        new_section_content = section_content.replace(
                            "*This section will be automatically populated as",
                            f"- {entity_link} - Added on {datetime.datetime.now().strftime('%Y-%m-%d')}\n*This section will be automatically populated as"
                        )

                        if new_section_content == section_content:  # No placeholder text found
                            # Add to the end of the section
                            new_line = f"\n- {entity_link} - Added on {datetime.datetime.now().strftime('%Y-%m-%d')}"
                            new_section_content = section_content + new_line

                        content = content.replace(section_content, new_section_content)

            # Write updated content
            with open(reference_file, 'w') as f:
                f.write(content)

            self.logger.info(f"Updated central reference file for {entity_type} with {entity_name}")

        except Exception as e:
            self.logger.error(f"Error updating central reference file for {entity_type}: {e}")

    def log_character(self, character_data: Dict[str, Any]):
        """
        Log a character to the vault.

        Args:
            character_data: Dictionary with character information
        """
        name = character_data.get("name", "Unknown Character")
        file_name = self._sanitize_filename(name)
        file_path = os.path.join(self.directories["characters"], f"{file_name}.md")

        # Prepare context with defaults for template
        character_context = character_data.copy()

        # Add default values for template fields if not present
        if "status" not in character_context:
            character_context["status"] = "Active" if character_context.get("alive", True) else "Dead"

        if "status_summary" not in character_context:
            hp = character_context.get("hp", 0)
            max_hp = character_context.get("max_hp", 0)
            status = character_context.get("status", "Unknown")
            character_context["status_summary"] = f"{status} - HP: {hp}/{max_hp}"

        if "bio" not in character_context:
            character_context["bio"] = "No biography available yet."

        # Render character file content using the template
        content = self._render_template("Character", character_context)

        # Write to file
        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Logged character: {name} to {file_path}")

        # Update index
        self._update_index()

        # Update the central reference file
        self._update_central_reference_file("characters", character_data["name"], "added")

        return name

    def log_location(self, location_data: Dict[str, Any]):
        """
        Log a location to the vault.

        Args:
            location_data: Dictionary with location information
        """
        if not location_data:
            self.logger.warning("Empty location data provided to log_location")
            return None

        name = location_data.get("name", "Unknown Location")
        if not name or name == "Unknown Location":
            self.logger.warning(f"Missing or invalid location name: {name}")
            # Still proceed but with a warning

        file_name = self._sanitize_filename(name)
        file_path = os.path.join(self.directories["locations"], f"{file_name}.md")

        # Prepare context with defaults for template
        location_context = location_data.copy()

        # Add default values for template fields if not present
        if "type" not in location_context:
            location_context["type"] = "Location"

        if "discovered_date" not in location_context:
            location_context["discovered_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "overview" not in location_context:
            location_context["overview"] = location_context.get("description", "No details available.")

        if "notes" not in location_context:
            location_context["notes"] = "No additional notes."

        # Include characters present if available
        if "characters" not in location_context and location_data.get("name"):
            # If game_manager is accessible, we could get characters present
            # Currently, we'll use any provided in the location_data
            location_context["characters"] = location_data.get("characters", [])

        try:
            # Render location file content using the template
            content = self._render_template("Location", location_context)

            # Write to file
            with open(file_path, 'w') as f:
                f.write(content)

            self.logger.info(f"Logged location: {name} to {file_path}")

            # Update index
            self._update_index()

            # Update the central reference file
            self._update_central_reference_file("locations", location_data["name"], "added")

            return name
        except Exception as e:
            self.logger.error(f"Error logging location {name}: {e}")
            return None

    def log_event(self, event_data: Dict[str, Any]):
        """
        Log an event to the vault.

        Args:
            event_data: Dictionary with event information
        """
        name = event_data.get("name", "Unknown Event")
        file_name = self._sanitize_filename(name)
        file_path = os.path.join(self.directories["events"], f"{file_name}.md")

        # Prepare context with defaults for template
        event_context = event_data.copy()

        # Add default values for template fields if not present
        if "type" not in event_context:
            event_context["type"] = "General"

        if "timestamp" not in event_context:
            event_context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "location" not in event_context:
            event_context["location"] = "Unknown Location"

        if "summary" not in event_context and "description" in event_context:
            # Generate a summary from the description if available
            description = event_context["description"]
            event_context["summary"] = description[:100] + "..." if len(description) > 100 else description
        elif "summary" not in event_context:
            event_context["summary"] = "No summary available."

        if "description" not in event_context and "summary" in event_context:
            event_context["description"] = event_context["summary"]
        elif "description" not in event_context:
            event_context["description"] = "No detailed description available."

        # Render event file content using the template
        content = self._render_template("Event", event_context)

        # Write to file
        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Logged event: {name} to {file_path}")

        # Update index
        self._update_index()

        # Update references in related entities
        if "location" in event_context:
            self._add_reference_to_entity(
                "locations",
                event_context["location"],
                "events",
                name,
                event_context.get("summary", "Event occurred here")
            )

        if "participants" in event_context:
            for participant in event_context["participants"]:
                self._add_reference_to_entity(
                    "characters",
                    participant,
                    "events",
                    name,
                    event_context.get("summary", "Participated in this event")
                )

        # Update the central reference file
        self._update_central_reference_file("events", event_data["name"], "added")

        return name

    def log_session(self, session_data: Dict[str, Any]):
        """
        Log a game session to the vault.

        Args:
            session_data: Dictionary with session information
        """
        name = session_data.get("name", "Session")
        file_name = self._sanitize_filename(name)
        file_path = os.path.join(self.directories["sessions"], f"{file_name}.md")

        # Prepare context with defaults for template
        session_context = session_data.copy()

        # Add default values for template fields if not present
        if "date" not in session_context:
            session_context["date"] = datetime.datetime.now().strftime("%Y-%m-%d")

        if "summary" not in session_context:
            session_context["summary"] = "No summary available."

        if "run_id" not in session_context:
            session_context["run_id"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        if "next_steps" not in session_context:
            session_context["next_steps"] = "The adventure continues..."

        # Render session file content using the template
        content = self._render_template("Session", session_context)

        # Write to file
        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Logged session: {name} to {file_path}")

        # Update index
        self._update_index()

        # Update the central reference file
        self._update_central_reference_file("sessions", session_data["name"], "added")

        return name

    def log_skill_check(self, check_data: Dict[str, Any], event_manager=None):
        """
        Log a skill check as an event.

        Args:
            check_data: Dictionary with skill check information
            event_manager: Optional event manager for tracking
        """
        character = check_data.get("character", "Unknown")
        ability = check_data.get("ability", "")
        skill = check_data.get("skill", "")
        total = check_data.get("total", 0)
        dc = check_data.get("dc", 0)
        success = check_data.get("success", False)

        # Create skill check description
        skill_str = f"{skill} ({ability})" if skill else ability
        result_str = "SUCCESS" if success else "FAILURE"

        event_data = {
            "name": f"Skill Check: {character} - {skill_str}",
            "type": "Skill Check",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": f"{character} makes a {skill_str} check",
            "description": f"{character} rolled {total} vs DC {dc}: {result_str}",
            "participants": [character],
            "result": result_str,
            "check_details": check_data
        }

        if event_manager:
            self.log_event_with_event(event_data, event_manager)
        else:
            self.log_event(event_data)

        return event_data

    def log_quest(self, quest_data: Dict[str, Any]):
        """
        Log a quest to the vault.

        Args:
            quest_data: Dictionary with quest information
        """
        name = quest_data.get("name", "Unknown Quest")
        file_name = self._sanitize_filename(name)
        file_path = os.path.join(self.directories["quests"], f"{file_name}.md")

        # Prepare context with defaults for template
        quest_context = quest_data.copy()

        # Add default values for template fields if not present
        if "difficulty" not in quest_context:
            quest_context["difficulty"] = "Medium"

        if "status" not in quest_context:
            quest_context["status"] = "Active"

        if "start_date" not in quest_context:
            quest_context["start_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "overview" not in quest_context:
            quest_context["overview"] = quest_context.get("description", "No details available.")

        if "notes" not in quest_context:
            quest_context["notes"] = "No additional notes."

        # Make sure objectives are in the right format
        if "objectives" in quest_context and isinstance(quest_context["objectives"], list):
            formatted_objectives = []
            for obj in quest_context["objectives"]:
                if isinstance(obj, str):
                    formatted_objectives.append({"description": obj, "completed": False})
                elif isinstance(obj, dict) and "description" in obj:
                    if "completed" not in obj:
                        obj["completed"] = False
                    formatted_objectives.append(obj)
            quest_context["objectives"] = formatted_objectives

        # Render quest file content using the template
        content = self._render_template("Quest", quest_context)

        # Write to file
        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Logged quest: {name} to {file_path}")

        # Update index
        self._update_index()

        # Update the central reference file
        self._update_central_reference_file("quests", quest_data["name"], "added")

        return name

    def log_item(self, item_data: Dict[str, Any]):
        """
        Log an item to the vault.

        Args:
            item_data: Dictionary with item information
        """
        name = item_data.get("name", "Unknown Item")
        file_name = self._sanitize_filename(name)
        file_path = os.path.join(self.directories["items"], f"{file_name}.md")

        # Prepare context with defaults for template
        item_context = item_data.copy()

        # Add default values for template fields if not present
        if "type" not in item_context:
            item_context["type"] = "Miscellaneous"

        if "rarity" not in item_context:
            item_context["rarity"] = "Common"

        if "discovered_date" not in item_context:
            item_context["discovered_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "value" not in item_context:
            item_context["value"] = "Unknown"

        if "description" not in item_context:
            item_context["description"] = "No description available."

        if "notes" not in item_context:
            item_context["notes"] = "No additional notes."

        # Render item file content using the template
        content = self._render_template("Item", item_context)

        # Write to file
        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Logged item: {name} to {file_path}")

        # Update index
        self._update_index()

        # Update the central reference file
        self._update_central_reference_file("items", item_data["name"], "added")

        return name

    def log_combat(self, combat_data: Dict[str, Any]):
        """
        Log a combat encounter to the vault.

        Args:
            combat_data: Dictionary with combat information
        """
        name = combat_data.get("name", "Combat")
        file_name = self._sanitize_filename(name)
        # Combat events are stored as regular events
        file_path = os.path.join(self.directories["events"], f"{file_name}.md")

        # Prepare context with defaults for template
        combat_context = combat_data.copy()

        # Add default values for template fields if not present
        if "timestamp" not in combat_context:
            combat_context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "location" not in combat_context:
            combat_context["location"] = "Unknown Location"

        if "overview" not in combat_context:
            combat_context["overview"] = combat_context.get("description", "A combat encounter.")

        if "outcome" not in combat_context:
            combat_context["outcome"] = "Combat in progress..."

        # Render combat file content using the template
        content = self._render_template("Combat", combat_context)

        # Write to file
        with open(file_path, 'w') as f:
            f.write(content)

        self.logger.info(f"Logged combat: {name} to {file_path}")

        # Update references in related entities
        if "location" in combat_context:
            self._add_reference_to_entity(
                "locations",
                combat_context["location"],
                "events",
                name,
                "Combat occurred here"
            )

        if "player_team" in combat_context:
            for character in combat_context["player_team"]:
                self._add_reference_to_entity(
                    "characters",
                    character,
                    "events",
                    name,
                    "Participated in this combat"
                )

        # Update index
        self._update_index()

        # Update the central reference file
        self._update_central_reference_file("events", combat_data["name"], "added")

        return name

    def update_character_status(self, character_name: str, new_status: Dict[str, Any]):
        """
        Update the status of a character.

        Args:
            character_name: Name of the character
            new_status: Dictionary with updated status information

        Returns:
            True if the character was updated, False otherwise
        """
        file_name = self._sanitize_filename(character_name)
        file_path = os.path.join(self.directories["characters"], f"{file_name}.md")

        if not os.path.exists(file_path):
            self.logger.error(f"Cannot update status: Character file for {character_name} not found")
            return False

        try:
            # Read the existing character file to get its content
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract YAML frontmatter
            frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                self.logger.error(f"Cannot update status: Character file for {character_name} has no valid frontmatter")
                return False

            # Parse current character data from the file
            character_context = {}
            # Try to extract data with regex
            for line in frontmatter_match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    character_context[key.strip()] = value.strip()

            # Add any sections we want to preserve manually (not ideal, but workable for simple updates)
            # For example, extract character actions/history
            actions_match = re.search(r'## History\n\n(.*?)(?=\n\n##|\Z)', content, re.DOTALL)
            if actions_match:
                actions_text = actions_match.group(1)
                actions = []
                for line in actions_text.strip().split('\n'):
                    if line.startswith('- '):
                        actions.append(line[2:])  # Remove the bullet point
                character_context["actions"] = actions

            # Update character context with new status
            for key, value in new_status.items():
                character_context[key] = value

            # Add a new action if combat_action is present
            if "combat_action" in new_status:
                if "actions" not in character_context:
                    character_context["actions"] = []
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                character_context["actions"].insert(0, f"[{timestamp}] {new_status['combat_action']}")

            # Ensure we have a name
            character_context["name"] = character_name

            # Render updated character file
            updated_content = self._render_template("Character", character_context)

            # Write updated content
            with open(file_path, 'w') as f:
                f.write(updated_content)

            self.logger.info(f"Updated status for character {character_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating character status: {e}")
            return False

    def _add_reference_to_entity(self, entity_type: str, entity_name: str,
                               reference_type: str, reference_name: str, description: str = ""):
        """
        Add a reference to another entity in the entity's file.
        Used for bidirectional linking between entities.

        Args:
            entity_type: Type of entity (characters, locations, etc.)
            entity_name: Name of the entity to add the reference to
            reference_type: Type of reference (events, characters, etc.)
            reference_name: Name of the referenced entity
            description: Optional description of the relationship
        """
        # Check if directory exists
        if entity_type not in self.directories:
            self.logger.warning(f"Unknown entity type: {entity_type}")
            return False

        # Get the entity file path
        filename = self._sanitize_filename(entity_name) + ".md"
        filepath = os.path.join(self.directories[entity_type], filename)

        if not os.path.exists(filepath):
            self.logger.warning(f"Entity file does not exist: {filepath}")
            return False

        # Read the current content
        with open(filepath, 'r') as f:
            content = f.read()

        # Define the section title based on reference type
        if reference_type == "events":
            section_title = "## Events"
            if entity_type == "characters":
                section_title = "## Relationships"
        elif reference_type == "characters":
            section_title = "## Related Characters"
        elif reference_type == "locations":
            section_title = "## Related Locations"
        else:
            section_title = f"## Related {reference_type.title()}"

        # Check if the section exists
        if section_title in content:
            # Section exists, find it and add the reference
            section_pattern = f"{section_title}\n\n(.*?)(?=\n\n##|\Z)"
            match = re.search(section_pattern, content, re.DOTALL)

            if match:
                # Check if reference already exists
                if self._create_internal_link(reference_name) in match.group(1):
                    # Reference already exists, don't duplicate
                    return True

                # Add the reference to the existing section
                existing_section = match.group(1)
                ref_link = self._create_internal_link(reference_name)

                if description:
                    new_section = f"{existing_section}- {ref_link}: {description}\n"
                else:
                    new_section = f"{existing_section}- {ref_link}\n"

                # Replace the existing section with the updated one
                updated_content = re.sub(section_pattern, f"{section_title}\n\n{new_section}", content, flags=re.DOTALL)
            else:
                # This shouldn't happen, but handle it anyway
                self.logger.warning(f"Failed to find section content for {section_title}")
                return False
        else:
            # Section doesn't exist, add it at the end
            ref_link = self._create_internal_link(reference_name)

            if description:
                new_section = f"\n\n{section_title}\n\n- {ref_link}: {description}\n"
            else:
                new_section = f"\n\n{section_title}\n\n- {ref_link}\n"

            # Add the new section to the end
            updated_content = content + new_section

        # Write the updated content back to the file
        with open(filepath, 'w') as f:
            f.write(updated_content)

        self.logger.info(f"Added reference to {reference_name} in {entity_name}")
        return True

    def update_quest_objective(self, quest_name: str, objective_index: int, completed: bool = True):
        """
        Update the status of a quest objective.

        Args:
            quest_name: Name of the quest
            objective_index: Index of the objective to update (0-based)
            completed: Whether the objective is completed

        Returns:
            True if the objective was updated, False otherwise
        """
        file_name = self._sanitize_filename(quest_name)
        file_path = os.path.join(self.directories["quests"], f"{file_name}.md")

        if not os.path.exists(file_path):
            self.logger.error(f"Cannot update objective: Quest file for {quest_name} not found")
            return False

        try:
            # Read the existing quest file to get its content
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract YAML frontmatter
            frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                self.logger.error(f"Cannot update objective: Quest file for {quest_name} has no valid frontmatter")
                return False

            # Parse current quest data from the file
            quest_context = {}
            # Try to extract data with regex - not ideal but workable for simple updates
            for line in frontmatter_match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    quest_context[key.strip()] = value.strip()

            # Read objectives section to extract current objectives
            objectives_match = re.search(r'## Objectives\n\n(.*?)(?=\n\n##|\Z)', content, re.DOTALL)
            if objectives_match:
                objectives_text = objectives_match.group(1)
                # Parse objectives from text
                objectives = []
                for line in objectives_text.strip().split('\n'):
                    if line.startswith('- '):
                        if '✅' in line or '⬜' in line:
                            obj_text = line[line.find('] ') + 2:].strip()
                            obj_completed = '✅' in line
                            objectives.append({"description": obj_text, "completed": obj_completed})

                # Update the objective if index is valid
                if 0 <= objective_index < len(objectives):
                    objectives[objective_index]["completed"] = completed

                    # Create updated quest context
                    updated_quest_context = {
                        "name": quest_name,
                        "objectives": objectives,
                        # Add other fields from frontmatter
                        **quest_context
                    }

                    # Render updated quest file
                    updated_content = self._render_template("Quest", updated_quest_context)

                    # Write updated content
                    with open(file_path, 'w') as f:
                        f.write(updated_content)

                    self.logger.info(f"Updated objective {objective_index} for quest {quest_name}")
                    return True
                else:
                    self.logger.error(f"Objective index {objective_index} out of range for quest {quest_name}")
                    return False
            else:
                self.logger.error(f"Cannot find objectives section in quest {quest_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error updating quest objective: {e}")
            return False

    def log_character_with_event(self, character_data, event_manager):
        """Log a character and publish an event for real-time updates."""
        self.log_character(character_data)
        self.logger.info(f"Character logged: {character_data.get('name')}, publishing event for real-time update")
        event_manager.publish("character_created", character_data)

    def log_location_with_event(self, location_data, event_manager):
        """Log a location and publish an event for real-time updates."""
        self.log_location(location_data)
        self.logger.info(f"Location logged: {location_data.get('name')}, publishing event for real-time update")
        event_manager.publish("location_created", location_data)

    def log_event_with_event(self, event_data, event_manager):
        """Log an event and publish an event for real-time updates."""
        self.log_event(event_data)
        self.logger.info(f"Event logged: {event_data.get('name')}, publishing event for real-time update")
        event_manager.publish("event_occurred", event_data)

    def log_quest_with_event(self, quest_data, event_manager):
        """Log a quest and publish an event for real-time updates."""
        self.log_quest(quest_data)
        self.logger.info(f"Quest logged: {quest_data.get('name')}, publishing event for real-time update")
        event_manager.publish("quest_created", quest_data)

    def log_item_with_event(self, item_data, event_manager):
        """Log an item and publish an event for real-time updates."""
        self.log_item(item_data)
        self.logger.info(f"Item logged: {item_data.get('name')}, publishing event for real-time update")
        event_manager.publish("item_created", item_data)

    def log_combat_with_event(self, combat_data, event_manager):
        """Log a combat and publish an event for real-time updates."""
        self.log_combat(combat_data)
        self.logger.info(f"Combat logged: {combat_data.get('name')}, publishing event for real-time update")
        event_manager.publish("combat_started", combat_data)

    def log_session_with_event(self, session_data, event_manager):
        """Log a session and publish an event for real-time updates."""
        self.log_session(session_data)
        self.logger.info(f"Session logged: {session_data.get('name')}, publishing event for real-time update")
        event_manager.publish("session_created", session_data)

    def update_character_status_with_event(self, character_name, new_status, event_manager):
        """Update a character's status and publish an event for real-time updates."""
        self.update_character_status(character_name, new_status)

        # Construct character_data from new_status for the event
        character_data = {"name": character_name}
        character_data.update(new_status)

        if new_status.get("alive") is False:
            event_manager.publish("character_died", character_data)
        else:
            event_manager.publish("character_updated", character_data)

    def update_quest_objective_with_event(self, quest_name, objective_index, completed, event_manager):
        """Update a quest objective and publish an event for real-time updates."""
        self.update_quest_objective(quest_name, objective_index, completed)

        # Read the quest file to get updated data
        quest_path = os.path.join(self.vault_path, "Quests", self._sanitize_filename(quest_name) + ".md")
        if not os.path.exists(quest_path):
            return False

        # We need to extract quest data from the file, or ideally we'd have a method to get quest data
        # For now, we'll just create a simple event
        quest_data = {
            "name": quest_name,
            "objective_update": {
                "index": objective_index,
                "completed": completed
            }
        }

        event_manager.publish("quest_updated", quest_data)

    # ===== BIDIRECTIONAL SYNC METHODS =====

    def read_character_from_vault(self, character_name: str) -> Optional[Dict[str, Any]]:
        """
        Read character data from Obsidian vault.

        Args:
            character_name: Name of the character to read

        Returns:
            Dictionary with character data, or None if not found
        """
        file_name = self._sanitize_filename(character_name)
        file_path = os.path.join(self.directories["characters"], f"{file_name}.md")

        if not os.path.exists(file_path):
            self.logger.warning(f"Character file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract YAML frontmatter
            frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                self.logger.error(f"No frontmatter found in character file: {file_path}")
                return None

            # Parse frontmatter
            character_data = {}
            for line in frontmatter_match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    # Convert numeric values
                    if value.isdigit():
                        character_data[key] = int(value)
                    elif value.lower() in ['true', 'false']:
                        character_data[key] = value.lower() == 'true'
                    else:
                        character_data[key] = value

            # Extract additional data from content
            character_data["name"] = character_name

            # Map template field names to expected field names
            if "class" in character_data:
                character_data["char_class"] = character_data["class"]

            # Extract HP from status_summary if available
            if "status_summary" in character_data:
                hp_match = re.search(r'HP: (\d+)/(\d+)', character_data["status_summary"])
                if hp_match:
                    character_data["hp"] = int(hp_match.group(1))
                    character_data["max_hp"] = int(hp_match.group(2))

            self.logger.info(f"Successfully read character from vault: {character_name}")
            return character_data

        except Exception as e:
            self.logger.error(f"Error reading character from vault: {e}")
            return None

    def read_quest_from_vault(self, quest_name: str) -> Optional[Dict[str, Any]]:
        """
        Read quest data from Obsidian vault.

        Args:
            quest_name: Name of the quest to read

        Returns:
            Dictionary with quest data, or None if not found
        """
        file_name = self._sanitize_filename(quest_name)
        file_path = os.path.join(self.directories["quests"], f"{file_name}.md")

        if not os.path.exists(file_path):
            self.logger.warning(f"Quest file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract YAML frontmatter
            frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                self.logger.error(f"No frontmatter found in quest file: {file_path}")
                return None

            # Parse frontmatter
            quest_data = {}
            for line in frontmatter_match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    # Convert numeric values
                    if value.isdigit():
                        quest_data[key] = int(value)
                    elif value.lower() in ['true', 'false']:
                        quest_data[key] = value.lower() == 'true'
                    else:
                        quest_data[key] = value

            # Extract objectives from content
            objectives_match = re.search(r'## Objectives\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if objectives_match:
                objectives_text = objectives_match.group(1)
                objectives = []
                for line in objectives_text.strip().split('\n'):
                    if line.startswith('- '):
                        if '✅' in line or '⬜' in line:
                            # Extract text after the checkbox
                            obj_text = line[line.find('✅') + 1:].strip() if '✅' in line else line[line.find('⬜') + 1:].strip()
                            obj_completed = '✅' in line
                            objectives.append({"description": obj_text, "completed": obj_completed})
                quest_data["objectives"] = objectives

            quest_data["name"] = quest_name
            self.logger.info(f"Successfully read quest from vault: {quest_name}")
            return quest_data

        except Exception as e:
            self.logger.error(f"Error reading quest from vault: {e}")
            return None

    def sync_character_to_game(self, character_name: str, game_character) -> bool:
        """
        Sync character data from Obsidian vault to game character object.

        Args:
            character_name: Name of the character to sync
            game_character: Game character object to update

        Returns:
            True if sync was successful, False otherwise
        """
        vault_data = self.read_character_from_vault(character_name)
        if not vault_data:
            return False

        try:
            # Update game character with vault data
            if "hp" in vault_data:
                game_character.hp = vault_data["hp"]
            if "max_hp" in vault_data:
                game_character.max_hp = vault_data["max_hp"]
            if "attack" in vault_data:
                game_character.attack = vault_data["attack"]
            if "defense" in vault_data:
                game_character.defense = vault_data["defense"]
            if "alive" in vault_data:
                game_character.alive = vault_data["alive"]
            if "status_effects" in vault_data:
                game_character.status_effects = vault_data["status_effects"]

            self.logger.info(f"Successfully synced character {character_name} from vault to game")
            return True

        except Exception as e:
            self.logger.error(f"Error syncing character to game: {e}")
            return False

    def sync_game_to_vault(self, game_character) -> bool:
        """
        Sync game character data to Obsidian vault.

        Args:
            game_character: Game character object to sync

        Returns:
            True if sync was successful, False otherwise
        """
        try:
            character_data = {
                "name": game_character.name,
                "char_class": game_character.char_class,
                "hp": game_character.hp,
                "max_hp": game_character.max_hp,
                "attack": game_character.attack,
                "defense": game_character.defense,
                "alive": game_character.alive,
                "status_effects": getattr(game_character, 'status_effects', []),
                "status": "Active" if game_character.alive else "Dead",
                "status_summary": f"{'Active' if game_character.alive else 'Dead'} - HP: {game_character.hp}/{game_character.max_hp}"
            }

            # Update the character in the vault
            self.log_character(character_data)

            self.logger.info(f"Successfully synced character {game_character.name} from game to vault")
            return True

        except Exception as e:
            self.logger.error(f"Error syncing character to vault: {e}")
            return False

    def get_vault_status(self) -> Dict[str, Any]:
        """
        Get current status of the Obsidian vault.

        Returns:
            Dictionary with vault statistics and status
        """
        status = {
            "vault_path": self.vault_path,
            "characters": 0,
            "locations": 0,
            "events": 0,
            "quests": 0,
            "items": 0,
            "sessions": 0,
            "last_updated": None,
            "total_files": 0
        }

        try:
            # Count files in each directory
            for entity_type, directory in self.directories.items():
                if os.path.exists(directory):
                    files = [f for f in os.listdir(directory) if f.endswith('.md')]
                    status[entity_type] = len(files)
                    status["total_files"] += len(files)

            # Find most recently modified file
            latest_time = 0
            for directory in self.directories.values():
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        if file.endswith('.md'):
                            file_path = os.path.join(directory, file)
                            mod_time = os.path.getmtime(file_path)
                            if mod_time > latest_time:
                                latest_time = mod_time

            if latest_time > 0:
                status["last_updated"] = datetime.datetime.fromtimestamp(latest_time).strftime("%Y-%m-%d %H:%M:%S")

            self.logger.info(f"Vault status retrieved: {status['total_files']} total files")
            return status

        except Exception as e:
            self.logger.error(f"Error getting vault status: {e}")
            return status
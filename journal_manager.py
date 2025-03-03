import os
import logging
import datetime
import re
from typing import Dict, List, Any, Optional, Union

class JournalManager:
    """
    Manages character journals and internal thoughts.
    Provides methods to create, update, and retrieve journal entries.
    Uses "theory of mind" concepts to generate realistic internal thoughts.
    """

    def __init__(self, obsidian_logger, knowledge_graph):
        """
        Initialize the journal manager.

        Args:
            obsidian_logger: The ObsidianLogger instance for creating files
            knowledge_graph: The KnowledgeGraph instance for character knowledge
        """
        self.obsidian_logger = obsidian_logger
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger("journal_manager")

        # Ensure journal directories exist
        self.journal_dir = os.path.join(self.obsidian_logger.vault_path, "Journals")
        os.makedirs(self.journal_dir, exist_ok=True)

        # Create directories for each entry type
        self.entry_dirs = {
            "journal": os.path.join(self.journal_dir, "Entries"),
            "thought": os.path.join(self.journal_dir, "Thoughts")
        }

        for directory in self.entry_dirs.values():
            os.makedirs(directory, exist_ok=True)

    def _get_character_journal_path(self, character_name: str) -> str:
        """Get the path to a character's journal file."""
        sanitized_name = self.obsidian_logger._sanitize_filename(character_name)
        return os.path.join(self.journal_dir, f"{sanitized_name}.md")

    def _get_entry_path(self, character_name: str, entry_type: str, timestamp: datetime.datetime) -> str:
        """Get the path to a journal entry or thought file."""
        sanitized_name = self.obsidian_logger._sanitize_filename(character_name)
        date_str = timestamp.strftime("%Y-%m-%d-%H-%M-%S")
        return os.path.join(
            self.entry_dirs[entry_type],
            f"{sanitized_name}-{entry_type}-{date_str}.md"
        )

    def create_character_journal(self, character_data: Any) -> None:
        """
        Create a new journal file for a character.

        Args:
            character_data: The character data (dict or Character instance)
        """
        # Extract character data to ensure consistent format
        char_dict = self.extract_character_data(character_data)
        character_name = char_dict["name"]

        # Create context for template
        context = {
            "character_name": character_name,
            "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "journal_entries": [],
            "internal_thoughts": [],
            "related_events": [],
            "related_characters": [],
            "related_quests": ["Main Quest"]  # Add Main Quest by default
        }

        # Add additional character information
        if "class" in char_dict:
            context["character_class"] = char_dict["class"]
        if "race" in char_dict:
            context["character_race"] = char_dict["race"]
        if "bio" in char_dict:
            context["character_bio"] = char_dict["bio"]

        # Add quests if available in character data
        if "quests" in char_dict and char_dict["quests"]:
            context["related_quests"] = char_dict["quests"]

        # Render the template - remove the .md extension since it's added by _render_template
        journal_content = self.obsidian_logger._render_template("CharacterJournal", context)

        # Write to file
        journal_path = self._get_character_journal_path(character_name)
        with open(journal_path, "w") as f:
            f.write(journal_content)

        self.logger.info(f"Created journal for {character_name}")

        # Create a folder for this character's journal entries
        character_folder = os.path.join(self.journal_dir, self.obsidian_logger._sanitize_filename(character_name))
        os.makedirs(character_folder, exist_ok=True)

        # Add journal to character page
        self._add_journal_link_to_character(character_name)

        # Add character reference to Main Quest
        try:
            self._add_character_to_quest(character_name, "Main Quest")
        except Exception as e:
            self.logger.warning(f"Could not add {character_name} to Main Quest: {e}")

    def _add_character_to_quest(self, character_name: str, quest_name: str) -> None:
        """
        Add a character reference to a quest.

        Args:
            character_name: The name of the character
            quest_name: The name of the quest
        """
        quest_file = os.path.join(
            self.obsidian_logger.vault_path,
            "Quests",
            f"{self.obsidian_logger._sanitize_filename(quest_name)}.md"
        )

        if not os.path.exists(quest_file):
            self.logger.warning(f"Quest file {quest_file} not found")
            return

        try:
            with open(quest_file, 'r') as f:
                content = f.read()

            # Find the Involved Characters section
            char_section_match = re.search(r'## Involved Characters\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if char_section_match:
                char_section = char_section_match.group(1)

                # Check if character is already listed
                char_link = f"[[{character_name}]]"
                if char_link in char_section:
                    return  # Character already in quest

                # If section has "No characters" placeholder, replace it
                if "No characters currently involved" in char_section:
                    new_char_section = f"- {char_link}\n"
                else:
                    # Otherwise add to existing list
                    new_char_section = char_section.strip() + f"\n- {char_link}\n"

                # Replace the section in the content
                updated_content = content.replace(char_section, new_char_section)

                # Write updated content back to file
                with open(quest_file, 'w') as f:
                    f.write(updated_content)

                self.logger.info(f"Added {character_name} to quest {quest_name}")
            else:
                self.logger.warning(f"Could not find Involved Characters section in {quest_name}")
        except Exception as e:
            self.logger.error(f"Error adding character to quest: {e}")

    def _add_journal_link_to_character(self, character_name: str) -> None:
        """Add a link to the journal on the character's page."""
        character_file = os.path.join(
            self.obsidian_logger.directories["characters"],
            f"{self.obsidian_logger._sanitize_filename(character_name)}.md"
        )

        if not os.path.exists(character_file):
            self.logger.warning(f"Character file for {character_name} not found")
            return

        # Read the character file
        with open(character_file, "r") as f:
            content = f.read()

        # Check if journal link already exists
        journal_link = f"[[{character_name}'s Journal]]"
        if journal_link in content:
            return

        # Add journal link to the character file
        if "## Biography" in content:
            content = content.replace(
                "## Biography",
                f"## Journal\n- {journal_link}\n\n## Biography"
            )
        else:
            # Just add to the end if Biography section not found
            content += f"\n\n## Journal\n- {journal_link}\n"

        # Write updated content
        with open(character_file, "w") as f:
            f.write(content)

    def add_journal_entry(self, character_name: str, content: str,
                         related_event: Optional[str] = None,
                         related_characters: List[str] = None,
                         related_locations: List[str] = None,
                         related_quests: List[str] = None,
                         mood: Optional[str] = None) -> None:
        """
        Add a journal entry for a character.

        Args:
            character_name: The name of the character
            content: The content of the journal entry
            related_event: Optional related event name
            related_characters: Optional list of related character names
            related_locations: Optional list of related location names
            related_quests: Optional list of related quest names
            mood: Optional mood of the character
        """
        self._add_entry(
            character_name=character_name,
            content=content,
            entry_type="journal",
            related_event=related_event,
            related_characters=related_characters or [],
            related_locations=related_locations or [],
            related_quests=related_quests or ["Main Quest"],  # Default to Main Quest
            mood=mood
        )

    def add_internal_thought(self, character_name: str, content: str,
                           related_event: Optional[str] = None,
                           related_characters: List[str] = None,
                           related_locations: List[str] = None,
                           related_quests: List[str] = None,
                           mood: Optional[str] = None) -> None:
        """
        Add an internal thought for a character.

        Args:
            character_name: The name of the character
            content: The content of the internal thought
            related_event: Optional related event name
            related_characters: Optional list of related character names
            related_locations: Optional list of related location names
            related_quests: Optional list of related quest names
            mood: Optional mood of the character
        """
        self._add_entry(
            character_name=character_name,
            content=content,
            entry_type="thought",
            related_event=related_event,
            related_characters=related_characters or [],
            related_locations=related_locations or [],
            related_quests=related_quests or ["Main Quest"],  # Default to Main Quest
            mood=mood
        )

    def _add_entry(self, character_name: str, content: str, entry_type: str,
                 related_event: Optional[str] = None,
                 related_characters: List[str] = None,
                 related_locations: List[str] = None,
                 related_quests: List[str] = None,
                 mood: Optional[str] = None) -> None:
        """
        Add a journal entry or internal thought.

        Args:
            character_name: The name of the character
            content: The content of the entry
            entry_type: Either "journal" or "thought"
            related_event: Optional related event name
            related_characters: Optional list of related character names
            related_locations: Optional list of related location names
            related_quests: Optional list of related quest names
            mood: Optional mood of the character
        """
        if entry_type not in ["journal", "thought"]:
            raise ValueError(f"Invalid entry type: {entry_type}")

        timestamp = datetime.datetime.now()

        # Create context for template
        context = {
            "character_name": character_name,
            "entry_date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "entry_type": entry_type,
            "content": content,
            "related_event": related_event,
            "related_characters": related_characters or [],
            "related_locations": related_locations or [],
            "related_quests": related_quests or ["Main Quest"],  # Default to Main Quest
            "mood": mood
        }

        # Render the template - remove the .md extension since it's added by _render_template
        entry_content = self.obsidian_logger._render_template("JournalEntry", context)

        # Write to file
        entry_path = self._get_entry_path(character_name, entry_type, timestamp)
        with open(entry_path, "w") as f:
            f.write(entry_content)

        # Update the character's journal index
        self._update_character_journal(
            character_name=character_name,
            entry_type=entry_type,
            timestamp=timestamp,
            content=content,
            related_event=related_event,
            related_characters=related_characters or [],
            related_quests=related_quests or []
        )

        self.logger.info(f"Added {entry_type} entry for {character_name}")

    def _update_character_journal(self, character_name: str, entry_type: str,
                               timestamp: datetime.datetime, content: str,
                               related_event: Optional[str] = None,
                               related_characters: List[str] = None,
                               related_quests: List[str] = None) -> None:
        """
        Update a character's journal with a new entry.

        Args:
            character_name: The name of the character
            entry_type: Either "journal" or "thought"
            timestamp: The timestamp of the entry
            content: The content of the entry
            related_event: Optional related event name
            related_characters: Optional list of related character names
            related_quests: Optional list of related quest names
        """
        journal_path = self._get_character_journal_path(character_name)

        # Create the journal if it doesn't exist
        if not os.path.exists(journal_path):
            self.create_character_journal({"name": character_name})

        # Read the journal file
        with open(journal_path, "r") as f:
            content_lines = f.readlines()

        # Create new entry
        date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        summary = content.split("\n")[0][:80] + "..." if len(content) > 80 else content
        new_entry = f"### {date_str}\n\n{content}\n\n"

        # Find section to update
        if entry_type == "journal":
            section_header = "## Journal Entries"
            no_entries_marker = "*No journal entries yet*"
        else:  # thought
            section_header = "## Internal Thoughts"
            no_entries_marker = "*No recorded thoughts yet*"

        # Find the section in the file
        section_index = -1
        for i, line in enumerate(content_lines):
            if line.strip() == section_header:
                section_index = i
                break

        if section_index == -1:
            self.logger.error(f"Could not find {section_header} section in journal for {character_name}")
            return

        # Insert the new entry after the section header
        insert_index = section_index + 1

        # If there are no entries yet, remove the placeholder
        if insert_index < len(content_lines) and no_entries_marker in content_lines[insert_index]:
            content_lines.pop(insert_index)

        # Insert the new entry
        content_lines.insert(insert_index, new_entry)

        # Add related event if provided
        if related_event and "## Related Events" in "".join(content_lines):
            event_marker = "*No related events recorded*"
            event_section_index = -1
            for i, line in enumerate(content_lines):
                if line.strip() == "## Related Events":
                    event_section_index = i
                    break

            if event_section_index != -1:
                event_insert_index = event_section_index + 1
                event_link = f"- [[{related_event}]]\n"

                # Check if the event is already listed
                event_already_listed = False
                for i in range(event_insert_index, min(event_insert_index + 10, len(content_lines))):
                    if i < len(content_lines) and related_event in content_lines[i]:
                        event_already_listed = True
                        break

                # If there are no events yet, remove the placeholder
                if event_insert_index < len(content_lines) and event_marker in content_lines[event_insert_index]:
                    content_lines.pop(event_insert_index)

                # Add the event if not already listed
                if not event_already_listed:
                    content_lines.insert(event_insert_index, event_link)

        # Update related characters if provided
        if related_characters and "## Related Characters" in "".join(content_lines):
            char_marker = "*No character connections recorded*"
            char_section_index = -1
            for i, line in enumerate(content_lines):
                if line.strip() == "## Related Characters":
                    char_section_index = i
                    break

            if char_section_index != -1:
                char_insert_index = char_section_index + 1

                # If there are no characters yet, remove the placeholder
                if char_insert_index < len(content_lines) and char_marker in content_lines[char_insert_index]:
                    content_lines.pop(char_insert_index)

                # Add each character that isn't already listed
                for char in related_characters:
                    if char != character_name:  # Don't list the character in their own related characters
                        char_link = f"- [[{char}]]\n"

                        # Check if the character is already listed
                        char_already_listed = False
                        for i in range(char_insert_index, min(char_insert_index + 30, len(content_lines))):
                            if i < len(content_lines) and f"[[{char}]]" in content_lines[i]:
                                char_already_listed = True
                                break

                        # Add the character if not already listed
                        if not char_already_listed:
                            content_lines.insert(char_insert_index, char_link)
                            char_insert_index += 1  # Move insert index after this entry

        # Update related quests if provided
        if related_quests and "## Related Quests" in "".join(content_lines):
            quest_marker = "*No related quests*"
            quest_section_index = -1
            for i, line in enumerate(content_lines):
                if line.strip() == "## Related Quests":
                    quest_section_index = i
                    break

            if quest_section_index != -1:
                quest_insert_index = quest_section_index + 1

                # If there are no quests yet, remove the placeholder
                if quest_insert_index < len(content_lines) and quest_marker in content_lines[quest_insert_index]:
                    content_lines.pop(quest_insert_index)

                # Add each quest that isn't already listed
                for quest in related_quests:
                    quest_link = f"- [[{quest}]]\n"

                    # Check if the quest is already listed
                    quest_already_listed = False
                    for i in range(quest_insert_index, min(quest_insert_index + 20, len(content_lines))):
                        if i < len(content_lines) and f"[[{quest}]]" in content_lines[i]:
                            quest_already_listed = True
                            break

                    # Add the quest if not already listed
                    if not quest_already_listed:
                        content_lines.insert(quest_insert_index, quest_link)
                        quest_insert_index += 1  # Move insert index after this entry

        # Write updated content
        with open(journal_path, "w") as f:
            f.writelines(content_lines)

    def generate_journal_entry(self, character_name: str, event_data: Dict[str, Any]) -> str:
        """
        Generate a journal entry for a character based on an event.

        Args:
            character_name: The name of the character
            event_data: The event data dictionary

        Returns:
            The generated journal entry
        """
        # Try to get character data from the knowledge graph (what the character knows about themselves)
        character_data = {}
        if self.knowledge_graph.entity_knows_about(character_name, character_name):
            character_data = self.knowledge_graph.get_entity_knowledge(character_name, character_name) or {}

        # Extract character attributes for personalization
        char_class = character_data.get("class", "")
        status = character_data.get("status", "")
        abilities = character_data.get("abilities", [])

        event_name = event_data.get("name", "Unknown Event")
        event_description = event_data.get("description", "")
        event_location = event_data.get("location", "")
        event_characters = event_data.get("characters", [])
        event_quests = event_data.get("related_quests", ["Main Quest"])  # Get quest references

        # Filter out the current character from the list
        other_characters = [c for c in event_characters if c != character_name]

        # Create a more personalized journal entry based on character knowledge
        # Check if character knows about other characters using knowledge graph
        known_characters = []
        unknown_characters = []

        for char in other_characters:
            if self.knowledge_graph.entity_knows_about(character_name, char):
                known_characters.append(char)
            else:
                unknown_characters.append(char)

        # Generate a more personalized journal entry
        journal_entry = f"Dear Journal,\n\n"

        # Add character-specific greeting based on class
        if char_class.lower() == "cleric":
            journal_entry = f"By the blessings of the divine,\n\n"
        elif char_class.lower() == "wizard":
            journal_entry = f"Notes of the arcane,\n\n"
        elif char_class.lower() == "fighter":
            journal_entry = f"Battle Log,\n\n"
        elif char_class.lower() == "rogue":
            journal_entry = f"Shadow Records,\n\n"

        journal_entry += f"Today I was involved in an event known as '{event_name}'.\n\n"

        if event_description:
            journal_entry += f"{event_description}\n\n"

        if event_location:
            journal_entry += f"This took place at {event_location}. "

            # Add character's impression of the location if they've been there before
            if self.knowledge_graph.entity_knows_about(character_name, event_location):
                journal_entry += "I've been here before and it feels familiar. "
            else:
                journal_entry += "It's my first time at this place. "

            journal_entry += "\n\n"

        # Add mentions of other characters
        if known_characters:
            if len(known_characters) == 1:
                journal_entry += f"I encountered {known_characters[0]} during this event. We have met before.\n\n"
            else:
                chars_str = ", ".join(known_characters[:-1]) + f" and {known_characters[-1]}"
                journal_entry += f"I encountered {chars_str} during this event. These are people I already know.\n\n"

        if unknown_characters:
            if len(unknown_characters) == 1:
                journal_entry += f"I also met {unknown_characters[0]} for the first time. This is someone new to me.\n\n"
            else:
                chars_str = ", ".join(unknown_characters[:-1]) + f" and {unknown_characters[-1]}"
                journal_entry += f"I also met {chars_str} for the first time. These are new acquaintances.\n\n"

        # Add class-specific reflections
        if char_class.lower() == "fighter":
            journal_entry += "I assessed their combat capabilities. Always good to know who would make a worthy ally in battle.\n\n"
        elif char_class.lower() == "wizard":
            journal_entry += "I observed them carefully, noting any signs of magical aptitude or interesting knowledge they might possess.\n\n"
        elif char_class.lower() == "cleric":
            journal_entry += "I watched for signs of their spiritual convictions and moral character.\n\n"
        elif char_class.lower() == "rogue":
            journal_entry += "I took note of their valuables and potential weaknesses. Old habits die hard.\n\n"

        # Add personal reflection
        journal_entry += f"This event has given me much to think about. I should reflect on what happened and what it means for my future.\n\n"

        # Add quest references
        if event_quests:
            if len(event_quests) == 1:
                journal_entry += f"This relates to my quest: {event_quests[0]}. I should keep this in mind as I proceed.\n\n"
            else:
                quests_str = ", ".join(event_quests[:-1]) + f" and {event_quests[-1]}"
                journal_entry += f"This relates to my quests: {quests_str}. I need to consider how this affects my objectives.\n\n"

        # Class-specific closing
        if char_class.lower() == "cleric":
            journal_entry += "May the light guide my path,\n"
        elif char_class.lower() == "wizard":
            journal_entry += "Until my next revelation,\n"
        elif char_class.lower() == "fighter":
            journal_entry += "Until the next battle,\n"
        elif char_class.lower() == "rogue":
            journal_entry += "Remaining in the shadows,\n"
        else:
            journal_entry += "Until next time,\n"

        journal_entry += f"{character_name}"

        return journal_entry

    def generate_internal_thought(self, character_name: str, event_data: Dict[str, Any]) -> str:
        """
        Generate an internal thought for a character based on an event.

        Args:
            character_name: The name of the character
            event_data: The event data dictionary

        Returns:
            The generated internal thought
        """
        # Try to get character data from the knowledge graph (what the character knows about themselves)
        character_data = {}
        if self.knowledge_graph.entity_knows_about(character_name, character_name):
            character_data = self.knowledge_graph.get_entity_knowledge(character_name, character_name) or {}

        # Extract character attributes for personalization
        char_class = character_data.get("class", "")
        status = character_data.get("status", "")
        abilities = character_data.get("abilities", [])
        status_effects = character_data.get("status_effects", [])

        event_name = event_data.get("name", "Unknown Event")
        event_description = event_data.get("description", "")
        event_location = event_data.get("location", "")
        event_characters = event_data.get("characters", [])
        event_quests = event_data.get("related_quests", ["Main Quest"])  # Get quest references

        # Filter out the current character from the list
        other_characters = [c for c in event_characters if c != character_name]

        # Create a more complex internal thought based on character class and status
        thought = f"*Internal thoughts about {event_name}*\n\n"

        # Add class-specific initial thoughts
        if char_class.lower() == "fighter":
            thought += "I analyze the tactical implications of what just happened. "
            if "Heavy Strike" in abilities:
                thought += "If things had gone poorly, my Heavy Strike ability could have turned the tide.\n\n"
            else:
                thought += "Always be prepared for battle, that's my motto.\n\n"

        elif char_class.lower() == "wizard":
            thought += "I contemplate the arcane implications of these events. "
            if "Fireball" in abilities:
                thought += "There's always the Fireball option if diplomacy fails...\n\n"
            else:
                thought += "Knowledge is power, and I must gather more of it.\n\n"

        elif char_class.lower() == "cleric":
            thought += "I consider what my deity would think of these developments. "
            if "Heal" in abilities:
                thought += "My healing abilities may be needed in the times ahead.\n\n"
            else:
                thought += "I must remain faithful and compassionate in all trials.\n\n"

        elif char_class.lower() == "rogue":
            thought += "I consider the angles and opportunities that might arise from this situation. "
            if "Backstab" in abilities:
                thought += "Always good to know who might deserve a backstab if things go south.\n\n"
            else:
                thought += "Trust is a luxury I rarely afford others.\n\n"

        # Add thoughts based on character status
        if status.lower() == "injured" or (hasattr(character_data, "hp") and character_data["hp"] < character_data.get("max_hp", 100) * 0.5):
            thought += "My wounds ache, reminding me of my mortality. I need to be more careful or find healing soon.\n\n"

        if "stunned" in status_effects:
            thought += "My head is still spinning from being stunned. I need to regain my focus.\n\n"

        # Add personal reactions based on event type
        if "battle" in event_name.lower() or "fight" in event_name.lower():
            thought += "My heart is still racing from the conflict. "
            thought += "The adrenaline hasn't worn off yet, and I find myself mentally replaying every move, wondering if I could have done better.\n\n"

        elif "meeting" in event_name.lower() or "discussion" in event_name.lower():
            thought += "I'm turning over the conversation in my mind, analyzing every word and implication. "
            thought += "Were there hidden meanings I missed? Did I say too much or too little?\n\n"

        elif "journey" in event_name.lower() or "travel" in event_name.lower():
            thought += "The road stretches before and behind me, a symbol of my life's path. "
            thought += "Each step takes me further from what was and closer to what will be.\n\n"

        else:
            thought += "I'm not entirely sure how to feel about what just happened. "
            thought += "Events like these can be difficult to process immediately.\n\n"

        # Add reflections on location
        if event_location:
            if self.knowledge_graph.entity_knows_about(character_name, event_location):
                thought += f"Being back at {event_location} brings back memories. Places hold power over us in ways we don't always acknowledge.\n\n"
            else:
                thought += f"This new place, {event_location}, made quite an impression on me. First impressions matter, and I wonder if I'll return here.\n\n"

        # Add thoughts about other characters
        if other_characters:
            thought += "The people involved in this event occupy my thoughts:\n\n"

            for char in other_characters:
                if self.knowledge_graph.entity_knows_about(character_name, char):
                    # Get what the character knows about this other character
                    knowledge = self.knowledge_graph.get_entity_knowledge(character_name, char)
                    if knowledge:
                        relationship = knowledge.get("relationship", "acquaintance")
                        thought += f"- {char}: We have history together as {relationship}. I wonder how this event will affect our relationship.\n"
                    else:
                        thought += f"- {char}: I recognize them, but realize I don't know them as well as I perhaps should.\n"
                else:
                    thought += f"- {char}: A new face to me. I'm curious about their story and what brought them here.\n"

            thought += "\n"

        # Add deeper reflections and questions
        thought += "Questions that linger in my mind:\n\n"

        # Add class-specific questions
        if char_class.lower() == "fighter":
            thought += "1. How can I use this situation to prove my strength?\n"
            thought += "2. Who among these people would make a worthy ally in battle?\n"
        elif char_class.lower() == "wizard":
            thought += "1. What knowledge can I gain from these circumstances?\n"
            thought += "2. How might arcane forces be influencing these events?\n"
        elif char_class.lower() == "cleric":
            thought += "1. How can I best serve my deity in this situation?\n"
            thought += "2. Who among these people most needs my guidance or healing?\n"
        elif char_class.lower() == "rogue":
            thought += "1. What opportunities for profit might arise from this?\n"
            thought += "2. Who can I manipulate to my advantage?\n"
        else:
            thought += "1. How does this event change my path forward?\n"
            thought += "2. Who can I truly trust among those present?\n"

        thought += "3. What am I not seeing that might be important?\n"
        thought += "4. How should I prepare for what comes next?\n\n"

        # Add quest reflections
        if event_quests:
            thought += "My quest obligations weigh on my mind:\n\n"
            for quest in event_quests:
                if char_class.lower() == "fighter":
                    thought += f"- {quest}: Is this battle worthy of my skills? Will it bring honor or just blood?\n"
                elif char_class.lower() == "wizard":
                    thought += f"- {quest}: What knowledge might I gain from this pursuit? Is there arcane significance I'm overlooking?\n"
                elif char_class.lower() == "cleric":
                    thought += f"- {quest}: How does this quest align with my deity's will? Am I serving a higher purpose?\n"
                elif char_class.lower() == "rogue":
                    thought += f"- {quest}: What's the real reward here? Is there something more valuable beneath the surface?\n"
                else:
                    thought += f"- {quest}: How will completing this affect my path? Is it worth the risks involved?\n"
            thought += "\n"

        thought += "These thoughts are for me alone. Sometimes what we keep inside reveals more truth than what we share with others."

        return thought

    def extract_character_data(self, character_data: Any) -> Dict[str, Any]:
        """
        Extract character data from various possible sources.
        Handles both dictionary format and DnDGame Character class instances.

        Args:
            character_data: Character data (dict or Character instance)

        Returns:
            Dictionary containing character attributes
        """
        # If it's already a dictionary, just return it
        if isinstance(character_data, dict):
            return character_data

        # If it's a Character instance from DnDGame
        if hasattr(character_data, "name") and hasattr(character_data, "char_class"):
            char_dict = {
                "name": character_data.name,
                "class": character_data.char_class,
                "hp": character_data.hp,
                "max_hp": character_data.max_hp,
                "attack": character_data.attack,
                "defense": character_data.defense,
                "status": "Alive" if character_data.alive else "Dead",
                "status_effects": character_data.status_effects,
                "abilities": list(character_data.abilities.keys()) if hasattr(character_data, "abilities") else []
            }

            # Add team information if available
            if hasattr(character_data, "team") and character_data.team:
                char_dict["team"] = character_data.team

            return char_dict

        # If it's some other object, try to convert it to a dict
        try:
            return {k: v for k, v in character_data.__dict__.items()
                   if not k.startswith('_') and not callable(v)}
        except Exception as e:
            self.logger.error(f"Failed to extract character data: {e}")
            # Return a minimal dictionary with just the name if possible
            if hasattr(character_data, "name"):
                return {"name": character_data.name}
            else:
                raise ValueError("Invalid character data format")
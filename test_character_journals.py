#!/usr/bin/env python3
import os
import logging
import datetime
from obsidian_logger import ObsidianLogger
from journal_manager import JournalManager
from game_manager import GameManager, KnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_journals")

class MockEventManager:
    """Mock event manager for testing."""

    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def emit(self, event_type, event_data):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(event_data)

    def emit_multiple(self, events):
        for event_type, event_data in events:
            self.emit(event_type, event_data)

    def publish(self, event_type, event_data):
        """Mock publish method for compatibility with ObsidianLogger."""
        self.emit(event_type, event_data)

def create_test_vault():
    """Create a test vault directory."""
    test_vault = "journal-test-vault"
    os.makedirs(test_vault, exist_ok=True)
    return test_vault

def ensure_templates_exist(obsidian_logger):
    """Create template files if they don't exist."""
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    os.makedirs(template_dir, exist_ok=True)

    # CharacterJournal template
    character_journal_template = '''---
character: {{ character_name }}
date_created: {{ date_created }}
---

# {{ character_name }}'s Journal

## Journal Entries

{% if journal_entries %}
{% for entry in journal_entries %}
### {{ entry.date }}

{{ entry.content }}

{% endfor %}
{% else %}
*No journal entries yet*
{% endif %}

## Internal Thoughts

{% if internal_thoughts %}
{% for thought in internal_thoughts %}
### {{ thought.date }}

{{ thought.content }}

{% endfor %}
{% else %}
*No recorded thoughts yet*
{% endif %}

## Related Events
{% if related_events %}
{% for event in related_events %}
- [[{{ event }}]]
{% endfor %}
{% else %}
*No related events recorded*
{% endif %}

## Related Characters
{% if related_characters %}
{% for character in related_characters %}
- [[{{ character }}]]
{% endfor %}
{% else %}
*No character connections recorded*
{% endif %}'''

    # JournalEntry template
    journal_entry_template = '''---
character: {{ character_name }}
entry_date: {{ entry_date }}
entry_type: {{ entry_type }}
related_event: {{ related_event }}
---

# {{ character_name }}'s {{ entry_type|title }} - {{ entry_date }}

{% if entry_type == "journal" %}
## Journal Entry
{% else %}
## Internal Thought
{% endif %}

{{ content }}

{% if mood %}
**Mood**: {{ mood }}
{% endif %}

{% if related_characters %}
## Related Characters
{% for character in related_characters %}
- [[{{ character }}]]
{% endfor %}
{% endif %}

{% if related_locations %}
## Related Locations
{% for location in related_locations %}
- [[{{ location }}]]
{% endfor %}
{% endif %}

{% if related_event %}
## Related Event
[[{{ related_event }}]]
{% endif %}'''

    # Save templates
    with open(os.path.join(template_dir, "CharacterJournal.md"), "w") as f:
        f.write(character_journal_template)

    with open(os.path.join(template_dir, "JournalEntry.md"), "w") as f:
        f.write(journal_entry_template)

    logger.info("Created template files in templates directory")

def main():
    # Create test vault
    test_vault = create_test_vault()
    logger.info(f"Created test vault: {test_vault}")

    # Initialize components
    obsidian_logger = ObsidianLogger(vault_path=test_vault)

    # Create template files
    ensure_templates_exist(obsidian_logger)

    event_manager = MockEventManager()
    game_manager = GameManager(obsidian_logger, event_manager)

    # Create a character
    character_data = {
        "name": "Thorin Oakenshield",
        "race": "Dwarf",
        "class": "Fighter",
        "bio": "A proud dwarf warrior seeking to reclaim his homeland. Born into royalty but forced into exile, Thorin has become hardened by years of wandering and working menial jobs to survive.",
        "status": "Alive",
        "hp": 45,
        "max_hp": 45,
        "attack": 15,
        "defense": 12,
        "location": "The Prancing Pony Inn"
    }

    # Create a location
    location_data = {
        "name": "The Prancing Pony Inn",
        "description": "A cozy inn in the town of Bree, known for its comfortable beds and excellent ale.",
        "region": "Bree-land",
        "type": "Inn"
    }

    # Create other characters
    other_character_data = {
        "name": "Gandalf the Grey",
        "race": "Wizard",
        "class": "Mage",
        "bio": "A wandering wizard with a reputation for troublemaking and fireworks.",
        "status": "Alive",
        "hp": 30,
        "max_hp": 30,
        "attack": 10,
        "defense": 8,
        "location": "The Prancing Pony Inn"
    }

    # Emit events to create the entities
    logger.info("Creating test entities...")
    event_manager.emit("location_created", location_data)
    event_manager.emit("character_created", character_data)
    event_manager.emit("character_created", other_character_data)

    # Create an event
    event_data = {
        "name": "Secret Meeting",
        "description": "Thorin meets with Gandalf to discuss the quest to reclaim Erebor.",
        "location": "The Prancing Pony Inn",
        "characters": ["Thorin Oakenshield", "Gandalf the Grey"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    logger.info("Creating test event...")
    event_manager.emit("event_occurred", event_data)

    # Print out the paths where the journal files are located
    character_name = character_data["name"]
    sanitized_name = obsidian_logger._sanitize_filename(character_name)

    journal_path = os.path.join(test_vault, "Journals", f"{sanitized_name}.md")
    entries_path = os.path.join(test_vault, "Journals", "Entries")
    thoughts_path = os.path.join(test_vault, "Journals", "Thoughts")

    logger.info(f"\nTest completed. Journal files created:")
    logger.info(f"Character Journal: {journal_path}")
    logger.info(f"Journal Entries Directory: {entries_path}")
    logger.info(f"Internal Thoughts Directory: {thoughts_path}")

    # Print instructions for viewing the files
    logger.info("\nTo view the journal files, you can use the following commands:")
    logger.info(f"cat {journal_path}")
    logger.info(f"ls -la {entries_path}")
    logger.info(f"ls -la {thoughts_path}")

    # Create a second event
    second_event_data = {
        "name": "Recruiting Bilbo",
        "description": "Thorin and the company arrive at Bag End to recruit Bilbo Baggins as their burglar.",
        "location": "Bag End",
        "characters": ["Thorin Oakenshield", "Gandalf the Grey", "Bilbo Baggins"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Create the new character and location first
    new_character_data = {
        "name": "Bilbo Baggins",
        "race": "Hobbit",
        "class": "Rogue",
        "bio": "A respectable hobbit from the Shire who loves comfort and routine.",
        "status": "Alive",
        "hp": 20,
        "max_hp": 20,
        "attack": 5,
        "defense": 5,
        "location": "Bag End"
    }

    new_location_data = {
        "name": "Bag End",
        "description": "A comfortable hobbit-hole in Hobbiton, the home of Bilbo Baggins.",
        "region": "The Shire",
        "type": "Home"
    }

    logger.info("\nCreating new entities and event...")
    event_manager.emit("location_created", new_location_data)
    event_manager.emit("character_created", new_character_data)

    # Move Thorin and Gandalf to Bag End
    game_manager.handle_character_movement("Thorin Oakenshield", "The Prancing Pony Inn", "Bag End")
    game_manager.handle_character_movement("Gandalf the Grey", "The Prancing Pony Inn", "Bag End")

    # Create the second event
    event_manager.emit("event_occurred", second_event_data)

    logger.info("\nSecond test completed. Check the journal files again to see updates.")

if __name__ == "__main__":
    main()
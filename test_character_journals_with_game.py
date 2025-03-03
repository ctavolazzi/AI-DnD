#!/usr/bin/env python3
import os
import logging
import datetime
from obsidian_logger import ObsidianLogger
from journal_manager import JournalManager
from game_manager import GameManager, KnowledgeGraph
from dnd_game import DnDGame, Character

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_journals_with_game")

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
    test_vault = "character-journal-test-vault"
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
class: {{ character_class }}
race: {{ character_race }}
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

    # Create a real DnDGame with characters
    logger.info("Creating DnDGame with characters...")
    game = DnDGame(auto_create_characters=False)

    # Create characters manually using the DnDGame Character class
    warrior = Character("Grimgar the Bold", "Fighter", hp=45, max_hp=45, attack=15, defense=8)
    warrior.team = "Heroes"
    wizard = Character("Elandra Spellweaver", "Wizard", hp=30, max_hp=30, attack=10, defense=3)
    wizard.team = "Heroes"
    rogue = Character("Nyx Shadowstep", "Rogue", hp=35, max_hp=35, attack=12, defense=5)
    rogue.team = "Heroes"
    cleric = Character("Thalia Lightbringer", "Cleric", hp=40, max_hp=40, attack=8, defense=6)
    cleric.team = "Heroes"

    orc = Character("Grakk", "Orc", hp=60, max_hp=60, attack=16, defense=10)
    orc.team = "Enemies"
    goblin = Character("Snik", "Goblin", hp=25, max_hp=25, attack=8, defense=3)
    goblin.team = "Enemies"

    # Use these characters to create character events in the game_manager
    logger.info("Creating characters in game_manager...")

    # Create location first
    location_data = {
        "name": "Darkwood Tavern",
        "description": "A cozy tavern at the edge of the Darkwood Forest, frequented by adventurers and locals alike.",
        "region": "Darkwood Forest",
        "type": "Tavern"
    }
    event_manager.emit("location_created", location_data)

    # Add the characters to the game manager
    for char in [warrior, wizard, rogue, cleric, orc, goblin]:
        char_data = {
            "name": char.name,
            "class": char.char_class,
            "hp": char.hp,
            "max_hp": char.max_hp,
            "attack": char.attack,
            "defense": char.defense,
            "status": "Alive",
            "team": char.team,
            "abilities": list(char.abilities.keys()),
            "status_effects": char.status_effects,
            "location": "Darkwood Tavern"
        }

        # Create a bio based on character class
        if char.char_class == "Fighter":
            char_data["bio"] = f"{char.name} is a hardened warrior who has seen countless battles. With sword and shield, they face any danger head-on."
        elif char.char_class == "Wizard":
            char_data["bio"] = f"{char.name} has spent years studying the arcane arts. Their knowledge of spells and magical theory is extensive."
        elif char.char_class == "Rogue":
            char_data["bio"] = f"{char.name} prefers the shadows and striking when least expected. They've made a living through cunning and stealth."
        elif char.char_class == "Cleric":
            char_data["bio"] = f"{char.name} serves their deity with unwavering faith, bringing healing to allies and divine wrath to enemies."
        elif char.char_class == "Orc":
            char_data["bio"] = f"{char.name} is a fierce orc warrior, respected among their tribe for strength and battle prowess."
        elif char.char_class == "Goblin":
            char_data["bio"] = f"{char.name} is a clever goblin scout who relies on speed and numbers rather than direct confrontation."

        event_manager.emit("character_created", char_data)

    # Create relationships between characters
    logger.info("Establishing relationships between characters...")
    game_manager.relationships.add_relationship("Grimgar the Bold", "Elandra Spellweaver", "traveling companion")
    game_manager.relationships.add_relationship("Grimgar the Bold", "Nyx Shadowstep", "suspicious ally")
    game_manager.relationships.add_relationship("Elandra Spellweaver", "Thalia Lightbringer", "trusted friend")

    # Update knowledge graph so characters know about each other
    for hero in ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer"]:
        for other in ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer"]:
            if hero != other:
                game_manager.knowledge_graph.update_entity_knowledge(hero, other, {"name": other, "relationship": "ally"})

    # Create events
    logger.info("Creating game events...")

    # Event 1: Initial meeting
    meeting_event = {
        "name": "Heroes' Meeting",
        "description": "The heroes gather at the Darkwood Tavern to discuss rumors of orc raids in the nearby villages.",
        "location": "Darkwood Tavern",
        "characters": ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    event_manager.emit("event_occurred", meeting_event)

    # Event 2: Combat encounter
    combat_event = {
        "name": "Ambush on the Road",
        "description": "While traveling to investigate the raids, the party is ambushed by Grakk the orc and his goblin companion Snik.",
        "location": "Forest Road",
        "characters": ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer", "Grakk", "Snik"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Create the new location first
    forest_road = {
        "name": "Forest Road",
        "description": "A winding dirt road that cuts through the dense Darkwood Forest.",
        "region": "Darkwood Forest",
        "type": "Road"
    }
    event_manager.emit("location_created", forest_road)

    # Move characters to the new location
    for char in ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer", "Grakk", "Snik"]:
        game_manager.handle_character_movement(char, "Darkwood Tavern", "Forest Road")

    # Create the combat event
    event_manager.emit("event_occurred", combat_event)

    # Simulate combat effects - warrior takes damage
    warrior_data = game_manager.knowledge_graph.get_entity_knowledge("Grimgar the Bold", "Grimgar the Bold")
    if warrior_data:
        warrior_data["hp"] = 30  # Took 15 damage
        warrior_data["status"] = "Injured"
        game_manager.knowledge_graph.update_entity_knowledge("Grimgar the Bold", "Grimgar the Bold", warrior_data)

    # Wizard uses fireball
    wizard_combat_event = {
        "name": "Elandra's Fireball",
        "description": "Elandra cast a powerful fireball spell against the orc raiders, turning the tide of battle.",
        "location": "Forest Road",
        "characters": ["Elandra Spellweaver", "Grakk", "Snik"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    event_manager.emit("event_occurred", wizard_combat_event)

    # Rogue gets critical hit
    rogue_combat_event = {
        "name": "Nyx's Backstab",
        "description": "Nyx disappeared into the shadows and reappeared behind Grakk, landing a devastating backstab.",
        "location": "Forest Road",
        "characters": ["Nyx Shadowstep", "Grakk"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    event_manager.emit("event_occurred", rogue_combat_event)

    # Cleric heals warrior
    cleric_combat_event = {
        "name": "Thalia's Healing",
        "description": "Seeing Grimgar wounded, Thalia channeled divine energy to heal his injuries.",
        "location": "Forest Road",
        "characters": ["Thalia Lightbringer", "Grimgar the Bold"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    event_manager.emit("event_occurred", cleric_combat_event)

    # Update warrior's health after healing
    if warrior_data:
        warrior_data["hp"] = 40  # Healed 10 hp
        warrior_data["status"] = "Active"
        game_manager.knowledge_graph.update_entity_knowledge("Grimgar the Bold", "Grimgar the Bold", warrior_data)

    # Event 3: Victory
    victory_event = {
        "name": "Victory on the Road",
        "description": "After a fierce battle, the heroes defeated the orc raiders. Grakk was slain, but Snik escaped into the forest.",
        "location": "Forest Road",
        "characters": ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer", "Grakk", "Snik"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    event_manager.emit("event_occurred", victory_event)

    # Print out the paths where the journal files are located
    logger.info("\nTest completed. Journal files created:")

    for char_name in ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer"]:
        sanitized_name = obsidian_logger._sanitize_filename(char_name)
        journal_path = os.path.join(test_vault, "Journals", f"{sanitized_name}.md")
        logger.info(f"{char_name}'s Journal: {journal_path}")

    entries_path = os.path.join(test_vault, "Journals", "Entries")
    thoughts_path = os.path.join(test_vault, "Journals", "Thoughts")

    logger.info(f"Journal Entries Directory: {entries_path}")
    logger.info(f"Internal Thoughts Directory: {thoughts_path}")

    # Print instructions for viewing the files
    logger.info("\nTo view character journals, you can use the following commands:")
    for char_name in ["Grimgar the Bold", "Elandra Spellweaver", "Nyx Shadowstep", "Thalia Lightbringer"]:
        sanitized_name = obsidian_logger._sanitize_filename(char_name)
        logger.info(f"cat {test_vault}/Journals/{sanitized_name}.md")

if __name__ == "__main__":
    main()
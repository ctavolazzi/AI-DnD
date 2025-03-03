#!/usr/bin/env python3
import os
import logging
import datetime
import shutil
from dungeon_master import DungeonMaster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_dm_journals")

def setup_test_vault():
    """Create a test vault for the Dungeon Master."""
    test_vault = "dm-journal-test-vault"
    # Remove existing vault if it exists
    if os.path.exists(test_vault):
        shutil.rmtree(test_vault)

    # Create the vault directory
    os.makedirs(test_vault, exist_ok=True)
    logger.info(f"Created test vault: {test_vault}")

    return test_vault

def main():
    """Test the Dungeon Master's integration with character journals."""
    # Create a test vault
    test_vault = setup_test_vault()

    # Create a Dungeon Master instance with the test vault
    dm = DungeonMaster(vault_path=test_vault)
    logger.info("Created Dungeon Master instance")

    # Initialize the run
    run_id = dm.initialize_run()
    logger.info(f"Initialized run with ID: {run_id}")

    # Add required templates
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    os.makedirs(template_dir, exist_ok=True)

    # Character Journal template
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
{% endif %}
'''

    # Journal Entry template
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
{% endif %}
'''

    # Save templates
    with open(os.path.join(template_dir, "CharacterJournal.md"), "w") as f:
        f.write(character_journal_template)

    with open(os.path.join(template_dir, "JournalEntry.md"), "w") as f:
        f.write(journal_entry_template)

    logger.info("Created template files in templates directory")

    # Initialize the game (creates characters and journals)
    logger.info("Initializing game...")
    dm.initialize_game()

    # Check if journals were created
    journals_dir = os.path.join(test_vault, "Journals")
    if os.path.exists(journals_dir):
        journals = os.listdir(journals_dir)
        character_journals = [j for j in journals if j.endswith(".md")]
        logger.info(f"Found {len(character_journals)} character journals: {character_journals}")

        # Check if entries and thoughts directories were created
        entries_dir = os.path.join(journals_dir, "Entries")
        thoughts_dir = os.path.join(journals_dir, "Thoughts")

        if os.path.exists(entries_dir):
            entries = os.listdir(entries_dir)
            logger.info(f"Found {len(entries)} journal entries")
        else:
            logger.warning("Entries directory not found")

        if os.path.exists(thoughts_dir):
            thoughts = os.listdir(thoughts_dir)
            logger.info(f"Found {len(thoughts)} internal thoughts")
        else:
            logger.warning("Thoughts directory not found")
    else:
        logger.error("Journals directory not found. Journal integration may not be working.")

    # Run a single turn to generate events
    logger.info("\nRunning a game turn to generate events...")
    dm.run_game_loop(max_turns=1)

    # Check for additional journal entries after events
    if os.path.exists(entries_dir):
        entries = os.listdir(entries_dir)
        logger.info(f"After events, found {len(entries)} journal entries")

    if os.path.exists(thoughts_dir):
        thoughts = os.listdir(thoughts_dir)
        logger.info(f"After events, found {len(thoughts)} internal thoughts")

    # Print sample of a character journal
    if character_journals:
        sample_journal = os.path.join(journals_dir, character_journals[0])
        logger.info(f"\nSample character journal ({character_journals[0]}):")
        with open(sample_journal, 'r') as f:
            logger.info(f.read())

    # Print instructions for checking the test results
    logger.info("\nTest completed. To view the journals, use:")
    logger.info(f"ls -la {test_vault}/Journals")
    logger.info(f"ls -la {test_vault}/Journals/Entries")
    logger.info(f"ls -la {test_vault}/Journals/Thoughts")

    # Display the first journal entry
    entry_files = os.listdir(entries_dir) if os.path.exists(entries_dir) else []
    if entry_files:
        sample_entry = os.path.join(entries_dir, entry_files[0])
        logger.info(f"\nSample journal entry ({entry_files[0]}):")
        with open(sample_entry, 'r') as f:
            logger.info(f.read())

if __name__ == "__main__":
    main()
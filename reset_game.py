#!/usr/bin/env python3
import os
import shutil
import time
import datetime
import json
import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Central configuration
CONFIG = {
    "vault_name": "ai-dnd-test-vault",
    "archive_dir": "ai-dnd-test-vault/Runs/Archived",
    "default_folders": [
        "Characters",
        "Locations",
        "Events",
        "Sessions",
        "Quests",
        "Items",
        "Runs",
        "Runs/Archived",
        "Dashboard"
    ],
    "required_files": [
        {"path": "Welcome.md", "is_template": True},
        {"path": "Start.md", "is_template": True},
        {"path": "Index.md", "is_template": True},
        {"path": "Runs/README.md", "is_template": True},
        {"path": "Dashboard.md", "is_template": True}
        # Current-Run.md is now created only when a game is started
    ],
    "entity_templates": [
        {"type": "character", "template": "Character.md"},
        {"type": "location", "template": "Location.md"},
        {"type": "item", "template": "Item.md"},
        {"type": "event", "template": "Event.md"},
        {"type": "quest", "template": "Quest.md"},
        {"type": "session", "template": "Session.md"},
        {"type": "combat", "template": "Combat.md"}
    ],
    "templates_dir": "templates",
    "obsidian_dir": ".obsidian",
    "run_program": "main.py"
}

def ensure_dir_exists(directory):
    """Ensure a directory exists, create it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def copy_directory_contents(src, dest):
    """Copy all contents from source to destination directory."""
    if not os.path.exists(src):
        logger.warning(f"Source directory does not exist: {src}")
        return

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    logger.info(f"Copied contents from {src} to {dest}")

def generate_file_from_template(template_name, output_path, context=None):
    """Generate a file from a template with optional context."""
    if context is None:
        context = {}

    template_path = os.path.join(CONFIG["templates_dir"], f"{template_name}.md")

    # Ensure templates directory exists
    ensure_dir_exists(CONFIG["templates_dir"])

    # Check if template exists, if not create a default one
    if not os.path.exists(template_path):
        create_default_template(template_name)

    # Read template content
    with open(template_path, 'r') as f:
        content = f.read()

    # Simple template substitution
    for key, value in context.items():
        content = content.replace(f"{{{{ {key} }}}}", str(value))

    # Write to output file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)

    logger.info(f"Generated {output_path} from template {template_name}")

def create_default_template(template_name):
    """Create a default template if it doesn't exist."""
    template_path = os.path.join(CONFIG["templates_dir"], f"{template_name}.md")

    content = ""
    if template_name == "Welcome":
        content = """This is your new *vault*.

An AI DnD DM will use this project to fill out data as it plays itself.

Check out [[Start]] to learn how to follow along.
"""
    elif template_name == "Start":
        content = """# How to Follow This Self-Playing Adventure

Welcome to your AI-driven D&D adventure! This page explains how to follow along as the AI plays the game and updates this journal automatically.

## How This Works

1. **The Game Plays Itself**: The AI-DnD system runs in the background, simulating characters, encounters, and combat
2. **The Journal Updates**: As events occur, new pages are created and existing ones are updated
3. **You Follow Along**: Use the links to navigate between pages and watch the story unfold

## Current Progress

> **Active Game Session**
> [[Current-Run|🎲 View Current Game Session]]

## Following the Adventure

### Step 1: Check the Dashboard
Use the [[Dashboard|📊 Dashboard]] to get a quick overview of the current game state, including:
- Active characters
- Current quest
- Recent events
- Game statistics

### Step 2: Explore the Content
Follow these narrative elements as they develop:
- **Characters**: Follow their journeys and stat progression
- **Locations**: Discover new areas as characters explore them
- **Quests**: See what objectives characters are pursuing
- **Combat**: Watch battles unfold with detailed turn-by-turn logging

### Step 3: Find Game Content
Two ways to browse all game content:
- Visit the [[Index|📑 Complete Index]] for a categorized listing of all content
- Use the [[Dashboard|📊 Dashboard]] navigation links for quick access

### Step 4: Review Past Runs
If you want to explore previous adventures:
- Visit [[Runs/Archived/README|📚 Archived Runs]] to see past game sessions

---

> [!TIP]
> As the game progresses, you'll see pages being added and updated. Navigate by clicking on any `[[bracketed link]]`.
"""
    elif template_name == "Index":
        content = """# Game Content Index

Last updated: {{ timestamp }}

> [!NOTE]
> This index provides a complete catalog of all game content by category.
> For how to follow along, see the [[Start]] page.
> For quick navigation, use the [[Dashboard]].

## Game Categories

### 👤 Characters
All characters encountered in the world.
- `[[Characters/]]` - Browse all characters

### 🗺️ Locations
Places discovered during the adventure.
- `[[Locations/]]` - Browse all locations

### 📜 Events
Significant moments in the adventure.
- `[[Events/]]` - Browse all events

### 📝 Sessions
Game session summaries and logs.
- `[[Sessions/]]` - Browse all sessions

### ⚔️ Quests
Active and completed quests.
- `[[Quests/]]` - Browse all quests

### 💎 Items
Artifacts, equipment, and treasures.
- `[[Items/]]` - Browse all items

## Game Management

- `[[Current-Run]]` - 🎲 Current Game Session
- `[[Runs/Archived/README|Archived Runs]]` - 📚 Previous Sessions
- `[[Dashboard]]` - 📊 Status Dashboard
- `[[Start]]` - 📖 How to Follow Along

---

> [!TIP]
> This index updates automatically as the game progresses.
"""
    elif template_name == "Runs_README":
        content = """# Archived Runs

This section contains archives of previous game runs.

## Available Archived Runs

No archived runs yet.
"""
    elif template_name == "Archived_README":
        content = """# Archived Runs

This folder contains archived game runs. Each archive contains the complete state of a game run, including all characters, locations, events, etc.

## Available Archives

No archives yet.

## How to Browse Archives

Each archive is named with the timestamp of when it was created. Click on an archive folder to explore its contents.

## Restoring an Archive

Archives are read-only. To restore an archive, you would need to copy its contents to the main vault folder.
"""
    elif template_name == "Dashboard":
        content = """# Game Dashboard

*Last Updated: {{ timestamp }}*

## Current Game Status

**Run ID**: {{ run_id }}
**Status**: {{ status }}
**Turn Count**: {{ turn_count }}

## Active Quest
{{ quest }}

## Current Party
{% for character in characters %}
- [[{{ character }}]]
{% endfor %}

## Recent Events
{% for event in events %}
- [[{{ event }}]]
{% endfor %}

## Navigation
- [[Current-Run|🎲 Current Game Session]]
- [[Index|📑 Game Index]]
- [[Characters/|👤 Characters]]
- [[Locations/|🗺️ Locations]]
- [[Events/|📜 Events]]
- [[Quests/|⚔️ Quests]]
- [[Items/|💎 Items]]
- [[Sessions/|📝 Sessions]]
"""
    elif template_name == "Current_Run":
        content = """---
run_id: {{ run_id }}
timestamp: {{ timestamp }}
status: {{ status }}
turn_count: {{ turn_count }}
---

# Current Game Run: {{ run_id }}

Started: {{ timestamp }}
Last Updated: {{ timestamp }}
Current Turn: {{ turn_count }}

## Active Quest
No active quest.

## Characters
No characters created yet.

## Events
No events have occurred yet.

## Combat
No combat has occurred yet.

## Sessions
No sessions recorded yet.

*This run is currently in progress. Content will be updated as the game progresses.*
"""
    else:
        content = f"# {template_name}\n\nThis is a default template for {template_name}."

    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    with open(template_path, 'w') as f:
        f.write(content)

    logger.info(f"Created default template: {template_name}")

def archive_current_vault(archive_name=None):
    """Archive the current vault to preserve its state."""
    vault_path = CONFIG["vault_name"]

    if not os.path.exists(vault_path):
        logger.error(f"Cannot archive: Vault path {vault_path} does not exist")
        return None

    # Extract run ID from Current-Run.md if possible
    run_id = extract_run_id_from_current(vault_path)

    # Generate archive name if not provided
    if not archive_name:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        archive_name = f"Run-{run_id}-{timestamp}" if run_id else f"Run-{timestamp}"

    archive_dir = os.path.join(CONFIG["archive_dir"], archive_name)
    archive_path = os.path.join(vault_path, "Runs", "Archived")

    # Ensure archive directory exists
    ensure_dir_exists(archive_dir)

    logger.info(f"Creating archive in {archive_dir}")

    # Create a safe copy function that avoids recursive copying
    def safe_copy(src, dst):
        # Don't copy if source is inside the archive directory
        if src.startswith(archive_path):
            return

        # If it's a directory, create it then copy contents
        if os.path.isdir(src):
            os.makedirs(dst, exist_ok=True)
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                safe_copy(s, d)
        # Otherwise just copy the file
        elif os.path.isfile(src):
            shutil.copy2(src, dst)

    # Top-level directories to copy
    for item in os.listdir(vault_path):
        # Skip .obsidian directory
        if item == ".obsidian":
            continue

        # Special handling for Runs directory
        if item == "Runs":
            dst_runs = os.path.join(archive_dir, "Runs")
            os.makedirs(dst_runs, exist_ok=True)

            # Copy only README.md from Runs directory
            src_readme = os.path.join(vault_path, "Runs", "README.md")
            if os.path.exists(src_readme):
                shutil.copy2(src_readme, os.path.join(dst_runs, "README.md"))

            # Don't copy Archived directory
            continue

        # Copy other directories and files
        src = os.path.join(vault_path, item)
        dst = os.path.join(archive_dir, item)
        safe_copy(src, dst)

    # Create archive metadata
    metadata = {
        "archive_name": archive_name,
        "archive_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": run_id or "unknown",
        "vault_path": vault_path
    }

    metadata_path = os.path.join(archive_dir, "archive-metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Vault archived to {archive_dir}")
    return archive_name

def extract_run_id_from_current(vault_path):
    """Extract run ID from Current-Run.md if it exists."""
    current_run_path = os.path.join(vault_path, "Current-Run.md")
    if not os.path.exists(current_run_path):
        return None

    try:
        with open(current_run_path, 'r') as f:
            content = f.read()
            match = re.search(r"run_id: ([^\n]+)", content)
            if match:
                return match.group(1)
    except Exception as e:
        logger.warning(f"Error extracting run ID: {e}")

    return None

def update_runs_readme(archive_name=None):
    """Update the Runs README with info about all archives."""
    archive_dir = CONFIG["archive_dir"]
    readme_path = os.path.join(archive_dir, "README.md")

    # Ensure directory exists
    ensure_dir_exists(archive_dir)

    content = """# Archived Runs

This folder contains archives of previous game runs. Each archive preserves the complete state of a game at the time of archiving.

## Available Archives

"""

    # List all subdirectories (archives)
    archives = []
    try:
        for item in os.listdir(archive_dir):
            item_path = os.path.join(archive_dir, item)
            if os.path.isdir(item_path) and item != "__pycache__":
                # Try to extract metadata
                metadata_path = os.path.join(item_path, "archive-metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        try:
                            metadata = json.load(f)
                            archives.append({
                                "name": item,
                                "created": metadata.get("created", "Unknown date"),
                                "run_id": metadata.get("run_id", "Unknown"),
                                "description": metadata.get("description", "No description")
                            })
                        except json.JSONDecodeError:
                            archives.append({
                                "name": item,
                                "created": "Unknown date",
                                "run_id": "Unknown",
                                "description": "Metadata file corrupted"
                            })
                else:
                    # No metadata, use folder name
                    archives.append({
                        "name": item,
                        "created": "Unknown date",
                        "run_id": "Unknown",
                        "description": "No metadata available"
                    })
    except Exception as e:
        logger.error(f"Error listing archives: {e}")

    # If no archives found
    if not archives:
        content += "No archived runs available.\n\n"
    else:
        # Sort archives by creation date (newest first)
        archives.sort(key=lambda x: x.get("created", ""), reverse=True)

        # Add each archive to content
        for archive in archives:
            content += f"### {archive['name']}\n\n"
            content += f"- **Run ID**: {archive['run_id']}\n"
            content += f"- **Created**: {archive['created']}\n"
            content += f"- **Description**: {archive['description']}\n\n"
            content += f"[Browse this archive]({archive['name']}/Index.md)\n\n"

    # Add info about current run
    content += """## About Archiving

Game runs are archived when:
1. A game is reset
2. The archive command is explicitly run
3. A game concludes normally

Archives are read-only snapshots and cannot be modified.
"""

    # Write the README
    with open(readme_path, 'w') as f:
        f.write(content)

    logger.info(f"Updated archives README at {readme_path}")

    return True

def create_current_run_file():
    """Create a new Current-Run.md file for a fresh game."""
    run_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"Creating new Current-Run.md with run_id: {run_id}")

    context = {
        "run_id": run_id,
        "timestamp": timestamp,
        "status": "active",
        "turn_count": 0
    }

    # Generate the file using the template
    generate_file_from_template("Current_Run", os.path.join(CONFIG["vault_name"], "Current-Run.md"), context)

    # Double-check that the file was generated with the correct run_id
    current_run_path = os.path.join(CONFIG["vault_name"], "Current-Run.md")

    try:
        with open(current_run_path, 'r') as f:
            content = f.read()

        # If the template variables weren't replaced properly, do it manually
        if "{{run_id}}" in content or "{{ run_id }}" in content:
            logger.warning("Template variables weren't replaced properly in Current-Run.md, fixing manually")
            content = re.sub(r'{{[\s]*run_id[\s]*}}', run_id, content)
            content = re.sub(r'{{[\s]*timestamp[\s]*}}', timestamp, content)
            content = re.sub(r'{{[\s]*turn_count\|default\(0\)[\s]*}}', "0", content)
            content = re.sub(r'{{[\s]*character_count\|default\(0\)[\s]*}}', "0", content)
            content = re.sub(r'{{[\s]*current_quest\|default\(".*"\)[\s]*}}', "*No active quest*", content)
            content = re.sub(r'{{[\s]*party_status\|default\(".*"\)[\s]*}}', "*No characters yet*", content)
            content = re.sub(r'{{[\s]*recent_events\|default\(".*"\)[\s]*}}', "*No events recorded yet*", content)

            # Write the corrected content back to the file
            with open(current_run_path, 'w') as f:
                f.write(content)

            logger.info(f"Fixed template variables in Current-Run.md")

        # Verify the run_id is properly set in the file
        with open(current_run_path, 'r') as f:
            content = f.read()
            if f"run_id: {run_id}" not in content:
                logger.warning("run_id not found in Current-Run.md after generation, forcing update")
                # Force the correct run_id in the YAML frontmatter
                content = re.sub(r'run_id:.*\n', f'run_id: {run_id}\n', content)
                with open(current_run_path, 'w') as f:
                    f.write(content)
                logger.info(f"Forced run_id update in Current-Run.md")
    except Exception as e:
        logger.error(f"Error processing Current-Run.md: {e}")
        # Create a minimal file with the correct run_id as a fallback
        minimal_content = f"""---
run_id: {run_id}
timestamp: {timestamp}
status: active
turn_count: 0
---

# Current Game Run: {run_id}

Started: {timestamp}
Last Updated: {timestamp}
Current Turn: 0

This is a fresh game run created on {timestamp}.
"""
        with open(current_run_path, 'w') as f:
            f.write(minimal_content)
        logger.info(f"Created minimal Current-Run.md file with run_id {run_id}")

    return run_id

def reset_vault(create_current_run=False):
    """Reset the vault to a clean state, archiving the current contents if they exist.

    Args:
        create_current_run: If True, create a Current-Run.md file. Default is False.

    Returns:
        If create_current_run is True, returns the run_id; otherwise returns True on success
    """
    vault_path = CONFIG["vault_name"]

    # If vault exists, archive it first
    if os.path.exists(vault_path):
        logger.info("Existing vault found, archiving before reset...")
        archive_name = archive_current_vault()
        if archive_name:
            update_runs_readme(archive_name)

        # Delete the existing vault
        try:
            # Don't delete the entire vault, just clear its contents
            # This preserves any .obsidian configuration
            for item in os.listdir(vault_path):
                item_path = os.path.join(vault_path, item)
                if item != ".obsidian":  # Preserve Obsidian settings
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            logger.info(f"Cleared contents of existing vault at {vault_path}")
        except Exception as e:
            logger.error(f"Error clearing vault: {e}")
            return False

    # Create the vault directory if it doesn't exist
    ensure_dir_exists(vault_path)

    # Create default folder structure
    for folder in CONFIG["default_folders"]:
        folder_path = os.path.join(vault_path, folder)
        ensure_dir_exists(folder_path)

    # Create required files from templates
    context = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    for file_info in CONFIG["required_files"]:
        file_path = file_info["path"]
        template_name = os.path.splitext(os.path.basename(file_path))[0]

        if file_info.get("is_template", False):
            generate_file_from_template(template_name, os.path.join(vault_path, file_path), context)
        else:
            source_file = os.path.join(CONFIG["templates_dir"], file_path)
            dest_file = os.path.join(vault_path, file_path)

            if os.path.exists(source_file):
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy2(source_file, dest_file)
                logger.info(f"Copied {source_file} to {dest_file}")

    # Explicitly check for and delete Current-Run.md to ensure a clean factory state
    current_run_path = os.path.join(vault_path, "Current-Run.md")
    if os.path.exists(current_run_path):
        os.remove(current_run_path)
        logger.info("Deleted existing Current-Run.md file for clean reset")

    # Create a new Current-Run.md file only if requested
    run_id = None
    if create_current_run:
        run_id = create_current_run_file()

    # Update the README in the archives directory
    update_runs_readme()

    if create_current_run and run_id:
        logger.info(f"Vault reset complete. New run ID: {run_id}")
        return run_id
    else:
        logger.info("Vault reset complete. No Current-Run.md file created.")
        return True

if __name__ == "__main__":
    # Reset the vault when script is run directly
    reset_vault(create_current_run=False)  # Don't create Current-Run.md when run directly
    logger.info("Vault has been reset and is ready for a new game.")
    logger.info(f"To start the game, run: python {CONFIG['run_program']}")
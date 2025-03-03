# AI-DnD Templating System

This directory contains templates for the various entity types in the AI-DnD game. These templates are used to generate Markdown files in the Obsidian vault as the game progresses.

## Template Format

Templates use a combination of Markdown and [Jinja2](https://jinja.palletsprojects.com/) templating syntax:

- Variables are enclosed in double curly braces: `{{ variable_name }}`
- Control structures use `{% %}` syntax (e.g., `{% if condition %}...{% endif %}`)
- YAML frontmatter is included at the top of each template for metadata

## Available Templates

1. **Character.md** - Template for character files
   - Used when creating new characters or updating existing ones
   - Tracks stats, abilities, inventory, relationships, and history

2. **Location.md** - Template for location files
   - Used for describing places in the game world
   - Tracks connected locations, present characters, and history

3. **Item.md** - Template for item files
   - Used for weapons, artifacts, and other objects
   - Tracks properties, effects, and ownership history

4. **Event.md** - Template for event files
   - Used for notable occurrences in the game
   - Tracks participants, outcomes, and related entities

5. **Quest.md** - Template for quest files
   - Used for tracking objectives and progress
   - Tracks status, difficulty, related locations/items/characters

6. **Session.md** - Template for session summaries
   - Provides an overview of a gaming session
   - Tracks characters present, locations visited, events, etc.

7. **Combat.md** - Template for combat encounters
   - Used for battles and fights
   - Tracks participants, actions, and outcomes

## Creating New Templates

To create a new template:

1. Create a new Markdown file in this directory with the `.md` extension
2. Add YAML frontmatter at the top for metadata fields
3. Use `{{ variable_name }}` syntax to include dynamic content
4. Use Jinja2 control structures for conditional content or loops

## How Templates Are Used

The `ObsidianLogger` class in `obsidian_logger.py` uses Jinja2 to render these templates with context data provided by the game. The rendered content is then written to the appropriate location in the Obsidian vault.

## Template Variables

Each template expects specific variables to be present in the context. If a required variable is missing, a default value will be used where possible.

See the individual template files for the specific variables used by each.
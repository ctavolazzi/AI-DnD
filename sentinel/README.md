# Sentinel: Game State Monitoring System for AI-DnD

Sentinel is a comprehensive monitoring system designed to ensure logical consistency within the AI-DnD game. It validates game state, identifies inconsistencies, and logs issues for review without making changes to the game state itself.

## Purpose

The primary purpose of Sentinel is to:

1. **Monitor game state** for logical inconsistencies
2. **Validate relationships** between game entities
3. **Ensure narrative consistency** throughout gameplay
4. **Identify potential issues** before they impact the player experience
5. **Provide detailed logs** for debugging and analysis

## Components

Sentinel consists of several key components:

### Core Components

- **Sentinel**: The main coordinator class that manages validation activities
- **SentinelConfig**: Configuration settings for validation rules and operational parameters

### Validators

- **EntityValidator**: Ensures individual entities have all required fields and valid values
- **RelationshipValidator**: Validates relationships between entities for consistency
- **WorldStateValidator**: Checks the overall game world state for logical consistency
- **NarrativeConsistencyValidator**: Monitors narrative elements for continuity and coherence

## Integration

To integrate Sentinel into your AI-DnD game:

1. Initialize the Sentinel system with your game components:

```python
from sentinel.integration import initialize_sentinel

# Initialize Sentinel with game components
sentinel = initialize_sentinel(game_manager, dungeon_master)
```

2. Run validation at strategic points in your game loop:

```python
# Run full validation
issues = sentinel.validate_all()

# Or validate specific aspects
entity_issues = sentinel.validate_entity("player_character")
relationship_issues = sentinel.validate_relationships()
```

3. Handle any issues found:

```python
from sentinel.integration import handle_validation_issues

# Log issues and optionally attempt auto-fixes
handle_validation_issues(issues, game_manager, auto_fix=True)
```

## Configuration

Sentinel is highly configurable through the `SentinelConfig` class:

```python
from sentinel.config import SentinelConfig

# Create custom configuration
config = SentinelConfig()
config.enabled = True
config.log_level = "INFO"

# Set validation intervals (in seconds)
config.validation_intervals = {
    "entity": 60,        # Validate entities every minute
    "relationship": 120,  # Validate relationships every 2 minutes
    "world_state": 300,   # Validate world state every 5 minutes
    "narrative": 600      # Validate narrative consistency every 10 minutes
}

# Configure entity validation rules
config.entity_rules = {
    "required_fields": {
        "character": ["name", "description", "location", "status"],
        # ... other entity types
    }
}

# Initialize Sentinel with custom config
sentinel = initialize_sentinel(game_manager, dungeon_master, config)
```

## Validation Rules

Sentinel validates game state based on configurable rules:

### Entity Rules

- Required fields for each entity type
- Valid status values
- Internal consistency of entity data

### Relationship Rules

- Valid relationship types
- Bidirectional relationship consistency
- Relationship validity based on entity types

### World State Rules

- Location connection consistency
- Character placement in the world
- Item placement and ownership

### Narrative Rules

- Character knowledge consistency
- Quest progression logic
- Narrative continuity between game states

## Issue Handling

Validation issues are categorized by severity:

- **Error**: Critical issues that should be addressed immediately
- **Warning**: Potential problems that should be reviewed
- **Info**: Minor inconsistencies that may not require action

Issues can be logged, displayed to developers, or automatically fixed depending on configuration.

## Example Usage

See `sentinel/integration.py` for detailed examples of how to use Sentinel in your game.

## Best Practices

1. Run validation at key points in the game loop (turn start/end)
2. Configure validation intervals based on performance requirements
3. Review logs regularly to identify recurring issues
4. Use auto-fix capabilities cautiously for simple issues only
5. Adjust validation rules as your game evolves

## Contributing

To extend Sentinel:

1. Add new validation rules to existing validators
2. Create new validator classes for specific aspects of your game
3. Enhance the auto-fix capabilities for common issues
4. Improve performance for large game states

## License

This project is part of the AI-DnD game and follows the same licensing terms.
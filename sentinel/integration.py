"""
Sentinel Integration Example

This module demonstrates how to integrate the Sentinel monitoring system
into the AI-DnD game. It provides examples of initialization, configuration,
and usage of the Sentinel system for monitoring game state consistency.
"""

import logging
import os
from typing import Dict, Any, Optional

# Import Sentinel components
from sentinel.sentinel import Sentinel
from sentinel.config import SentinelConfig
from sentinel.validators.entity_validator import EntityValidator
from sentinel.validators.relationship_validator import RelationshipValidator
from sentinel.validators.world_state_validator import WorldStateValidator
from sentinel.validators.narrative_validator import NarrativeConsistencyValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'sentinel.log'), mode='a')
    ]
)

logger = logging.getLogger("sentinel.integration")


def initialize_sentinel(game_manager, dungeon_master=None, config=None) -> Sentinel:
    """
    Initialize the Sentinel monitoring system with the game components.

    Args:
        game_manager: The GameManager instance
        dungeon_master: The DungeonMaster instance
        config: Optional custom configuration

    Returns:
        Initialized Sentinel instance
    """
    logger.info("Initializing Sentinel monitoring system")

    # Create default config if none provided
    if config is None:
        config = create_default_config()

    # Initialize Sentinel
    sentinel = Sentinel(
        game_manager=game_manager,
        dungeon_master=dungeon_master,
        config=config
    )

    # Register with game components
    sentinel.register_with_game_components()

    logger.info("Sentinel monitoring system initialized successfully")
    return sentinel


def create_default_config() -> SentinelConfig:
    """
    Create a default configuration for the Sentinel system.

    Returns:
        Default SentinelConfig instance
    """
    logger.debug("Creating default Sentinel configuration")

    config = SentinelConfig()

    # Set general settings
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
            "location": ["name", "description", "connections"],
            "item": ["name", "description"],
            "quest": ["name", "description", "status"]
        },
        "valid_statuses": {
            "character": ["active", "inactive", "dead", "missing"],
            "quest": ["inactive", "active", "completed", "failed"]
        }
    }

    # Configure relationship validation rules
    config.relationship_rules = {
        "valid_types": ["knows", "friends_with", "enemies_with", "has_item", "at_location", "assigned_to"],
        "check_bidirectional": True
    }

    # Configure world state validation rules
    config.world_state_rules = {
        "verify_location_connections": True,
        "verify_location_character_lists": True,
        "check_isolated_locations": True,
        "check_orphaned_entities": True,
        "connections_should_be_bidirectional": True
    }

    # Configure narrative consistency rules
    config.narrative_rules = {
        "check_character_knowledge": True,
        "check_quest_progression": True,
        "check_narrative_continuity": True,
        "significant_relationship_change_threshold": 0.3
    }

    # Configure severity thresholds
    config.severity_thresholds = {
        "missing_required_field": "error",
        "invalid_status": "error",
        "missing_relationship": "warning",
        "isolated_location": "info",
        "orphaned_entity": "warning",
        "character_location_mismatch": "error",
        "missing_knowledge": "warning",
        "unexplained_knowledge": "warning",
        "impossible_movement": "error"
    }

    # Configure operational settings
    config.operational_settings = {
        "max_validation_time": 5.0,  # Maximum time in seconds for a validation run
        "max_issues_logged": 100,    # Maximum number of issues to log per validation
        "throttle_validation": True  # Throttle validation if game is busy
    }

    logger.debug("Default Sentinel configuration created")
    return config


def integrate_with_game_loop(game_loop_function, sentinel: Sentinel):
    """
    Decorator to integrate Sentinel validation with the game loop.

    Args:
        game_loop_function: The main game loop function to wrap
        sentinel: The Sentinel instance

    Returns:
        Wrapped game loop function with Sentinel validation
    """
    def wrapped_game_loop(*args, **kwargs):
        # Run pre-turn validation
        logger.debug("Running pre-turn validation")
        pre_turn_issues = sentinel.validate_all()
        if pre_turn_issues:
            logger.warning(f"Found {len(pre_turn_issues)} issues before turn execution")
            # Log issues but don't interrupt gameplay

        # Execute the original game loop function
        result = game_loop_function(*args, **kwargs)

        # Run post-turn validation
        logger.debug("Running post-turn validation")
        post_turn_issues = sentinel.validate_all()
        if post_turn_issues:
            logger.warning(f"Found {len(post_turn_issues)} issues after turn execution")
            # Log issues but don't interrupt gameplay

        return result

    return wrapped_game_loop


def handle_validation_issues(issues: list, game_manager=None, auto_fix=False):
    """
    Handle validation issues found by Sentinel.

    Args:
        issues: List of validation issues
        game_manager: The GameManager instance (for auto-fixing)
        auto_fix: Whether to attempt automatic fixes for issues
    """
    if not issues:
        logger.info("No validation issues found")
        return

    logger.info(f"Handling {len(issues)} validation issues")

    # Group issues by severity
    errors = []
    warnings = []
    infos = []

    for issue in issues:
        severity = issue.get("severity", "warning")
        if severity == "error":
            errors.append(issue)
        elif severity == "warning":
            warnings.append(issue)
        else:
            infos.append(issue)

    # Log issues by severity
    if errors:
        logger.error(f"Found {len(errors)} critical issues that need attention")
        for i, error in enumerate(errors):
            logger.error(f"Error {i+1}: {error['title']} - {error['description']}")

    if warnings:
        logger.warning(f"Found {len(warnings)} warnings that should be reviewed")
        for i, warning in enumerate(warnings):
            logger.warning(f"Warning {i+1}: {warning['title']} - {warning['description']}")

    if infos:
        logger.info(f"Found {len(infos)} informational issues")
        # Don't log all info issues to avoid cluttering the log

    # Attempt auto-fixes if enabled
    if auto_fix and game_manager:
        fixed_count = attempt_auto_fixes(issues, game_manager)
        logger.info(f"Auto-fixed {fixed_count} issues")


def attempt_auto_fixes(issues: list, game_manager) -> int:
    """
    Attempt to automatically fix certain types of validation issues.

    Args:
        issues: List of validation issues
        game_manager: The GameManager instance

    Returns:
        Number of issues fixed
    """
    fixed_count = 0

    for issue in issues:
        issue_title = issue.get("title", "")

        # Handle character location mismatches
        if issue_title == "Character Location Mismatch" and len(issue.get("entities", [])) >= 2:
            location_id = issue["entities"][0]
            character_id = issue["entities"][1]

            try:
                # Update location's character list
                if hasattr(game_manager, "locations") and location_id in game_manager.locations:
                    location = game_manager.locations[location_id]
                    if "characters" not in location:
                        location["characters"] = []
                    if character_id not in location["characters"]:
                        location["characters"].append(character_id)
                        logger.info(f"Auto-fixed: Added character {character_id} to location {location_id} character list")
                        fixed_count += 1
            except Exception as e:
                logger.error(f"Error during auto-fix: {e}")

        # Handle missing character list
        elif issue_title == "Missing Character List" and "missing_characters" in issue:
            location_id = issue["entities"][0]
            missing_characters = issue.get("missing_characters", [])

            try:
                # Create character list for location
                if hasattr(game_manager, "locations") and location_id in game_manager.locations:
                    location = game_manager.locations[location_id]
                    if "characters" not in location:
                        location["characters"] = []

                    for character_id in missing_characters:
                        if character_id not in location["characters"]:
                            location["characters"].append(character_id)

                    logger.info(f"Auto-fixed: Created character list for location {location_id}")
                    fixed_count += 1
            except Exception as e:
                logger.error(f"Error during auto-fix: {e}")

    return fixed_count


# Example usage in main game file
def example_usage():
    """Example of how to use Sentinel in the main game file."""
    # This is just an example and won't actually run

    # Assume these are defined elsewhere
    game_manager = None  # GameManager instance
    dungeon_master = None  # DungeonMaster instance

    # Initialize Sentinel
    sentinel = initialize_sentinel(game_manager, dungeon_master)

    # Integrate with game loop
    original_game_loop = None  # The original game loop function
    game_loop = integrate_with_game_loop(original_game_loop, sentinel)

    # Run validation on demand
    issues = sentinel.validate_all()
    handle_validation_issues(issues, game_manager)

    # Validate specific entity
    character_issues = sentinel.validate_entity("player_character")
    if character_issues:
        logger.warning(f"Found {len(character_issues)} issues with player character")

    # Validate relationships
    relationship_issues = sentinel.validate_relationships()
    if relationship_issues:
        logger.warning(f"Found {len(relationship_issues)} relationship issues")


if __name__ == "__main__":
    # This won't actually run, it's just for demonstration
    print("This is an example module showing how to integrate Sentinel.")
    print("Import and use these functions in your main game code.")
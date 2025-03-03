"""
Entity Validator Module

This module provides validation for individual entities within the game world,
ensuring they have all required fields, valid values, and consistent internal state.
"""

import logging
from typing import Dict, List, Any, Optional, Set

logger = logging.getLogger("sentinel.validators.entity")


class EntityValidator:
    """
    Validates individual entities within the game world.

    This validator checks that entities (characters, locations, items, quests)
    have all required fields, valid values, and consistent internal state.
    """

    def __init__(self, game_manager, config=None):
        """
        Initialize the entity validator.

        Args:
            game_manager: Reference to the GameManager instance
            config: Configuration settings for validation
        """
        self.game_manager = game_manager
        self.config = config
        logger.debug("EntityValidator initialized")

    def validate(self) -> List[Dict[str, Any]]:
        """
        Validate all entities in the game world.

        Returns:
            List of issues found during validation
        """
        logger.info("Starting validation of all entities")
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate entities: game_manager not set")
            return issues

        # Validate characters
        logger.debug("Validating characters")
        for character_id in self._get_all_character_ids():
            character_issues = self.validate_character(character_id)
            issues.extend(character_issues)

        # Validate locations
        logger.debug("Validating locations")
        for location_id in self._get_all_location_ids():
            location_issues = self.validate_location(location_id)
            issues.extend(location_issues)

        # Validate items
        logger.debug("Validating items")
        for item_id in self._get_all_item_ids():
            item_issues = self.validate_item(item_id)
            issues.extend(item_issues)

        # Validate quests
        logger.debug("Validating quests")
        for quest_id in self._get_all_quest_ids():
            quest_issues = self.validate_quest(quest_id)
            issues.extend(quest_issues)

        logger.info(f"Entity validation complete. Found {len(issues)} issues.")
        return issues

    def validate_single_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Validate a specific entity by ID.

        Args:
            entity_id: The ID of the entity to validate

        Returns:
            List of issues found during validation
        """
        entity_type = self._determine_entity_type(entity_id)

        if entity_type == "character":
            return self.validate_character(entity_id)
        elif entity_type == "location":
            return self.validate_location(entity_id)
        elif entity_type == "item":
            return self.validate_item(entity_id)
        elif entity_type == "quest":
            return self.validate_quest(entity_id)
        else:
            logger.warning(f"Unknown entity type for entity_id: {entity_id}")
            return [{
                "title": "Unknown Entity Type",
                "description": f"Cannot validate entity with ID {entity_id}: unknown type",
                "severity": "warning",
                "entities": [entity_id]
            }]

    def validate_character(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Validate a character entity.

        Args:
            character_id: The ID of the character to validate

        Returns:
            List of issues found during validation
        """
        issues = []

        # Get character data
        character = self._get_character(character_id)
        if not character:
            issues.append({
                "title": "Character Not Found",
                "description": f"Character with ID {character_id} not found in game state",
                "severity": "error",
                "entities": [character_id]
            })
            return issues

        # Check required fields
        required_fields = self._get_required_character_fields()
        for field in required_fields:
            if field not in character or character[field] is None:
                issues.append({
                    "title": "Missing Required Field",
                    "description": f"Character '{character_id}' is missing required field: {field}",
                    "severity": self._get_severity("missing_required_field"),
                    "entities": [character_id],
                    "field": field
                })

        # Check valid status values
        if "status" in character:
            valid_statuses = self._get_valid_character_statuses()
            if character["status"] not in valid_statuses:
                issues.append({
                    "title": "Invalid Character Status",
                    "description": f"Character '{character_id}' has invalid status: {character['status']}",
                    "severity": self._get_severity("invalid_field_value"),
                    "entities": [character_id],
                    "field": "status",
                    "value": character["status"],
                    "valid_values": valid_statuses
                })

        # Check HP consistency (max_hp >= hp, hp >= 0)
        if "hp" in character and "max_hp" in character:
            if not isinstance(character["hp"], (int, float)) or not isinstance(character["max_hp"], (int, float)):
                issues.append({
                    "title": "Invalid HP Values",
                    "description": f"Character '{character_id}' has non-numeric HP values",
                    "severity": self._get_severity("invalid_field_value"),
                    "entities": [character_id],
                    "fields": ["hp", "max_hp"]
                })
            elif character["hp"] > character["max_hp"]:
                issues.append({
                    "title": "HP Exceeds Max HP",
                    "description": f"Character '{character_id}' has HP ({character['hp']}) greater than max HP ({character['max_hp']})",
                    "severity": self._get_severity("invalid_field_value"),
                    "entities": [character_id],
                    "fields": ["hp", "max_hp"]
                })
            elif character["hp"] < 0:
                issues.append({
                    "title": "Negative HP",
                    "description": f"Character '{character_id}' has negative HP ({character['hp']})",
                    "severity": self._get_severity("invalid_field_value"),
                    "entities": [character_id],
                    "field": "hp"
                })

        # Check alive status consistency with HP
        if "alive" in character and "hp" in character:
            if character["alive"] and character["hp"] <= 0:
                issues.append({
                    "title": "Inconsistent Alive Status",
                    "description": f"Character '{character_id}' is marked as alive but has HP <= 0",
                    "severity": self._get_severity("inconsistent_relationship"),
                    "entities": [character_id],
                    "fields": ["alive", "hp"]
                })
            elif not character["alive"] and character["hp"] > 0:
                issues.append({
                    "title": "Inconsistent Dead Status",
                    "description": f"Character '{character_id}' is marked as dead but has HP > 0",
                    "severity": self._get_severity("inconsistent_relationship"),
                    "entities": [character_id],
                    "fields": ["alive", "hp"]
                })

        # Check location consistency
        if "location" in character:
            location_id = character["location"]
            location_exists = self._check_location_exists(location_id)

            if not location_exists:
                issues.append({
                    "title": "Invalid Location Reference",
                    "description": f"Character '{character_id}' references non-existent location: {location_id}",
                    "severity": self._get_severity("invalid_field_value"),
                    "entities": [character_id],
                    "field": "location"
                })
            else:
                # Check if character has present_at relationship with this location
                has_relationship = self._check_character_location_relationship(character_id, location_id)
                if not has_relationship:
                    issues.append({
                        "title": "Missing Location Relationship",
                        "description": f"Character '{character_id}' claims to be at '{location_id}' but has no 'present_at' relationship",
                        "severity": self._get_severity("character_location_mismatch"),
                        "entities": [character_id, location_id]
                    })

        return issues

    def validate_location(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Validate a location entity.

        Args:
            location_id: The ID of the location to validate

        Returns:
            List of issues found during validation
        """
        issues = []

        # Get location data
        location = self._get_location(location_id)
        if not location:
            issues.append({
                "title": "Location Not Found",
                "description": f"Location with ID {location_id} not found in game state",
                "severity": "error",
                "entities": [location_id]
            })
            return issues

        # Check required fields
        required_fields = self._get_required_location_fields()
        for field in required_fields:
            if field not in location or location[field] is None:
                issues.append({
                    "title": "Missing Required Field",
                    "description": f"Location '{location_id}' is missing required field: {field}",
                    "severity": self._get_severity("missing_required_field"),
                    "entities": [location_id],
                    "field": field
                })

        # Check connections validity (if present)
        if "connections" in location and location["connections"]:
            for connected_location_id in location["connections"]:
                if not self._check_location_exists(connected_location_id):
                    issues.append({
                        "title": "Invalid Connection Reference",
                        "description": f"Location '{location_id}' references non-existent connected location: {connected_location_id}",
                        "severity": self._get_severity("invalid_field_value"),
                        "entities": [location_id],
                        "field": "connections"
                    })

        # Check characters consistency (if present)
        if "characters" in location and location["characters"]:
            for character_id in location["characters"]:
                if not self._check_character_exists(character_id):
                    issues.append({
                        "title": "Invalid Character Reference",
                        "description": f"Location '{location_id}' lists non-existent character: {character_id}",
                        "severity": self._get_severity("invalid_field_value"),
                        "entities": [location_id],
                        "field": "characters"
                    })
                else:
                    # Check if character has this location set as its location
                    char_location_match = self._check_character_location_field(character_id, location_id)
                    if not char_location_match:
                        issues.append({
                            "title": "Character Location Mismatch",
                            "description": f"Location '{location_id}' lists character '{character_id}' but character's location field points elsewhere",
                            "severity": self._get_severity("character_location_mismatch"),
                            "entities": [location_id, character_id]
                        })

        return issues

    def validate_item(self, item_id: str) -> List[Dict[str, Any]]:
        """
        Validate an item entity.

        Args:
            item_id: The ID of the item to validate

        Returns:
            List of issues found during validation
        """
        issues = []

        # Get item data
        item = self._get_item(item_id)
        if not item:
            issues.append({
                "title": "Item Not Found",
                "description": f"Item with ID {item_id} not found in game state",
                "severity": "error",
                "entities": [item_id]
            })
            return issues

        # Check required fields
        required_fields = self._get_required_item_fields()
        for field in required_fields:
            if field not in item or item[field] is None:
                issues.append({
                    "title": "Missing Required Field",
                    "description": f"Item '{item_id}' is missing required field: {field}",
                    "severity": self._get_severity("missing_required_field"),
                    "entities": [item_id],
                    "field": field
                })

        # Add more item-specific validation as needed

        return issues

    def validate_quest(self, quest_id: str) -> List[Dict[str, Any]]:
        """
        Validate a quest entity.

        Args:
            quest_id: The ID of the quest to validate

        Returns:
            List of issues found during validation
        """
        issues = []

        # Get quest data
        quest = self._get_quest(quest_id)
        if not quest:
            issues.append({
                "title": "Quest Not Found",
                "description": f"Quest with ID {quest_id} not found in game state",
                "severity": "error",
                "entities": [quest_id]
            })
            return issues

        # Check required fields
        required_fields = self._get_required_quest_fields()
        for field in required_fields:
            if field not in quest or quest[field] is None:
                issues.append({
                    "title": "Missing Required Field",
                    "description": f"Quest '{quest_id}' is missing required field: {field}",
                    "severity": self._get_severity("missing_required_field"),
                    "entities": [quest_id],
                    "field": field
                })

        # Check valid status values
        if "status" in quest:
            valid_statuses = self._get_valid_quest_statuses()
            if quest["status"] not in valid_statuses:
                issues.append({
                    "title": "Invalid Quest Status",
                    "description": f"Quest '{quest_id}' has invalid status: {quest['status']}",
                    "severity": self._get_severity("invalid_field_value"),
                    "entities": [quest_id],
                    "field": "status",
                    "value": quest["status"],
                    "valid_values": valid_statuses
                })

        return issues

    # Helper methods

    def _determine_entity_type(self, entity_id: str) -> str:
        """Determine the type of an entity based on its ID and presence in different collections."""
        if self._check_character_exists(entity_id):
            return "character"
        elif self._check_location_exists(entity_id):
            return "location"
        elif self._check_item_exists(entity_id):
            return "item"
        elif self._check_quest_exists(entity_id):
            return "quest"
        else:
            return "unknown"

    def _get_all_character_ids(self) -> List[str]:
        """Get IDs of all characters in the game."""
        if not self.game_manager:
            return []

        try:
            # Implementation depends on GameManager's API
            return list(self.game_manager.characters.keys())
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting character IDs: {e}")
            return []

    def _get_all_location_ids(self) -> List[str]:
        """Get IDs of all locations in the game."""
        if not self.game_manager:
            return []

        try:
            # Implementation depends on GameManager's API
            return list(self.game_manager.locations.keys())
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting location IDs: {e}")
            return []

    def _get_all_item_ids(self) -> List[str]:
        """Get IDs of all items in the game."""
        if not self.game_manager:
            return []

        try:
            # Implementation depends on GameManager's API
            return list(self.game_manager.items.keys()) if hasattr(self.game_manager, "items") else []
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting item IDs: {e}")
            return []

    def _get_all_quest_ids(self) -> List[str]:
        """Get IDs of all quests in the game."""
        if not self.game_manager:
            return []

        try:
            # Implementation depends on GameManager's API
            return list(self.game_manager.quests.keys()) if hasattr(self.game_manager, "quests") else []
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting quest IDs: {e}")
            return []

    def _get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get character data by ID."""
        if not self.game_manager:
            return None

        try:
            # Implementation depends on GameManager's API
            return self.game_manager.characters.get(character_id)
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting character {character_id}: {e}")
            return None

    def _get_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get location data by ID."""
        if not self.game_manager:
            return None

        try:
            # Implementation depends on GameManager's API
            return self.game_manager.locations.get(location_id)
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting location {location_id}: {e}")
            return None

    def _get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item data by ID."""
        if not self.game_manager:
            return None

        try:
            # Implementation depends on GameManager's API
            return self.game_manager.items.get(item_id) if hasattr(self.game_manager, "items") else None
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting item {item_id}: {e}")
            return None

    def _get_quest(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get quest data by ID."""
        if not self.game_manager:
            return None

        try:
            # Implementation depends on GameManager's API
            return self.game_manager.quests.get(quest_id) if hasattr(self.game_manager, "quests") else None
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting quest {quest_id}: {e}")
            return None

    def _check_character_exists(self, character_id: str) -> bool:
        """Check if a character exists in the game."""
        if not self.game_manager:
            return False

        try:
            # Implementation depends on GameManager's API
            return character_id in self.game_manager.characters
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking character existence {character_id}: {e}")
            return False

    def _check_location_exists(self, location_id: str) -> bool:
        """Check if a location exists in the game."""
        if not self.game_manager:
            return False

        try:
            # Implementation depends on GameManager's API
            return location_id in self.game_manager.locations
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking location existence {location_id}: {e}")
            return False

    def _check_item_exists(self, item_id: str) -> bool:
        """Check if an item exists in the game."""
        if not self.game_manager:
            return False

        try:
            # Implementation depends on GameManager's API
            return hasattr(self.game_manager, "items") and item_id in self.game_manager.items
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking item existence {item_id}: {e}")
            return False

    def _check_quest_exists(self, quest_id: str) -> bool:
        """Check if a quest exists in the game."""
        if not self.game_manager:
            return False

        try:
            # Implementation depends on GameManager's API
            return hasattr(self.game_manager, "quests") and quest_id in self.game_manager.quests
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking quest existence {quest_id}: {e}")
            return False

    def _check_character_location_relationship(self, character_id: str, location_id: str) -> bool:
        """Check if a character has a 'present_at' relationship with a location."""
        if not self.game_manager:
            return False

        try:
            # Implementation depends on GameManager's API
            # This assumes GameManager has an entity_relationship_manager attribute
            return self.game_manager.entity_relationship_manager.has_relationship(
                character_id, location_id, "present_at"
            )
        except (AttributeError, Exception) as e:
            logger.error(f"Error checking character-location relationship: {e}")
            return False

    def _check_character_location_field(self, character_id: str, location_id: str) -> bool:
        """Check if a character's location field points to the given location."""
        character = self._get_character(character_id)
        if not character:
            return False

        return character.get("location") == location_id

    def _get_required_character_fields(self) -> List[str]:
        """Get list of required fields for characters."""
        if self.config and hasattr(self.config, "entity_rules"):
            return self.config.entity_rules.get("required_character_fields", [])

        # Default required fields if config not available
        return ["name", "char_class", "hp", "max_hp", "attack", "defense", "alive", "status"]

    def _get_required_location_fields(self) -> List[str]:
        """Get list of required fields for locations."""
        if self.config and hasattr(self.config, "entity_rules"):
            return self.config.entity_rules.get("required_location_fields", [])

        # Default required fields if config not available
        return ["name", "description", "type"]

    def _get_required_item_fields(self) -> List[str]:
        """Get list of required fields for items."""
        if self.config and hasattr(self.config, "entity_rules"):
            return self.config.entity_rules.get("required_item_fields", [])

        # Default required fields if config not available
        return ["name", "description", "type"]

    def _get_required_quest_fields(self) -> List[str]:
        """Get list of required fields for quests."""
        if self.config and hasattr(self.config, "entity_rules"):
            return self.config.entity_rules.get("required_quest_fields", [])

        # Default required fields if config not available
        return ["name", "description", "status"]

    def _get_valid_character_statuses(self) -> List[str]:
        """Get list of valid character status values."""
        if self.config and hasattr(self.config, "entity_rules"):
            return self.config.entity_rules.get("valid_character_statuses", [])

        # Default valid statuses if config not available
        return ["Active", "Injured", "Unconscious", "Dead", "Missing"]

    def _get_valid_quest_statuses(self) -> List[str]:
        """Get list of valid quest status values."""
        if self.config and hasattr(self.config, "entity_rules"):
            return self.config.entity_rules.get("valid_quest_statuses", [])

        # Default valid statuses if config not available
        return ["Active", "Completed", "Failed", "On Hold"]

    def _get_severity(self, issue_type: str) -> str:
        """Get severity level for a given issue type."""
        if self.config and hasattr(self.config, "severity_thresholds"):
            return self.config.severity_thresholds.get(issue_type, "warning")

        # Default severity mappings if config not available
        severity_map = {
            "missing_required_field": "error",
            "invalid_field_value": "warning",
            "inconsistent_relationship": "warning",
            "character_location_mismatch": "error"
        }

        return severity_map.get(issue_type, "warning")
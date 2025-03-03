"""
Relationship Validator Module

This module provides validation for relationships between entities within the game world,
ensuring that they are logically consistent and properly maintained.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple

logger = logging.getLogger("sentinel.validators.relationship")


class RelationshipValidator:
    """
    Validates relationships between entities in the game world.

    This validator checks that relationships between entities are logically consistent,
    bidirectional when appropriate, and properly maintained across all systems.
    """

    def __init__(self, game_manager, config=None):
        """
        Initialize the relationship validator.

        Args:
            game_manager: Reference to the GameManager instance
            config: Configuration settings for validation
        """
        self.game_manager = game_manager
        self.config = config
        logger.debug("RelationshipValidator initialized")

    def validate(self) -> List[Dict[str, Any]]:
        """
        Validate all relationships in the game world.

        Returns:
            List of issues found during validation
        """
        logger.info("Starting validation of all entity relationships")
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate relationships: game_manager not set")
            return issues

        # Check character-location relationships
        if self._should_verify_character_location_relationships():
            logger.debug("Validating character-location relationships")
            character_location_issues = self._validate_character_location_relationships()
            issues.extend(character_location_issues)

        # Check character-character relationships
        logger.debug("Validating character-character relationships")
        character_character_issues = self._validate_character_character_relationships()
        issues.extend(character_character_issues)

        # Check character-item relationships
        logger.debug("Validating character-item relationships")
        character_item_issues = self._validate_character_item_relationships()
        issues.extend(character_item_issues)

        # Check character-quest relationships
        logger.debug("Validating character-quest relationships")
        character_quest_issues = self._validate_character_quest_relationships()
        issues.extend(character_quest_issues)

        # Check bidirectional relationships
        if self._should_check_bidirectional_relationships():
            logger.debug("Validating bidirectional relationships")
            bidirectional_issues = self._validate_bidirectional_relationships()
            issues.extend(bidirectional_issues)

        logger.info(f"Relationship validation complete. Found {len(issues)} issues.")
        return issues

    def validate_relationship(self, entity1_id: str, entity2_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Validate a specific relationship between two entities.

        Args:
            entity1_id: ID of the first entity
            entity2_id: ID of the second entity
            relation_type: Optional specific relation type to check

        Returns:
            List of issues found during validation
        """
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate relationship: game_manager not set")
            return issues

        # Ensure both entities exist
        entity1_type = self._get_entity_type(entity1_id)
        entity2_type = self._get_entity_type(entity2_id)

        if entity1_type == "unknown":
            issues.append({
                "title": "Unknown Entity",
                "description": f"Entity with ID '{entity1_id}' not found in game state",
                "severity": "error",
                "entities": [entity1_id]
            })
            return issues

        if entity2_type == "unknown":
            issues.append({
                "title": "Unknown Entity",
                "description": f"Entity with ID '{entity2_id}' not found in game state",
                "severity": "error",
                "entities": [entity2_id]
            })
            return issues

        # If relation_type is specified, check that specific relationship
        if relation_type:
            if not self._is_valid_relationship_type(relation_type):
                issues.append({
                    "title": "Invalid Relationship Type",
                    "description": f"Relationship type '{relation_type}' is not recognized",
                    "severity": "warning",
                    "entities": [entity1_id, entity2_id],
                    "relation_type": relation_type
                })
                return issues

            has_relationship = self._check_relationship_exists(entity1_id, entity2_id, relation_type)

            if not has_relationship:
                issues.append({
                    "title": "Missing Relationship",
                    "description": f"Expected relationship '{relation_type}' from '{entity1_id}' to '{entity2_id}' not found",
                    "severity": "warning",
                    "entities": [entity1_id, entity2_id],
                    "relation_type": relation_type
                })

            # Check if this is a relationship that should be bidirectional
            if self._should_be_bidirectional(relation_type):
                has_reverse = self._check_relationship_exists(entity2_id, entity1_id, relation_type)

                if not has_reverse:
                    issues.append({
                        "title": "Non-Bidirectional Relationship",
                        "description": f"Relationship '{relation_type}' exists from '{entity1_id}' to '{entity2_id}' but not in reverse",
                        "severity": "warning",
                        "entities": [entity1_id, entity2_id],
                        "relation_type": relation_type
                    })
        else:
            # Check all relationships between these entities
            for relation_type in self._get_valid_relationship_types():
                relationship_issues = self.validate_relationship(entity1_id, entity2_id, relation_type)
                issues.extend(relationship_issues)

        return issues

    def _validate_character_location_relationships(self) -> List[Dict[str, Any]]:
        """
        Validate relationships between characters and locations.

        Returns:
            List of issues found
        """
        issues = []

        # Get all characters and their locations
        for character_id in self._get_all_character_ids():
            character = self._get_character(character_id)
            if not character or "location" not in character:
                continue

            location_id = character["location"]

            # Check if this location exists
            if not self._check_entity_exists(location_id):
                issues.append({
                    "title": "Invalid Location Reference",
                    "description": f"Character '{character_id}' references non-existent location: {location_id}",
                    "severity": "error",
                    "entities": [character_id],
                    "relation_type": "present_at"
                })
                continue

            # Check if character has 'present_at' relationship with this location
            has_relationship = self._check_relationship_exists(character_id, location_id, "present_at")

            if not has_relationship:
                issues.append({
                    "title": "Missing Location Relationship",
                    "description": f"Character '{character_id}' is located at '{location_id}' but has no 'present_at' relationship",
                    "severity": "error",
                    "entities": [character_id, location_id],
                    "relation_type": "present_at"
                })

            # Check if the location has this character in its character list
            location_has_character = self._location_has_character(location_id, character_id)

            if not location_has_character:
                issues.append({
                    "title": "Location Missing Character",
                    "description": f"Character '{character_id}' is located at '{location_id}' but is not in the location's character list",
                    "severity": "error",
                    "entities": [character_id, location_id],
                    "relation_type": "present_at"
                })

        # Check for characters in location lists but not actually at the location
        for location_id in self._get_all_location_ids():
            location = self._get_location(location_id)
            if not location or "characters" not in location or not location["characters"]:
                continue

            for character_id in location["characters"]:
                if not self._check_entity_exists(character_id):
                    issues.append({
                        "title": "Invalid Character Reference",
                        "description": f"Location '{location_id}' references non-existent character: {character_id}",
                        "severity": "error",
                        "entities": [location_id],
                        "relation_type": "present_at"
                    })
                    continue

                # Check if character's location field matches this location
                character_location_match = self._character_at_location(character_id, location_id)

                if not character_location_match:
                    issues.append({
                        "title": "Character Location Mismatch",
                        "description": f"Character '{character_id}' is in location '{location_id}' character list but has a different location field",
                        "severity": "error",
                        "entities": [character_id, location_id],
                        "relation_type": "present_at"
                    })

                # Check if character has relationship with this location
                has_relationship = self._check_relationship_exists(character_id, location_id, "present_at")

                if not has_relationship:
                    issues.append({
                        "title": "Missing Location Relationship",
                        "description": f"Character '{character_id}' is in location '{location_id}' character list but has no 'present_at' relationship",
                        "severity": "error",
                        "entities": [character_id, location_id],
                        "relation_type": "present_at"
                    })

        return issues

    def _validate_character_character_relationships(self) -> List[Dict[str, Any]]:
        """
        Validate relationships between characters.

        Returns:
            List of issues found
        """
        issues = []

        # Get relationships requiring bidirectionality
        bidirectional_relations = self._get_bidirectional_relationships()

        # For each character, check their relationships with other characters
        character_ids = self._get_all_character_ids()

        for i, character1_id in enumerate(character_ids):
            # Only check each relationship pair once
            for character2_id in character_ids[i+1:]:
                for relation_type in ["allied_with", "hostile_to", "neutral_to", "knows"]:
                    # Check forward relationship
                    has_forward = self._check_relationship_exists(character1_id, character2_id, relation_type)

                    # Check reverse relationship
                    has_reverse = self._check_relationship_exists(character2_id, character1_id, relation_type)

                    # If relation should be bidirectional, check consistency
                    if relation_type in bidirectional_relations:
                        if has_forward and not has_reverse:
                            issues.append({
                                "title": "Non-Bidirectional Relationship",
                                "description": f"Relationship '{relation_type}' exists from '{character1_id}' to '{character2_id}' but not in reverse",
                                "severity": "warning",
                                "entities": [character1_id, character2_id],
                                "relation_type": relation_type
                            })
                        elif has_reverse and not has_forward:
                            issues.append({
                                "title": "Non-Bidirectional Relationship",
                                "description": f"Relationship '{relation_type}' exists from '{character2_id}' to '{character1_id}' but not in reverse",
                                "severity": "warning",
                                "entities": [character2_id, character1_id],
                                "relation_type": relation_type
                            })

                    # For 'knows' relationship, check if characters are in the same location
                    if relation_type == "knows":
                        same_location = self._characters_in_same_location(character1_id, character2_id)

                        if same_location and not (has_forward or has_reverse):
                            issues.append({
                                "title": "Missing Knowledge Relationship",
                                "description": f"Characters '{character1_id}' and '{character2_id}' are in the same location but don't know each other",
                                "severity": "info",
                                "entities": [character1_id, character2_id],
                                "relation_type": "knows"
                            })

        return issues

    def _validate_character_item_relationships(self) -> List[Dict[str, Any]]:
        """
        Validate relationships between characters and items.

        Returns:
            List of issues found
        """
        issues = []

        # For each character, check their relationships with items
        for character_id in self._get_all_character_ids():
            character = self._get_character(character_id)
            if not character:
                continue

            # Check inventory consistency if it exists
            if "inventory" in character and character["inventory"]:
                for item_id in character["inventory"]:
                    # Check if item exists
                    if not self._check_entity_exists(item_id):
                        issues.append({
                            "title": "Invalid Item Reference",
                            "description": f"Character '{character_id}' inventory references non-existent item: {item_id}",
                            "severity": "error",
                            "entities": [character_id],
                            "relation_type": "has_item"
                        })
                        continue

                    # Check if character has 'has_item' relationship with this item
                    has_relationship = self._check_relationship_exists(character_id, item_id, "has_item")

                    if not has_relationship:
                        issues.append({
                            "title": "Missing Item Relationship",
                            "description": f"Character '{character_id}' has item '{item_id}' in inventory but no 'has_item' relationship",
                            "severity": "warning",
                            "entities": [character_id, item_id],
                            "relation_type": "has_item"
                        })

            # Check for items the character has a relationship with but not in inventory
            item_relationships = self._get_entity_relationships_by_type(character_id, "has_item")

            character_inventory = character.get("inventory", [])

            for item_id in item_relationships:
                if item_id not in character_inventory:
                    issues.append({
                        "title": "Inconsistent Item Possession",
                        "description": f"Character '{character_id}' has 'has_item' relationship with '{item_id}' but item is not in inventory",
                        "severity": "warning",
                        "entities": [character_id, item_id],
                        "relation_type": "has_item"
                    })

        return issues

    def _validate_character_quest_relationships(self) -> List[Dict[str, Any]]:
        """
        Validate relationships between characters and quests.

        Returns:
            List of issues found
        """
        issues = []

        # For each character, check their relationships with quests
        for character_id in self._get_all_character_ids():
            character = self._get_character(character_id)
            if not character:
                continue

            # Check quests consistency if it exists
            if "quests" in character and character["quests"]:
                for quest_id in character["quests"]:
                    # Check if quest exists
                    if not self._check_entity_exists(quest_id):
                        issues.append({
                            "title": "Invalid Quest Reference",
                            "description": f"Character '{character_id}' references non-existent quest: {quest_id}",
                            "severity": "error",
                            "entities": [character_id],
                            "relation_type": "on_quest"
                        })
                        continue

                    # Check if character has 'on_quest' relationship with this quest
                    has_relationship = self._check_relationship_exists(character_id, quest_id, "on_quest")

                    if not has_relationship:
                        issues.append({
                            "title": "Missing Quest Relationship",
                            "description": f"Character '{character_id}' has quest '{quest_id}' in quest list but no 'on_quest' relationship",
                            "severity": "warning",
                            "entities": [character_id, quest_id],
                            "relation_type": "on_quest"
                        })

            # Check for quests the character has a relationship with but not in quest list
            quest_relationships = self._get_entity_relationships_by_type(character_id, "on_quest")

            character_quests = character.get("quests", [])

            for quest_id in quest_relationships:
                if quest_id not in character_quests:
                    issues.append({
                        "title": "Inconsistent Quest Assignment",
                        "description": f"Character '{character_id}' has 'on_quest' relationship with '{quest_id}' but quest is not in quest list",
                        "severity": "warning",
                        "entities": [character_id, quest_id],
                        "relation_type": "on_quest"
                    })

                    # Also check if this quest exists
                    if not self._check_entity_exists(quest_id):
                        issues.append({
                            "title": "Invalid Quest Reference",
                            "description": f"Character '{character_id}' has relationship with non-existent quest: {quest_id}",
                            "severity": "error",
                            "entities": [character_id, quest_id],
                            "relation_type": "on_quest"
                        })

        return issues

    def _validate_bidirectional_relationships(self) -> List[Dict[str, Any]]:
        """
        Validate that relationships that should be bidirectional are consistent.

        Returns:
            List of issues found
        """
        issues = []

        # Get relationships requiring bidirectionality
        bidirectional_relations = self._get_bidirectional_relationships()

        if not bidirectional_relations:
            return issues

        # Get all relationships of these types from the game manager
        for relation_type in bidirectional_relations:
            try:
                relationships = self._get_all_relationships_by_type(relation_type)

                for entity1_id, entity2_id in relationships:
                    # Check for reverse relationship
                    has_reverse = self._check_relationship_exists(entity2_id, entity1_id, relation_type)

                    if not has_reverse:
                        issues.append({
                            "title": "Non-Bidirectional Relationship",
                            "description": f"Relationship '{relation_type}' exists from '{entity1_id}' to '{entity2_id}' but not in reverse",
                            "severity": "warning",
                            "entities": [entity1_id, entity2_id],
                            "relation_type": relation_type
                        })
            except Exception as e:
                logger.error(f"Error validating bidirectional relationships for type {relation_type}: {e}")
                continue

        return issues

    # Helper methods

    def _should_verify_character_location_relationships(self) -> bool:
        """Check if character-location relationships should be verified."""
        if self.config and hasattr(self.config, "relationship_rules"):
            return self.config.relationship_rules.get("verify_character_location_relationships", True)
        return True

    def _should_check_bidirectional_relationships(self) -> bool:
        """Check if bidirectional relationships should be verified."""
        if self.config and hasattr(self.config, "relationship_rules"):
            return self.config.relationship_rules.get("check_bidirectional", True)
        return True

    def _is_valid_relationship_type(self, relation_type: str) -> bool:
        """Check if a relationship type is valid."""
        valid_types = self._get_valid_relationship_types()
        return relation_type in valid_types

    def _get_valid_relationship_types(self) -> List[str]:
        """Get list of valid relationship types."""
        if self.config and hasattr(self.config, "relationship_rules"):
            return self.config.relationship_rules.get("valid_relationship_types", [])

        # Default valid relationship types if config not available
        return [
            "present_at", "knows", "has_item", "on_quest", "allied_with",
            "hostile_to", "neutral_to", "leads", "follows"
        ]

    def _get_bidirectional_relationships(self) -> List[str]:
        """Get list of relationship types that should be bidirectional."""
        if self.config and hasattr(self.config, "relationship_rules"):
            return self.config.relationship_rules.get("relationships_requiring_bidirectional", [])

        # Default bidirectional relationship types if config not available
        return ["allied_with", "hostile_to", "neutral_to"]

    def _should_be_bidirectional(self, relation_type: str) -> bool:
        """Check if a relationship type should be bidirectional."""
        bidirectional_types = self._get_bidirectional_relationships()
        return relation_type in bidirectional_types

    def _get_entity_type(self, entity_id: str) -> str:
        """Determine the type of an entity based on its ID."""
        if not self.game_manager:
            return "unknown"

        try:
            if hasattr(self.game_manager, "characters") and entity_id in self.game_manager.characters:
                return "character"
            elif hasattr(self.game_manager, "locations") and entity_id in self.game_manager.locations:
                return "location"
            elif hasattr(self.game_manager, "items") and entity_id in self.game_manager.items:
                return "item"
            elif hasattr(self.game_manager, "quests") and entity_id in self.game_manager.quests:
                return "quest"
        except Exception as e:
            logger.error(f"Error determining entity type for {entity_id}: {e}")

        return "unknown"

    def _check_entity_exists(self, entity_id: str) -> bool:
        """Check if an entity exists in the game."""
        return self._get_entity_type(entity_id) != "unknown"

    def _check_character_exists(self, character_id: str) -> bool:
        """Check if a character exists in the game."""
        if not self.game_manager:
            return False

        try:
            return hasattr(self.game_manager, "characters") and character_id in self.game_manager.characters
        except Exception as e:
            logger.error(f"Error checking character existence {character_id}: {e}")
            return False

    def _check_location_exists(self, location_id: str) -> bool:
        """Check if a location exists in the game."""
        if not self.game_manager:
            return False

        try:
            return hasattr(self.game_manager, "locations") and location_id in self.game_manager.locations
        except Exception as e:
            logger.error(f"Error checking location existence {location_id}: {e}")
            return False

    def _get_all_character_ids(self) -> List[str]:
        """Get IDs of all characters in the game."""
        if not self.game_manager:
            return []

        try:
            if hasattr(self.game_manager, "characters"):
                return list(self.game_manager.characters.keys())
        except Exception as e:
            logger.error(f"Error getting character IDs: {e}")

        return []

    def _get_all_location_ids(self) -> List[str]:
        """Get IDs of all locations in the game."""
        if not self.game_manager:
            return []

        try:
            if hasattr(self.game_manager, "locations"):
                return list(self.game_manager.locations.keys())
        except Exception as e:
            logger.error(f"Error getting location IDs: {e}")

        return []

    def _get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get character data by ID."""
        if not self.game_manager:
            return None

        try:
            if hasattr(self.game_manager, "characters"):
                return self.game_manager.characters.get(character_id)
        except Exception as e:
            logger.error(f"Error getting character {character_id}: {e}")

        return None

    def _get_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get location data by ID."""
        if not self.game_manager:
            return None

        try:
            if hasattr(self.game_manager, "locations"):
                return self.game_manager.locations.get(location_id)
        except Exception as e:
            logger.error(f"Error getting location {location_id}: {e}")

        return None

    def _check_relationship_exists(self, entity1_id: str, entity2_id: str, relation_type: str) -> bool:
        """Check if a relationship exists between two entities."""
        if not self.game_manager:
            return False

        try:
            if hasattr(self.game_manager, "entity_relationship_manager"):
                return self.game_manager.entity_relationship_manager.has_relationship(
                    entity1_id, entity2_id, relation_type
                )
        except Exception as e:
            logger.error(f"Error checking relationship {relation_type} from {entity1_id} to {entity2_id}: {e}")

        return False

    def _get_entity_relationships_by_type(self, entity_id: str, relation_type: str) -> List[str]:
        """Get all entities that have a specific relationship with the given entity."""
        if not self.game_manager:
            return []

        try:
            if hasattr(self.game_manager, "entity_relationship_manager"):
                relations = self.game_manager.entity_relationship_manager.get_relations_by_type(entity_id, relation_type)
                return relations
        except Exception as e:
            logger.error(f"Error getting {relation_type} relationships for {entity_id}: {e}")

        return []

    def _get_all_relationships_by_type(self, relation_type: str) -> List[Tuple[str, str]]:
        """Get all entity pairs with a specific relationship type."""
        if not self.game_manager:
            return []

        try:
            if hasattr(self.game_manager, "entity_relationship_manager"):
                return self.game_manager.entity_relationship_manager.get_all_relations_by_type(relation_type)
        except Exception as e:
            logger.error(f"Error getting all {relation_type} relationships: {e}")

        return []

    def _location_has_character(self, location_id: str, character_id: str) -> bool:
        """Check if a location has a character in its character list."""
        location = self._get_location(location_id)
        if not location:
            return False

        return "characters" in location and character_id in location["characters"]

    def _character_at_location(self, character_id: str, location_id: str) -> bool:
        """Check if a character's location field points to a given location."""
        character = self._get_character(character_id)
        if not character:
            return False

        return "location" in character and character["location"] == location_id

    def _characters_in_same_location(self, character1_id: str, character2_id: str) -> bool:
        """Check if two characters are in the same location."""
        character1 = self._get_character(character1_id)
        character2 = self._get_character(character2_id)

        if not character1 or not character2:
            return False

        if "location" not in character1 or "location" not in character2:
            return False

        return character1["location"] == character2["location"]
"""
World State Validator Module

This module provides validation for the overall game world state,
ensuring that locations, connections, and entities are logically consistent.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, deque

logger = logging.getLogger("sentinel.validators.world_state")


class WorldStateValidator:
    """
    Validates the overall game world state.

    This validator ensures that locations, connections, and entities
    are logically consistent within the game world as a whole.
    """

    def __init__(self, game_manager, dungeon_master=None, config=None):
        """
        Initialize the world state validator.

        Args:
            game_manager: Reference to the GameManager instance
            dungeon_master: Reference to the DungeonMaster instance
            config: Configuration settings for validation
        """
        self.game_manager = game_manager
        self.dungeon_master = dungeon_master
        self.config = config
        logger.debug("WorldStateValidator initialized")

    def validate(self) -> List[Dict[str, Any]]:
        """
        Validate the overall game world state.

        Returns:
            List of issues found during validation
        """
        logger.info("Starting validation of world state")
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate world state: game_manager not set")
            return issues

        # Check location connections consistency
        if self._should_verify_location_connections():
            logger.debug("Validating location connections")
            connection_issues = self._validate_location_connections()
            issues.extend(connection_issues)

        # Check for isolated locations
        if self._should_check_isolated_locations():
            logger.debug("Checking for isolated locations")
            isolation_issues = self._check_for_isolated_locations()
            issues.extend(isolation_issues)

        # Check for orphaned entities
        if self._should_check_orphaned_entities():
            logger.debug("Checking for orphaned entities")
            orphan_issues = self._check_for_orphaned_entities()
            issues.extend(orphan_issues)

        # Check location character lists consistency
        if self._should_verify_location_character_lists():
            logger.debug("Validating location character lists")
            character_list_issues = self._validate_location_character_lists()
            issues.extend(character_list_issues)

        logger.info(f"World state validation complete. Found {len(issues)} issues.")
        return issues

    def validate_location(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Validate a specific location for consistency.

        Args:
            location_id: The ID of the location to validate

        Returns:
            List of issues found during validation
        """
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate location: game_manager not set")
            return issues

        # Check if the location exists
        location = self._get_location(location_id)
        if not location:
            issues.append({
                "title": "Location Not Found",
                "description": f"Location with ID {location_id} not found in game state",
                "severity": "error",
                "entities": [location_id]
            })
            return issues

        # Check connections validity
        connection_issues = self._validate_location_connections_for_one(location_id)
        issues.extend(connection_issues)

        # Check character list consistency
        character_list_issues = self._validate_location_character_list(location_id)
        issues.extend(character_list_issues)

        # Check if location is isolated
        if self._is_location_isolated(location_id):
            issues.append({
                "title": "Isolated Location",
                "description": f"Location '{location_id}' has no connections to other locations",
                "severity": self._get_severity("isolated_location"),
                "entities": [location_id]
            })

        return issues

    def _validate_location_connections(self) -> List[Dict[str, Any]]:
        """
        Validate connections between locations for consistency.

        Returns:
            List of issues found during validation
        """
        issues = []

        # Get all locations
        for location_id in self._get_all_location_ids():
            location_issues = self._validate_location_connections_for_one(location_id)
            issues.extend(location_issues)

        return issues

    def _validate_location_connections_for_one(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Validate connections for a specific location.

        Args:
            location_id: The ID of the location to validate

        Returns:
            List of issues found
        """
        issues = []

        location = self._get_location(location_id)
        if not location:
            return []

        # Check if connections exist and are valid
        if "connections" in location and location["connections"]:
            for connected_id, connection_info in location["connections"].items():
                # Check if connected location exists
                if not self._check_location_exists(connected_id):
                    issues.append({
                        "title": "Invalid Connection Reference",
                        "description": f"Location '{location_id}' references non-existent connected location: {connected_id}",
                        "severity": "error",
                        "entities": [location_id],
                        "connection": connected_id
                    })
                    continue

                # Check if the connection is bidirectional (if it should be)
                if self._should_connections_be_bidirectional():
                    connected_location = self._get_location(connected_id)

                    if not connected_location or "connections" not in connected_location:
                        issues.append({
                            "title": "Non-bidirectional Connection",
                            "description": f"Location '{location_id}' connects to '{connected_id}' but not vice versa",
                            "severity": "warning",
                            "entities": [location_id, connected_id]
                        })
                    elif location_id not in connected_location["connections"]:
                        issues.append({
                            "title": "Non-bidirectional Connection",
                            "description": f"Location '{location_id}' connects to '{connected_id}' but not vice versa",
                            "severity": "warning",
                            "entities": [location_id, connected_id]
                        })

        return issues

    def _check_for_isolated_locations(self) -> List[Dict[str, Any]]:
        """
        Check for locations that have no connections to other locations.

        Returns:
            List of issues for isolated locations
        """
        issues = []

        # Build a graph of location connections
        connection_graph = self._build_location_connection_graph()

        # Find isolated locations (nodes with no edges)
        for location_id in self._get_all_location_ids():
            if location_id not in connection_graph or not connection_graph[location_id]:
                issues.append({
                    "title": "Isolated Location",
                    "description": f"Location '{location_id}' has no connections to other locations",
                    "severity": self._get_severity("isolated_location"),
                    "entities": [location_id]
                })

        return issues

    def _is_location_isolated(self, location_id: str) -> bool:
        """
        Check if a specific location is isolated (has no connections).

        Args:
            location_id: The ID of the location to check

        Returns:
            True if the location is isolated, False otherwise
        """
        location = self._get_location(location_id)
        if not location:
            return False

        has_connections = "connections" in location and location["connections"]
        return not has_connections

    def _check_for_orphaned_entities(self) -> List[Dict[str, Any]]:
        """
        Check for entities (characters, items) that are not properly placed in the world.

        Returns:
            List of issues for orphaned entities
        """
        issues = []

        # Check for characters without a valid location
        for character_id in self._get_all_character_ids():
            character = self._get_character(character_id)
            if not character:
                continue

            # Check if character has a location
            if "location" not in character or not character["location"]:
                issues.append({
                    "title": "Character Missing Location",
                    "description": f"Character '{character_id}' has no location assigned",
                    "severity": self._get_severity("orphaned_entity"),
                    "entities": [character_id]
                })
                continue

            location_id = character["location"]

            # Check if the location exists
            if not self._check_location_exists(location_id):
                issues.append({
                    "title": "Character at Invalid Location",
                    "description": f"Character '{character_id}' is at non-existent location '{location_id}'",
                    "severity": "error",
                    "entities": [character_id]
                })

        # Check for items that are not placed somewhere (if item tracking is used)
        if hasattr(self.game_manager, "items"):
            for item_id in self._get_all_item_ids():
                item = self._get_item(item_id)
                if not item:
                    continue

                # Logic depends on how items are tracked (could be in character inventories, at locations, etc.)
                is_placed = self._is_item_placed(item_id)

                if not is_placed:
                    issues.append({
                        "title": "Unplaced Item",
                        "description": f"Item '{item_id}' is not placed in the world (not held by a character or at a location)",
                        "severity": self._get_severity("orphaned_entity"),
                        "entities": [item_id]
                    })

        return issues

    def _validate_location_character_lists(self) -> List[Dict[str, Any]]:
        """
        Validate character lists in locations.

        Returns:
            List of issues found
        """
        issues = []

        # Check all locations
        for location_id in self._get_all_location_ids():
            location_issues = self._validate_location_character_list(location_id)
            issues.extend(location_issues)

        return issues

    def _validate_location_character_list(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Validate character list for a specific location.

        Args:
            location_id: The ID of the location to validate

        Returns:
            List of issues found
        """
        issues = []

        location = self._get_location(location_id)
        if not location:
            return []

        # Get all characters at this location (based on their location field)
        characters_at_location = self._get_characters_at_location(location_id)

        # Check if the location's character list matches
        if "characters" not in location or not location["characters"]:
            if characters_at_location:
                issues.append({
                    "title": "Missing Character List",
                    "description": f"Location '{location_id}' has no character list but characters are located there",
                    "severity": "warning",
                    "entities": [location_id] + characters_at_location,
                    "missing_characters": characters_at_location
                })
        else:
            # Check for characters in location list but not actually there
            for character_id in location["characters"]:
                if not self._check_character_exists(character_id):
                    issues.append({
                        "title": "Invalid Character Reference",
                        "description": f"Location '{location_id}' lists non-existent character: {character_id}",
                        "severity": "error",
                        "entities": [location_id],
                        "invalid_character": character_id
                    })
                elif character_id not in characters_at_location:
                    issues.append({
                        "title": "Character Location Mismatch",
                        "description": f"Location '{location_id}' lists character '{character_id}' but character's location field points elsewhere",
                        "severity": "error",
                        "entities": [location_id, character_id]
                    })

            # Check for characters at location but not in list
            for character_id in characters_at_location:
                if character_id not in location["characters"]:
                    issues.append({
                        "title": "Missing Character in Location List",
                        "description": f"Character '{character_id}' is at location '{location_id}' but not in location's character list",
                        "severity": "error",
                        "entities": [location_id, character_id]
                    })

        return issues

    # Helper methods

    def _should_verify_location_connections(self) -> bool:
        """Check if location connections should be verified."""
        if self.config and hasattr(self.config, "world_state_rules"):
            return self.config.world_state_rules.get("verify_location_connections", True)
        return True

    def _should_verify_location_character_lists(self) -> bool:
        """Check if location character lists should be verified."""
        if self.config and hasattr(self.config, "world_state_rules"):
            return self.config.world_state_rules.get("verify_location_character_lists", True)
        return True

    def _should_check_isolated_locations(self) -> bool:
        """Check if isolated locations should be identified."""
        if self.config and hasattr(self.config, "world_state_rules"):
            return self.config.world_state_rules.get("check_isolated_locations", True)
        return True

    def _should_check_orphaned_entities(self) -> bool:
        """Check if orphaned entities should be identified."""
        if self.config and hasattr(self.config, "world_state_rules"):
            return self.config.world_state_rules.get("check_orphaned_entities", True)
        return True

    def _should_connections_be_bidirectional(self) -> bool:
        """Check if location connections should be bidirectional."""
        if self.config and hasattr(self.config, "world_state_rules"):
            return self.config.world_state_rules.get("connections_should_be_bidirectional", True)
        return True

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

    def _get_all_item_ids(self) -> List[str]:
        """Get IDs of all items in the game."""
        if not self.game_manager or not hasattr(self.game_manager, "items"):
            return []

        try:
            return list(self.game_manager.items.keys())
        except Exception as e:
            logger.error(f"Error getting item IDs: {e}")

        return []

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

    def _get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item data by ID."""
        if not self.game_manager or not hasattr(self.game_manager, "items"):
            return None

        try:
            return self.game_manager.items.get(item_id)
        except Exception as e:
            logger.error(f"Error getting item {item_id}: {e}")

        return None

    def _check_location_exists(self, location_id: str) -> bool:
        """Check if a location exists in the game."""
        if not self.game_manager:
            return False

        try:
            if hasattr(self.game_manager, "locations"):
                return location_id in self.game_manager.locations
        except Exception as e:
            logger.error(f"Error checking location existence {location_id}: {e}")

        return False

    def _check_character_exists(self, character_id: str) -> bool:
        """Check if a character exists in the game."""
        if not self.game_manager:
            return False

        try:
            if hasattr(self.game_manager, "characters"):
                return character_id in self.game_manager.characters
        except Exception as e:
            logger.error(f"Error checking character existence {character_id}: {e}")

        return False

    def _build_location_connection_graph(self) -> Dict[str, List[str]]:
        """
        Build a graph of location connections.

        Returns:
            Dictionary mapping location IDs to lists of connected location IDs
        """
        graph = defaultdict(list)

        # Add all locations to the graph
        for location_id in self._get_all_location_ids():
            location = self._get_location(location_id)
            if not location:
                continue

            # Add edges for each connection
            if "connections" in location and location["connections"]:
                for connected_id in location["connections"]:
                    if self._check_location_exists(connected_id):
                        graph[location_id].append(connected_id)

        return graph

    def _get_characters_at_location(self, location_id: str) -> List[str]:
        """
        Get IDs of all characters at a specific location.

        Args:
            location_id: The ID of the location

        Returns:
            List of character IDs
        """
        characters = []

        for character_id in self._get_all_character_ids():
            character = self._get_character(character_id)
            if not character:
                continue

            if "location" in character and character["location"] == location_id:
                characters.append(character_id)

        return characters

    def _is_item_placed(self, item_id: str) -> bool:
        """
        Check if an item is placed somewhere in the game world.

        Args:
            item_id: The ID of the item to check

        Returns:
            True if the item is placed (held by character or at a location), False otherwise
        """
        # This implementation depends on how items are tracked in the game
        # Could check character inventories, location items, etc.

        # Check if any character has this item
        for character_id in self._get_all_character_ids():
            character = self._get_character(character_id)
            if not character:
                continue

            if "inventory" in character and item_id in character["inventory"]:
                return True

        # Check if item is at any location (if locations track items)
        for location_id in self._get_all_location_ids():
            location = self._get_location(location_id)
            if not location:
                continue

            if "items" in location and item_id in location["items"]:
                return True

        # Check item relationships
        try:
            if hasattr(self.game_manager, "entity_relationship_manager"):
                # Check if any entity has a "has_item" relationship with this item
                has_relationship = False
                for entity_id in self._get_all_character_ids() + self._get_all_location_ids():
                    if self.game_manager.entity_relationship_manager.has_relationship(entity_id, item_id, "has_item"):
                        has_relationship = True
                        break

                if has_relationship:
                    return True
        except Exception as e:
            logger.error(f"Error checking item relationships for {item_id}: {e}")

        return False

    def _get_severity(self, issue_type: str) -> str:
        """Get severity level for a given issue type."""
        if self.config and hasattr(self.config, "severity_thresholds"):
            return self.config.severity_thresholds.get(issue_type, "warning")

        # Default severity mappings if config not available
        severity_map = {
            "isolated_location": "info",
            "orphaned_entity": "warning",
            "character_location_mismatch": "error"
        }

        return severity_map.get(issue_type, "warning")
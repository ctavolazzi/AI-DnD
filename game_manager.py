import logging
from typing import Dict, List, Set, Any, Optional, Union
import datetime
import os
import json
import re

class KnowledgeGraph:
    """
    Tracks what entities know about other entities and events.
    Implements "theory of mind" - entities only know what they would logically know.
    """
    def __init__(self):
        self.knowledge = {}  # entity -> {known_entity -> last_known_state}
        self.logger = logging.getLogger("knowledge_graph")

    def entity_knows_about(self, entity: str, target: str) -> bool:
        """Check if an entity knows about a target entity."""
        if entity not in self.knowledge:
            return False
        return target in self.knowledge[entity]

    def get_entity_knowledge(self, entity: str, target: str) -> Optional[Dict]:
        """Get what an entity knows about a target."""
        if not self.entity_knows_about(entity, target):
            return None
        return self.knowledge[entity][target]

    def update_entity_knowledge(self, entity: str, target: str, knowledge: Dict):
        """Update what an entity knows about a target."""
        if entity not in self.knowledge:
            self.knowledge[entity] = {}
        self.knowledge[entity][target] = knowledge
        self.logger.debug(f"{entity} now knows about {target}: {knowledge}")

    def propagate_knowledge(self, source: str, target: str, entities: List[str]):
        """Propagate knowledge about a target from source to other entities."""
        if source not in self.knowledge or target not in self.knowledge[source]:
            return

        knowledge = self.knowledge[source][target]
        for entity in entities:
            if entity != source:
                self.update_entity_knowledge(entity, target, knowledge)

    def forget_entity(self, entity: str, target: str):
        """Entity forgets about a target."""
        if entity in self.knowledge and target in self.knowledge[entity]:
            del self.knowledge[entity][target]
            self.logger.debug(f"{entity} has forgotten about {target}")


class EntityRelationshipManager:
    """
    Manages relationships between entities (characters, locations, items, etc.)
    """
    def __init__(self):
        self.relationships = {}  # entity -> {related_entity -> relationship_type}
        self.logger = logging.getLogger("entity_relationship")

    def add_relationship(self, entity1: str, entity2: str, relationship_type: str, bidirectional: bool = True):
        """Add a relationship between two entities."""
        if entity1 not in self.relationships:
            self.relationships[entity1] = {}

        self.relationships[entity1][entity2] = relationship_type
        self.logger.debug(f"Added relationship: {entity1} -> {entity2} ({relationship_type})")

        if bidirectional:
            if entity2 not in self.relationships:
                self.relationships[entity2] = {}
            self.relationships[entity2][entity1] = relationship_type
            self.logger.debug(f"Added relationship: {entity2} -> {entity1} ({relationship_type})")

    def remove_relationship(self, entity1: str, entity2: str, bidirectional: bool = True):
        """Remove a relationship between two entities."""
        if entity1 in self.relationships and entity2 in self.relationships[entity1]:
            del self.relationships[entity1][entity2]
            self.logger.debug(f"Removed relationship: {entity1} -> {entity2}")

        if bidirectional and entity2 in self.relationships and entity1 in self.relationships[entity2]:
            del self.relationships[entity2][entity1]
            self.logger.debug(f"Removed relationship: {entity2} -> {entity1}")

    def get_related_entities(self, entity: str, relationship_type: Optional[str] = None) -> List[str]:
        """Get all entities related to the given entity, optionally filtered by relationship type."""
        if entity not in self.relationships:
            return []

        if relationship_type is None:
            return list(self.relationships[entity].keys())

        return [e for e, r in self.relationships[entity].items() if r == relationship_type]

    def get_relationship(self, entity1: str, entity2: str) -> Optional[str]:
        """Get the relationship between two entities."""
        if entity1 not in self.relationships or entity2 not in self.relationships[entity1]:
            return None
        return self.relationships[entity1][entity2]


class GameManager:
    """
    Central manager for game state that maintains logical consistency and entity knowledge.
    Handles updates across all game entities and ensures proper linking.
    """
    def __init__(self, obsidian_logger, event_manager):
        self.obsidian = obsidian_logger
        self.event_manager = event_manager
        self.entities = {
            "characters": {},
            "locations": {},
            "items": {},
            "events": {},
            "quests": {}
        }
        self.knowledge_graph = KnowledgeGraph()
        self.relationship_manager = EntityRelationshipManager()
        self.logger = logging.getLogger("game_manager")

        # Subscribe to events
        self._register_event_handlers()

    def _register_event_handlers(self):
        """Register handlers for all event types."""
        self.event_manager.subscribe("character_created", self._on_character_created)
        self.event_manager.subscribe("character_updated", self._on_character_updated)
        self.event_manager.subscribe("character_died", self._on_character_died)
        self.event_manager.subscribe("location_created", self._on_location_created)
        self.event_manager.subscribe("location_updated", self._on_location_updated)
        self.event_manager.subscribe("event_occurred", self._on_event_occurred)
        self.event_manager.subscribe("quest_created", self._on_quest_created)
        self.event_manager.subscribe("quest_updated", self._on_quest_updated)
        self.event_manager.subscribe("item_created", self._on_item_created)
        self.event_manager.subscribe("item_updated", self._on_item_updated)

    def _on_character_created(self, character_data):
        """Handle character creation event."""
        name = character_data["name"]
        self.entities["characters"][name] = character_data
        self.logger.info(f"Character registered: {name}")

        # A character knows about themselves
        self.knowledge_graph.update_entity_knowledge(name, name, character_data)

        # Initial relationships with starting location if any
        if "location" in character_data and character_data["location"]:
            location = character_data["location"]
            self.relationship_manager.add_relationship(name, location, "present_at")
            self.knowledge_graph.update_entity_knowledge(name, location,
                self.entities["locations"].get(location, {"name": location}))

    def _on_character_updated(self, character_data):
        """Handle character update event."""
        name = character_data["name"]
        if name in self.entities["characters"]:
            old_data = self.entities["characters"][name]
            self.entities["characters"][name] = character_data
            self.logger.info(f"Character updated: {name}")

            # Character knows their own updated state
            self.knowledge_graph.update_entity_knowledge(name, name, character_data)

            # Check for location change
            if "location" in character_data and "location" in old_data:
                if character_data["location"] != old_data["location"]:
                    if old_data["location"]:
                        self.relationship_manager.remove_relationship(name, old_data["location"])
                    if character_data["location"]:
                        self.relationship_manager.add_relationship(name, character_data["location"], "present_at")
                        # Character learns about new location
                        self.knowledge_graph.update_entity_knowledge(name, character_data["location"],
                            self.entities["locations"].get(character_data["location"],
                                                        {"name": character_data["location"]}))

    def _on_character_died(self, character_data):
        """Handle character death event."""
        name = character_data["name"]
        if name in self.entities["characters"]:
            self.entities["characters"][name] = character_data
            self.logger.info(f"Character died: {name}")

            # Update their relationships and knowledge
            location = character_data.get("location")
            if location:
                # Inform other characters at this location about the death
                chars_at_location = self.relationship_manager.get_related_entities(location, "present_at")
                for char in chars_at_location:
                    if char != name:  # Don't update the dead character
                        self.knowledge_graph.update_entity_knowledge(char, name, character_data)
                        self.logger.debug(f"{char} witnessed death of {name}")

    def _on_location_created(self, location_data):
        """Handle location creation event."""
        name = location_data["name"]
        self.entities["locations"][name] = location_data
        self.logger.info(f"Location registered: {name}")

    def _on_location_updated(self, location_data):
        """Handle location update event."""
        name = location_data["name"]
        if name in self.entities["locations"]:
            self.entities["locations"][name] = location_data
            self.logger.info(f"Location updated: {name}")

            # Update knowledge for characters at this location
            chars_at_location = self.relationship_manager.get_related_entities(name, "present_at")
            for char in chars_at_location:
                self.knowledge_graph.update_entity_knowledge(char, name, location_data)

    def _on_event_occurred(self, event_data):
        """Handle event occurrence."""
        name = event_data["name"]
        self.entities["events"][name] = event_data
        self.logger.info(f"Event occurred: {name}")

        # Update knowledge for participants
        participants = event_data.get("participants", [])
        location = event_data.get("location")

        # Characters present learn about the event
        if location:
            chars_at_location = self.relationship_manager.get_related_entities(location, "present_at")
            for char in chars_at_location:
                if char in participants or not participants:  # If no specific participants or char is a participant
                    self.knowledge_graph.update_entity_knowledge(char, name, event_data)
                    self.logger.debug(f"{char} knows about event {name}")

            # Add relationship between event and location
            self.relationship_manager.add_relationship(name, location, "occurred_at", bidirectional=True)

    def _on_quest_created(self, quest_data):
        """Handle quest creation."""
        name = quest_data["name"]
        self.entities["quests"][name] = quest_data
        self.logger.info(f"Quest registered: {name}")

    def _on_quest_updated(self, quest_data):
        """Handle quest update."""
        name = quest_data["name"]
        if name in self.entities["quests"]:
            self.entities["quests"][name] = quest_data
            self.logger.info(f"Quest updated: {name}")

    def _on_item_created(self, item_data):
        """Handle item creation."""
        name = item_data["name"]
        self.entities["items"][name] = item_data
        self.logger.info(f"Item registered: {name}")

    def _on_item_updated(self, item_data):
        """Handle item update."""
        name = item_data["name"]
        if name in self.entities["items"]:
            self.entities["items"][name] = item_data
            self.logger.info(f"Item updated: {name}")

    def get_entity(self, entity_type: str, name: str) -> Optional[Dict]:
        """Get entity data by type and name."""
        if entity_type not in self.entities or name not in self.entities[entity_type]:
            return None
        return self.entities[entity_type][name]

    def get_character_knowledge(self, character: str, target_type: str, target_name: str) -> Optional[Dict]:
        """Get what a character knows about a target entity."""
        # First check if the character exists
        if character not in self.entities["characters"]:
            return None

        # Then check what they know
        return self.knowledge_graph.get_entity_knowledge(character, target_name)

    def notify_entities_at_location(self, location: str, event_data: Dict, exclude: List[str] = None):
        """Notify all entities at a location about an event."""
        if exclude is None:
            exclude = []

        chars_at_location = self.relationship_manager.get_related_entities(location, "present_at")
        for char in chars_at_location:
            if char not in exclude:
                self.knowledge_graph.update_entity_knowledge(char, event_data["name"], event_data)
                self.logger.debug(f"Notified {char} about {event_data['name']}")

    def handle_character_movement(self, character: str, from_location: str, to_location: str):
        """Handle a character moving from one location to another."""
        if character not in self.entities["characters"]:
            return

        # Update relationships
        if from_location:
            self.relationship_manager.remove_relationship(character, from_location)

        if to_location:
            self.relationship_manager.add_relationship(character, to_location, "present_at")

            # Character learns about the new location
            if to_location in self.entities["locations"]:
                self.knowledge_graph.update_entity_knowledge(character, to_location,
                    self.entities["locations"][to_location])

            # Characters at the new location learn about the arrival
            chars_at_location = self.relationship_manager.get_related_entities(to_location, "present_at")
            for char in chars_at_location:
                if char != character:
                    self.knowledge_graph.update_entity_knowledge(char, character,
                        self.entities["characters"][character])

            # Create an arrival event
            event_data = {
                "name": f"Arrival-{character}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "Movement",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": to_location,
                "description": f"{character} arrives at {to_location}.",
                "participants": [character]
            }

            # Log the event
            self.obsidian.log_event_with_event(event_data, self.event_manager)

    def update_entity_file(self, entity_type: str, entity_name: str):
        """Update the entity file in Obsidian with latest data."""
        if entity_type not in self.entities or entity_name not in self.entities[entity_type]:
            return False

        entity_data = self.entities[entity_type][entity_name]

        # Use appropriate logger method based on entity type
        if entity_type == "characters":
            self.obsidian.log_character_with_event(entity_data, self.event_manager)
        elif entity_type == "locations":
            self.obsidian.log_location_with_event(entity_data, self.event_manager)
        elif entity_type == "events":
            self.obsidian.log_event_with_event(entity_data, self.event_manager)
        elif entity_type == "quests":
            self.obsidian.log_quest_with_event(entity_data, self.event_manager)
        elif entity_type == "items":
            self.obsidian.log_item_with_event(entity_data, self.event_manager)

        return True
"""
Narrative Consistency Validator Module

This module provides validation for the narrative consistency of the game,
ensuring that the story elements, character knowledge, and plot progression
are logically consistent.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

logger = logging.getLogger("sentinel.validators.narrative")


class NarrativeConsistencyValidator:
    """
    Validates the consistency of the game narrative.

    This validator ensures that story elements, character knowledge,
    and plot progression remain logically consistent throughout the game.
    """

    def __init__(self, game_manager, dungeon_master=None, config=None):
        """
        Initialize the narrative consistency validator.

        Args:
            game_manager: Reference to the GameManager instance
            dungeon_master: Reference to the DungeonMaster instance
            config: Configuration settings for validation
        """
        self.game_manager = game_manager
        self.dungeon_master = dungeon_master
        self.config = config
        self.previous_states = []  # Store previous states for continuity checks
        logger.debug("NarrativeConsistencyValidator initialized")

    def validate(self) -> List[Dict[str, Any]]:
        """
        Validate the narrative consistency of the game.

        Returns:
            List of issues found during validation
        """
        logger.info("Starting validation of narrative consistency")
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate narrative: game_manager not set")
            return issues

        # Check character knowledge consistency
        if self._should_check_character_knowledge():
            logger.debug("Validating character knowledge consistency")
            knowledge_issues = self._validate_character_knowledge()
            issues.extend(knowledge_issues)

        # Check quest progression consistency
        if self._should_check_quest_progression():
            logger.debug("Validating quest progression consistency")
            quest_issues = self._validate_quest_progression()
            issues.extend(quest_issues)

        # Check narrative continuity
        if self._should_check_narrative_continuity() and self.previous_states:
            logger.debug("Validating narrative continuity")
            continuity_issues = self._validate_narrative_continuity()
            issues.extend(continuity_issues)

        # Store current state for future continuity checks
        self._store_current_state_snapshot()

        logger.info(f"Narrative consistency validation complete. Found {len(issues)} issues.")
        return issues

    def validate_character_knowledge(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Validate the knowledge consistency for a specific character.

        Args:
            character_id: The ID of the character to validate

        Returns:
            List of issues found during validation
        """
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate character knowledge: game_manager not set")
            return issues

        # Check if character exists
        character = self._get_character(character_id)
        if not character:
            issues.append({
                "title": "Character Not Found",
                "description": f"Character with ID {character_id} not found in game state",
                "severity": "error",
                "entities": [character_id]
            })
            return issues

        # Check character knowledge against facts they should know
        knowledge_issues = self._validate_single_character_knowledge(character_id)
        issues.extend(knowledge_issues)

        return issues

    def validate_quest(self, quest_id: str) -> List[Dict[str, Any]]:
        """
        Validate the consistency of a specific quest.

        Args:
            quest_id: The ID of the quest to validate

        Returns:
            List of issues found during validation
        """
        issues = []

        if not self.game_manager:
            logger.warning("Cannot validate quest: game_manager not set")
            return issues

        # Check if quest exists
        quest = self._get_quest(quest_id)
        if not quest:
            issues.append({
                "title": "Quest Not Found",
                "description": f"Quest with ID {quest_id} not found in game state",
                "severity": "error",
                "entities": [quest_id]
            })
            return issues

        # Check quest progression logic
        progression_issues = self._validate_single_quest_progression(quest_id)
        issues.extend(progression_issues)

        return issues

    def record_state_change(self, entity_id: str, field: str, old_value: Any, new_value: Any):
        """
        Record a significant state change for continuity checking.

        Args:
            entity_id: The ID of the entity being changed
            field: The field/attribute that changed
            old_value: The previous value
            new_value: The new value
        """
        logger.debug(f"Recording state change: {entity_id}.{field} changed from '{old_value}' to '{new_value}'")
        change_record = {
            "entity_id": entity_id,
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "timestamp": self._get_current_timestamp()
        }

        # Store this change for later continuity checks
        if not hasattr(self, "state_changes"):
            self.state_changes = []

        self.state_changes.append(change_record)

        # Limit the number of stored changes to prevent memory issues
        max_changes = 1000
        if len(self.state_changes) > max_changes:
            self.state_changes = self.state_changes[-max_changes:]

    def _validate_character_knowledge(self) -> List[Dict[str, Any]]:
        """
        Validate knowledge consistency for all characters.

        Returns:
            List of issues found during validation
        """
        issues = []

        # Check each character's knowledge
        for character_id in self._get_all_character_ids():
            character_issues = self._validate_single_character_knowledge(character_id)
            issues.extend(character_issues)

        return issues

    def _validate_single_character_knowledge(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Validate knowledge consistency for a specific character.

        Args:
            character_id: The ID of the character to validate

        Returns:
            List of issues found
        """
        issues = []

        character = self._get_character(character_id)
        if not character:
            return []

        # Check character's memory against facts they should know
        if "memory" in character and hasattr(self.game_manager, "facts"):
            character_memory = character["memory"]

            # Get facts the character should know based on their location history and interactions
            facts_should_know = self._get_facts_character_should_know(character_id)

            # Check for important facts missing from memory
            for fact_id in facts_should_know:
                fact = self.game_manager.facts.get(fact_id)
                if not fact:
                    continue

                # Check if the character's memory contains this fact
                fact_in_memory = self._is_fact_in_memory(fact, character_memory)

                if not fact_in_memory:
                    issues.append({
                        "title": "Missing Knowledge",
                        "description": f"Character '{character_id}' should know fact '{fact.get('name', fact_id)}' but it's not in their memory",
                        "severity": self._get_severity("missing_knowledge"),
                        "entities": [character_id],
                        "fact": fact_id
                    })

        # Check if character knows things they shouldn't
        if "memory" in character and hasattr(self.game_manager, "facts"):
            character_memory = character["memory"]

            # Get facts the character should NOT know
            facts_should_not_know = self._get_facts_character_should_not_know(character_id)

            # Check for facts in memory that shouldn't be there
            for fact_id in facts_should_not_know:
                fact = self.game_manager.facts.get(fact_id)
                if not fact:
                    continue

                # Check if the character's memory contains this fact
                fact_in_memory = self._is_fact_in_memory(fact, character_memory)

                if fact_in_memory:
                    issues.append({
                        "title": "Unexplained Knowledge",
                        "description": f"Character '{character_id}' knows fact '{fact.get('name', fact_id)}' but shouldn't have learned it",
                        "severity": self._get_severity("unexplained_knowledge"),
                        "entities": [character_id],
                        "fact": fact_id
                    })

        return issues

    def _validate_quest_progression(self) -> List[Dict[str, Any]]:
        """
        Validate quest progression consistency for all quests.

        Returns:
            List of issues found during validation
        """
        issues = []

        # Check each quest's progression
        if hasattr(self.game_manager, "quests"):
            for quest_id in self.game_manager.quests:
                quest_issues = self._validate_single_quest_progression(quest_id)
                issues.extend(quest_issues)

        return issues

    def _validate_single_quest_progression(self, quest_id: str) -> List[Dict[str, Any]]:
        """
        Validate progression consistency for a specific quest.

        Args:
            quest_id: The ID of the quest to validate

        Returns:
            List of issues found
        """
        issues = []

        quest = self._get_quest(quest_id)
        if not quest:
            return []

        # Check quest status against prerequisites
        if "status" in quest and "prerequisites" in quest:
            quest_status = quest["status"]
            prerequisites = quest["prerequisites"]

            # If quest is active or completed, check that prerequisites are met
            if quest_status in ["active", "completed"]:
                for prereq_id in prerequisites:
                    prereq_quest = self._get_quest(prereq_id)

                    if not prereq_quest:
                        issues.append({
                            "title": "Missing Prerequisite Quest",
                            "description": f"Quest '{quest_id}' requires non-existent quest '{prereq_id}'",
                            "severity": "error",
                            "entities": [quest_id],
                            "prerequisite": prereq_id
                        })
                    elif "status" not in prereq_quest or prereq_quest["status"] != "completed":
                        issues.append({
                            "title": "Unsatisfied Prerequisite",
                            "description": f"Quest '{quest_id}' is {quest_status} but prerequisite quest '{prereq_id}' is not completed",
                            "severity": "error",
                            "entities": [quest_id, prereq_id]
                        })

        # Check quest stages progression logic
        if "stages" in quest and "current_stage" in quest:
            stages = quest["stages"]
            current_stage = quest["current_stage"]

            # Check that current stage exists
            if current_stage not in stages:
                issues.append({
                    "title": "Invalid Quest Stage",
                    "description": f"Quest '{quest_id}' references non-existent stage '{current_stage}'",
                    "severity": "error",
                    "entities": [quest_id],
                    "stage": current_stage
                })

            # Check that stage requirements are met
            if "completed_stages" in quest:
                completed_stages = quest["completed_stages"]

                # Get dependencies for current stage
                if current_stage in stages and "dependencies" in stages[current_stage]:
                    dependencies = stages[current_stage]["dependencies"]

                    for dependency in dependencies:
                        if dependency not in completed_stages:
                            issues.append({
                                "title": "Unsatisfied Stage Dependency",
                                "description": f"Quest '{quest_id}' is at stage '{current_stage}' but dependency stage '{dependency}' is not completed",
                                "severity": "warning",
                                "entities": [quest_id],
                                "stage": current_stage,
                                "dependency": dependency
                            })

        return issues

    def _validate_narrative_continuity(self) -> List[Dict[str, Any]]:
        """
        Validate narrative continuity by comparing current state with previous states.

        Returns:
            List of issues found during validation
        """
        issues = []

        # Skip if no previous states
        if not self.previous_states:
            return issues

        # Get most recent state
        previous_state = self.previous_states[-1]

        # Check for abrupt or unexplained changes in character relationships
        relationship_issues = self._check_relationship_continuity(previous_state)
        issues.extend(relationship_issues)

        # Check for logical inconsistencies in quest progression
        quest_issues = self._check_quest_continuity(previous_state)
        issues.extend(quest_issues)

        # Check for inconsistent character movements
        movement_issues = self._check_character_movement_continuity(previous_state)
        issues.extend(movement_issues)

        return issues

    def _check_relationship_continuity(self, previous_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for abrupt or unexplained changes in character relationships.

        Args:
            previous_state: The previous game state

        Returns:
            List of relationship continuity issues
        """
        issues = []

        # This implementation depends on how relationships are stored
        # For example, if using an entity relationship manager:
        if hasattr(self.game_manager, "entity_relationship_manager") and "relationships" in previous_state:
            prev_relationships = previous_state["relationships"]
            current_relationships = self._extract_current_relationships()

            # Check for significant relationship strength changes
            for rel_key, prev_rel in prev_relationships.items():
                if rel_key in current_relationships:
                    current_rel = current_relationships[rel_key]

                    # Check if relationship type or strength changed significantly
                    if "type" in prev_rel and "type" in current_rel and prev_rel["type"] != current_rel["type"]:
                        parts = rel_key.split(":")
                        if len(parts) >= 2:
                            entity1, entity2 = parts[0], parts[1]
                            issues.append({
                                "title": "Abrupt Relationship Change",
                                "description": f"Relationship between '{entity1}' and '{entity2}' changed from '{prev_rel['type']}' to '{current_rel['type']}' without explanation",
                                "severity": self._get_severity("abrupt_relationship_change"),
                                "entities": [entity1, entity2]
                            })

                    if "strength" in prev_rel and "strength" in current_rel:
                        strength_diff = abs(prev_rel["strength"] - current_rel["strength"])
                        if strength_diff > self._get_significant_relationship_change_threshold():
                            parts = rel_key.split(":")
                            if len(parts) >= 2:
                                entity1, entity2 = parts[0], parts[1]
                                issues.append({
                                    "title": "Significant Relationship Shift",
                                    "description": f"Relationship strength between '{entity1}' and '{entity2}' changed by {strength_diff} without explanation",
                                    "severity": self._get_severity("significant_relationship_shift"),
                                    "entities": [entity1, entity2]
                                })

        return issues

    def _check_quest_continuity(self, previous_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for logical inconsistencies in quest progression.

        Args:
            previous_state: The previous game state

        Returns:
            List of quest continuity issues
        """
        issues = []

        if "quests" in previous_state and hasattr(self.game_manager, "quests"):
            prev_quests = previous_state["quests"]

            for quest_id, prev_quest in prev_quests.items():
                if quest_id in self.game_manager.quests:
                    current_quest = self.game_manager.quests[quest_id]

                    # Check for quest status changes
                    if "status" in prev_quest and "status" in current_quest:
                        prev_status = prev_quest["status"]
                        current_status = current_quest["status"]

                        # Check for invalid status transitions
                        if prev_status == "completed" and current_status != "completed":
                            issues.append({
                                "title": "Invalid Quest Status Regression",
                                "description": f"Quest '{quest_id}' regressed from 'completed' to '{current_status}'",
                                "severity": "error",
                                "entities": [quest_id]
                            })

                        if prev_status == "failed" and current_status == "active":
                            issues.append({
                                "title": "Invalid Quest Status Transition",
                                "description": f"Quest '{quest_id}' transitioned from 'failed' to 'active' without reset",
                                "severity": "error",
                                "entities": [quest_id]
                            })

                    # Check for stage regressions
                    if "current_stage" in prev_quest and "current_stage" in current_quest and "stages" in current_quest:
                        if prev_quest["current_stage"] != current_quest["current_stage"]:
                            prev_stage = prev_quest["current_stage"]
                            current_stage = current_quest["current_stage"]

                            # Check if the stage change skipped dependencies
                            if "stages" in current_quest and current_stage in current_quest["stages"]:
                                stage_info = current_quest["stages"][current_stage]
                                if "dependencies" in stage_info:
                                    dependencies = stage_info["dependencies"]
                                    if prev_stage not in dependencies and prev_stage != current_stage:
                                        issues.append({
                                            "title": "Illogical Quest Stage Jump",
                                            "description": f"Quest '{quest_id}' jumped from stage '{prev_stage}' to '{current_stage}' without satisfying dependencies",
                                            "severity": "warning",
                                            "entities": [quest_id]
                                        })

        return issues

    def _check_character_movement_continuity(self, previous_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for inconsistent character movements.

        Args:
            previous_state: The previous game state

        Returns:
            List of character movement continuity issues
        """
        issues = []

        if "characters" in previous_state and hasattr(self.game_manager, "characters"):
            prev_characters = previous_state["characters"]

            for character_id, prev_character in prev_characters.items():
                if character_id in self.game_manager.characters:
                    current_character = self.game_manager.characters[character_id]

                    # Check for location changes
                    if "location" in prev_character and "location" in current_character:
                        prev_location = prev_character["location"]
                        current_location = current_character["location"]

                        if prev_location != current_location:
                            # Check if the locations are connected
                            if not self._are_locations_connected(prev_location, current_location):
                                issues.append({
                                    "title": "Impossible Character Movement",
                                    "description": f"Character '{character_id}' moved from '{prev_location}' to '{current_location}' but they are not connected",
                                    "severity": self._get_severity("impossible_movement"),
                                    "entities": [character_id, prev_location, current_location]
                                })

        return issues

    def _store_current_state_snapshot(self):
        """Store a snapshot of the current game state for continuity checks."""
        if not self.game_manager:
            return

        state = {
            "timestamp": self._get_current_timestamp()
        }

        # Store character data
        if hasattr(self.game_manager, "characters"):
            state["characters"] = self._snapshot_dict(self.game_manager.characters)

        # Store quest data
        if hasattr(self.game_manager, "quests"):
            state["quests"] = self._snapshot_dict(self.game_manager.quests)

        # Store relationship data
        if hasattr(self.game_manager, "entity_relationship_manager"):
            state["relationships"] = self._extract_current_relationships()

        # Store location data
        if hasattr(self.game_manager, "locations"):
            state["locations"] = self._snapshot_dict(self.game_manager.locations)

        # Add to previous states
        self.previous_states.append(state)

        # Limit the number of stored states to prevent memory issues
        max_states = 10
        if len(self.previous_states) > max_states:
            self.previous_states = self.previous_states[-max_states:]

    # Helper methods

    def _snapshot_dict(self, source_dict: Dict) -> Dict:
        """Create a deep copy snapshot of a dictionary."""
        import copy
        return copy.deepcopy(source_dict)

    def _extract_current_relationships(self) -> Dict[str, Any]:
        """Extract current relationships from the entity relationship manager."""
        relationships = {}

        if hasattr(self.game_manager, "entity_relationship_manager"):
            try:
                # This implementation depends on how the relationship manager is structured
                # Example implementation:
                if hasattr(self.game_manager.entity_relationship_manager, "get_all_relationships"):
                    all_relationships = self.game_manager.entity_relationship_manager.get_all_relationships()
                    for rel in all_relationships:
                        # Create a key combining both entities and relationship type
                        key = f"{rel['source']}:{rel['target']}:{rel['type']}"
                        relationships[key] = rel
            except Exception as e:
                logger.error(f"Error extracting relationships: {e}")

        return relationships

    def _get_current_timestamp(self) -> str:
        """Get the current timestamp as a string."""
        from datetime import datetime
        return datetime.now().isoformat()

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

    def _get_quest(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get quest data by ID."""
        if not self.game_manager or not hasattr(self.game_manager, "quests"):
            return None

        try:
            return self.game_manager.quests.get(quest_id)
        except Exception as e:
            logger.error(f"Error getting quest {quest_id}: {e}")

        return None

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

    def _get_facts_character_should_know(self, character_id: str) -> List[str]:
        """
        Determine which facts a character should know based on their experience.

        Args:
            character_id: The ID of the character

        Returns:
            List of fact IDs the character should know
        """
        # This implementation depends on how facts and character knowledge are tracked
        # Example implementation:
        facts_should_know = []

        character = self._get_character(character_id)
        if not character:
            return []

        if hasattr(self.game_manager, "facts"):
            for fact_id, fact in self.game_manager.facts.items():
                # Check if character was at the location where the fact is revealed
                if "location" in fact and "visited_locations" in character and fact["location"] in character["visited_locations"]:
                    facts_should_know.append(fact_id)

                # Check if character has completed a quest that reveals the fact
                if "revealed_by_quest" in fact and "completed_quests" in character and fact["revealed_by_quest"] in character["completed_quests"]:
                    facts_should_know.append(fact_id)

                # Check if character has talked to an NPC who knows this fact
                if "known_by_npc" in fact and "interacted_with" in character:
                    for npc_id in fact["known_by_npc"]:
                        if npc_id in character["interacted_with"]:
                            facts_should_know.append(fact_id)
                            break

        return facts_should_know

    def _get_facts_character_should_not_know(self, character_id: str) -> List[str]:
        """
        Determine which facts a character should NOT know.

        Args:
            character_id: The ID of the character

        Returns:
            List of fact IDs the character should not know
        """
        # This implementation depends on how facts and character knowledge are tracked
        # Example implementation:
        facts_should_not_know = []

        character = self._get_character(character_id)
        if not character:
            return []

        if hasattr(self.game_manager, "facts"):
            for fact_id, fact in self.game_manager.facts.items():
                # If the fact is hidden and character hasn't done anything to learn it
                if "hidden" in fact and fact["hidden"]:
                    should_know = False

                    # Check if character was at the location where the fact is revealed
                    if "location" in fact and "visited_locations" in character and fact["location"] in character["visited_locations"]:
                        should_know = True

                    # Check if character has completed a quest that reveals the fact
                    if "revealed_by_quest" in fact and "completed_quests" in character and fact["revealed_by_quest"] in character["completed_quests"]:
                        should_know = True

                    # Check if character has talked to an NPC who knows this fact
                    if "known_by_npc" in fact and "interacted_with" in character:
                        for npc_id in fact["known_by_npc"]:
                            if npc_id in character["interacted_with"]:
                                should_know = True
                                break

                    if not should_know:
                        facts_should_not_know.append(fact_id)

        return facts_should_not_know

    def _is_fact_in_memory(self, fact: Dict[str, Any], memory: List[Dict[str, Any]]) -> bool:
        """
        Check if a fact is present in a character's memory.

        Args:
            fact: The fact to check for
            memory: The character's memory

        Returns:
            True if the fact is in memory, False otherwise
        """
        # This implementation depends on how memory is structured
        # Example implementation:
        if "keywords" in fact:
            keywords = fact["keywords"]

            for memory_item in memory:
                if "content" in memory_item:
                    content = memory_item["content"].lower()

                    # Check if all keywords are in the memory item
                    all_keywords_present = all(keyword.lower() in content for keyword in keywords)

                    if all_keywords_present:
                        return True

        return False

    def _are_locations_connected(self, location1_id: str, location2_id: str) -> bool:
        """
        Check if two locations are directly connected.

        Args:
            location1_id: The ID of the first location
            location2_id: The ID of the second location

        Returns:
            True if the locations are connected, False otherwise
        """
        if not self.game_manager or not hasattr(self.game_manager, "locations"):
            return False

        try:
            location1 = self.game_manager.locations.get(location1_id)

            if not location1:
                return False

            # Check if location2 is in location1's connections
            if "connections" in location1 and location2_id in location1["connections"]:
                return True

            # If using a different structure for connections:
            if hasattr(self.game_manager, "location_graph"):
                return location2_id in self.game_manager.location_graph.get(location1_id, [])
        except Exception as e:
            logger.error(f"Error checking location connection: {e}")

        return False

    def _get_significant_relationship_change_threshold(self) -> float:
        """Get the threshold for significant relationship strength changes."""
        if self.config and hasattr(self.config, "narrative_rules"):
            return self.config.narrative_rules.get("significant_relationship_change_threshold", 0.3)
        return 0.3

    def _should_check_character_knowledge(self) -> bool:
        """Check if character knowledge should be validated."""
        if self.config and hasattr(self.config, "narrative_rules"):
            return self.config.narrative_rules.get("check_character_knowledge", True)
        return True

    def _should_check_quest_progression(self) -> bool:
        """Check if quest progression should be validated."""
        if self.config and hasattr(self.config, "narrative_rules"):
            return self.config.narrative_rules.get("check_quest_progression", True)
        return True

    def _should_check_narrative_continuity(self) -> bool:
        """Check if narrative continuity should be validated."""
        if self.config and hasattr(self.config, "narrative_rules"):
            return self.config.narrative_rules.get("check_narrative_continuity", True)
        return True

    def _get_severity(self, issue_type: str) -> str:
        """Get severity level for a given issue type."""
        if self.config and hasattr(self.config, "severity_thresholds"):
            return self.config.severity_thresholds.get(issue_type, "warning")

        # Default severity mappings if config not available
        severity_map = {
            "missing_knowledge": "warning",
            "unexplained_knowledge": "warning",
            "abrupt_relationship_change": "warning",
            "significant_relationship_shift": "info",
            "impossible_movement": "error"
        }

        return severity_map.get(issue_type, "warning")
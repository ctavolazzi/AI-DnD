#!/usr/bin/env python3
"""
Sentinel Core Module

This module defines the Sentinel class, which serves as the central coordinator
for all game monitoring and validation activities. The Sentinel observes the game
state without making changes, identifying inconsistencies and logging them for
later review.
"""

import os
import logging
import datetime
import time
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable

from sentinel.config import SentinelConfig
from sentinel.validators import (
    EntityValidator,
    RelationshipValidator,
    WorldStateValidator,
    NarrativeConsistencyValidator
)

# Setup module-level logger
logger = logging.getLogger("sentinel")


class Sentinel:
    """
    The Sentinel is responsible for monitoring and validating the game state
    to ensure logical consistency throughout the world.

    The Sentinel performs periodic validations, cross-references entities, checks
    relationships, and ensures narrative consistency without modifying any state.

    Any inconsistencies found are logged through a dedicated logging channel.
    """

    def __init__(self,
                 game_manager=None,
                 dungeon_master=None,
                 config: Optional[SentinelConfig] = None,
                 log_level: int = logging.INFO):
        """
        Initialize the Sentinel with references to key game components.

        Args:
            game_manager: Reference to the GameManager instance
            dungeon_master: Reference to the DungeonMaster instance
            config: Configuration for Sentinel behavior and validation rules
            log_level: Logging level for Sentinel messages
        """
        self.game_manager = game_manager
        self.dungeon_master = dungeon_master
        self.config = config or SentinelConfig()

        # Setup logging
        self._setup_logging(log_level)

        # Initialize validators
        self.validators = self._initialize_validators()

        # Track the last validation times
        self.last_validation_times = {}

        # Performance metrics
        self.performance_stats = {
            "validation_runs": 0,
            "issues_found": 0,
            "total_validation_time": 0,
            "validation_times_by_type": {}
        }

        logger.info("Sentinel initialized and standing watch")

    def _setup_logging(self, log_level: int):
        """Set up dedicated logging for the Sentinel."""
        logger.setLevel(log_level)

        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Create a file handler for sentinel logs
        log_file = f"logs/sentinel_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)

        # Create a formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

    def _initialize_validators(self) -> Dict[str, Any]:
        """Initialize all validator components."""
        return {
            "entity": EntityValidator(self.game_manager, self.config),
            "relationship": RelationshipValidator(self.game_manager, self.config),
            "world_state": WorldStateValidator(self.game_manager, self.dungeon_master, self.config),
            "narrative": NarrativeConsistencyValidator(self.game_manager, self.dungeon_master, self.config)
        }

    def validate_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run all validators and return aggregated results.

        Returns:
            Dict mapping validation types to lists of issues found
        """
        start_time = time.time()

        logger.info("Starting full validation of game state")
        self.performance_stats["validation_runs"] += 1

        results = {}

        # Run all validators and collect results
        for name, validator in self.validators.items():
            validator_start = time.time()
            issues = validator.validate()
            validator_time = time.time() - validator_start

            # Store timing information
            if name not in self.performance_stats["validation_times_by_type"]:
                self.performance_stats["validation_times_by_type"][name] = []
            self.performance_stats["validation_times_by_type"][name].append(validator_time)

            # Store results
            results[name] = issues

            # Log any issues found
            if issues:
                for issue in issues:
                    self._log_issue(name, issue)

                logger.warning(f"Found {len(issues)} issues during {name} validation")
                self.performance_stats["issues_found"] += len(issues)
            else:
                logger.info(f"No issues found during {name} validation")

        # Update performance metrics
        total_time = time.time() - start_time
        self.performance_stats["total_validation_time"] += total_time

        logger.info(f"Full validation completed in {total_time:.2f} seconds")

        return results

    def _log_issue(self, validator_type: str, issue: Dict[str, Any]):
        """Log a single issue with appropriate level and formatting."""
        severity = issue.get("severity", "warning").lower()

        if severity == "critical":
            log_method = logger.critical
        elif severity == "error":
            log_method = logger.error
        elif severity == "warning":
            log_method = logger.warning
        else:
            log_method = logger.info

        message = (
            f"[{validator_type.upper()}] {issue.get('title', 'Unnamed Issue')}: "
            f"{issue.get('description', 'No description provided')}"
        )

        # Include entity details if available
        entities = issue.get("entities", [])
        if entities:
            entity_str = ", ".join(str(e) for e in entities)
            message += f" | Entities: {entity_str}"

        log_method(message)

    def validate_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Validate a specific entity for consistency.

        Args:
            entity_id: The ID of the entity to validate

        Returns:
            List of issues found with the entity
        """
        logger.info(f"Validating entity: {entity_id}")
        issues = self.validators["entity"].validate_single_entity(entity_id)

        for issue in issues:
            self._log_issue("entity", issue)

        return issues

    def validate_relationship(self, entity1_id: str, entity2_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Validate the relationship between two entities.

        Args:
            entity1_id: The ID of the first entity
            entity2_id: The ID of the second entity
            relation_type: Optional specific relation type to check

        Returns:
            List of issues found with the relationship
        """
        logger.info(f"Validating relationship between {entity1_id} and {entity2_id}")
        issues = self.validators["relationship"].validate_relationship(entity1_id, entity2_id, relation_type)

        for issue in issues:
            self._log_issue("relationship", issue)

        return issues

    def validate_location_consistency(self, location_id: str) -> List[Dict[str, Any]]:
        """
        Validate that a location's state is consistent with all entities that reference it.

        Args:
            location_id: The ID of the location to validate

        Returns:
            List of issues found with the location
        """
        logger.info(f"Validating location consistency: {location_id}")
        issues = self.validators["world_state"].validate_location(location_id)

        for issue in issues:
            self._log_issue("world_state", issue)

        return issues

    def validate_character_consistency(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Validate that a character's state is consistent across all game systems.

        Args:
            character_id: The ID of the character to validate

        Returns:
            List of issues found with the character
        """
        logger.info(f"Validating character consistency: {character_id}")
        issues = self.validators["entity"].validate_character(character_id)

        for issue in issues:
            self._log_issue("entity", issue)

        return issues

    def register_with_game(self, game_manager, dungeon_master):
        """
        Register the Sentinel with the game manager and dungeon master.

        This should be called after game initialization is complete to link
        the Sentinel with the necessary game components.

        Args:
            game_manager: The GameManager instance
            dungeon_master: The DungeonMaster instance
        """
        self.game_manager = game_manager
        self.dungeon_master = dungeon_master

        # Reinitialize validators with new references
        self.validators = self._initialize_validators()

        logger.info("Sentinel registered with game components")

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the Sentinel.

        Returns:
            Dict containing performance metrics
        """
        stats = self.performance_stats.copy()

        # Calculate averages
        if stats["validation_runs"] > 0:
            stats["avg_validation_time"] = stats["total_validation_time"] / stats["validation_runs"]
            stats["avg_issues_per_run"] = stats["issues_found"] / stats["validation_runs"]

        # Calculate average time per validator
        avg_times_by_type = {}
        for validator_type, times in stats["validation_times_by_type"].items():
            if times:
                avg_times_by_type[validator_type] = sum(times) / len(times)
            else:
                avg_times_by_type[validator_type] = 0

        stats["avg_times_by_validator"] = avg_times_by_type

        return stats

    def schedule_validation(self, interval_seconds: int = 300):
        """
        Schedule regular validation runs.
        This is meant to be called in a separate thread to periodically validate the game state.

        Args:
            interval_seconds: Time between validation runs in seconds
        """
        logger.info(f"Scheduling validation every {interval_seconds} seconds")

        while True:
            time.sleep(interval_seconds)
            self.validate_all()
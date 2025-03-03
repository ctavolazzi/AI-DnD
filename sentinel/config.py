"""
Sentinel Configuration Module

This module defines the configuration settings for the Sentinel monitoring system,
including validation rules, thresholds, and operational parameters.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field


@dataclass
class SentinelConfig:
    """Configuration settings for the Sentinel monitoring system."""

    # General settings
    enabled: bool = True
    log_level: str = "INFO"

    # Validation frequencies (in seconds)
    validation_intervals: Dict[str, int] = field(default_factory=lambda: {
        "entity": 300,          # Check entities every 5 minutes
        "relationship": 300,    # Check relationships every 5 minutes
        "world_state": 600,     # Check world state every 10 minutes
        "narrative": 1800       # Check narrative consistency every 30 minutes
    })

    # Entity validation settings
    entity_rules: Dict[str, Any] = field(default_factory=lambda: {
        "required_character_fields": [
            "name", "char_class", "hp", "max_hp", "attack", "defense",
            "alive", "status", "bio", "abilities", "team", "location"
        ],
        "required_location_fields": [
            "name", "description", "type"
        ],
        "required_item_fields": [
            "name", "description", "type"
        ],
        "required_quest_fields": [
            "name", "description", "status"
        ],
        "valid_character_statuses": [
            "Active", "Injured", "Unconscious", "Dead", "Missing"
        ],
        "valid_quest_statuses": [
            "Active", "Completed", "Failed", "On Hold"
        ]
    })

    # Relationship validation settings
    relationship_rules: Dict[str, Any] = field(default_factory=lambda: {
        "valid_relationship_types": [
            "present_at", "knows", "has_item", "on_quest", "allied_with",
            "hostile_to", "neutral_to", "leads", "follows"
        ],
        "check_bidirectional": True,
        "relationships_requiring_bidirectional": [
            "allied_with", "hostile_to", "neutral_to"
        ],
        "verify_character_location_relationships": True
    })

    # World state validation settings
    world_state_rules: Dict[str, Any] = field(default_factory=lambda: {
        "verify_location_connections": True,
        "verify_character_locations": True,
        "verify_item_locations": True,
        "verify_location_character_lists": True,
        "check_isolated_locations": True,
        "check_orphaned_entities": True
    })

    # Narrative consistency validation settings
    narrative_rules: Dict[str, Any] = field(default_factory=lambda: {
        "check_event_continuity": True,
        "check_character_knowledge_consistency": True,
        "check_quest_progression_logic": True,
        "check_character_motivation_consistency": True,
        "max_days_between_quest_updates": 5
    })

    # Issue severity thresholds
    severity_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "missing_required_field": "error",
        "invalid_field_value": "warning",
        "inconsistent_relationship": "warning",
        "orphaned_entity": "warning",
        "isolated_location": "info",
        "narrative_discontinuity": "warning",
        "knowledge_inconsistency": "warning",
        "quest_progression_issue": "warning",
        "character_location_mismatch": "error"
    })

    # Operational settings
    max_validation_time: int = 30  # Maximum time (seconds) for a full validation
    max_issues_to_log: int = 100   # Maximum number of issues to log per validation
    throttle_validations: bool = True  # Throttle validations when busy


class ValidationRule:
    """Base class for validation rules."""

    def __init__(self, name: str, severity: str = "warning", entities: Optional[List[str]] = None):
        self.name = name
        self.severity = severity
        self.entities = entities or []

    def validate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate the rule against the given context.

        Args:
            context: The context to validate

        Returns:
            An issue dict if validation fails, None if successful
        """
        raise NotImplementedError("Subclasses must implement validate method")


class FieldPresenceRule(ValidationRule):
    """Rule that checks for the presence of required fields."""

    def __init__(self, name: str, required_fields: List[str], severity: str = "error"):
        super().__init__(name, severity)
        self.required_fields = required_fields

    def validate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        missing_fields = []
        entity = context.get("entity", {})

        for field in self.required_fields:
            if field not in entity or entity[field] is None:
                missing_fields.append(field)

        if missing_fields:
            return {
                "title": f"Missing Required Fields: {self.name}",
                "description": f"Entity is missing required fields: {', '.join(missing_fields)}",
                "severity": self.severity,
                "entities": [entity.get("name", "Unknown")],
                "missing_fields": missing_fields
            }

        return None


class RelationshipConsistencyRule(ValidationRule):
    """Rule that checks for consistency in relationships between entities."""

    def __init__(self, name: str, entity_type: str, relation_type: str, severity: str = "warning"):
        super().__init__(name, severity)
        self.entity_type = entity_type
        self.relation_type = relation_type

    def validate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        entity = context.get("entity", {})
        relationships = context.get("relationships", {})

        if not relationships:
            return None

        # Check specific logic based on relation_type
        # Implementation will depend on the specific rule

        return None


# Registry of built-in validation rules
DEFAULT_RULES = {
    "character_fields": FieldPresenceRule(
        "Character Required Fields",
        ["name", "char_class", "hp", "max_hp", "attack", "defense", "alive", "status"],
        "error"
    ),
    "location_fields": FieldPresenceRule(
        "Location Required Fields",
        ["name", "description", "type"],
        "error"
    ),
    "character_location": RelationshipConsistencyRule(
        "Character Location Consistency",
        "character",
        "present_at",
        "error"
    )
}
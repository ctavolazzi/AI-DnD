"""
Sentinel: Game State Monitoring System for AI-DnD

This package provides a comprehensive monitoring system designed to ensure
logical consistency within the AI-DnD game. It validates game state, identifies
inconsistencies, and logs issues for review without making changes to the game
state itself.

Components:
- Sentinel: Main coordinator class that manages validation activities
- SentinelConfig: Configuration settings for validation rules
- Validators: Classes that perform specific validation checks
"""

from sentinel.sentinel import Sentinel
from sentinel.config import SentinelConfig
from sentinel.validators import (
    EntityValidator,
    RelationshipValidator,
    WorldStateValidator,
    NarrativeConsistencyValidator
)

__all__ = [
    'Sentinel',
    'SentinelConfig',
    'EntityValidator',
    'RelationshipValidator',
    'WorldStateValidator',
    'NarrativeConsistencyValidator'
]
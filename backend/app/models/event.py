"""Event model for narrative history tracking"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Event(Base):
    """
    Represents a narrative event in the game.

    Events form the complete narrative history and provide:
    - Event sourcing for game state reconstruction
    - Audit trail for data integrity
    - Narrative timeline for storytelling
    """
    __tablename__ = "events"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Foreign Key
    session_id = Column(String, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Event Identity
    event_type = Column(String, nullable=False, index=True)  # combat, dialogue, skill_check, etc.
    turn_number = Column(Integer, nullable=False, index=True)

    # Event Data
    summary = Column(String, nullable=False)  # Short description
    description = Column(Text, nullable=True)  # Full narrative

    # Event Context
    location_id = Column(String, nullable=True, index=True)
    character_ids = Column(JSON, default=[], nullable=False)  # Characters involved

    # Event Results (JSON for flexibility)
    data = Column(JSON, default={}, nullable=False)  # Specific event data
    # Examples:
    # - combat: {"attacker": "Hero 1", "target": "Goblin 1", "damage": 15, "killed": false}
    # - skill_check: {"character": "Hero 1", "skill": "Stealth", "roll": 18, "dc": 15, "success": true}
    # - dialogue: {"speaker": "NPC", "dialogue": "Welcome traveler", "choice_made": "ask_about_quest"}

    # State Changes (for reconstruction)
    state_before = Column(JSON, nullable=True)  # Relevant state before event
    state_after = Column(JSON, nullable=True)   # Relevant state after event

    # Integrity
    checksum = Column(String, nullable=True)  # Hash of event data for integrity verification

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    # session = relationship("GameSession", back_populates="events")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "turn_number": self.turn_number,
            "summary": self.summary,
            "description": self.description,
            "location_id": self.location_id,
            "character_ids": self.character_ids,
            "data": self.data,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

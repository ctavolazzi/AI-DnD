"""Game session model for persistent game state"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class GameSession(Base):
    """
    Represents a single game session/campaign.

    This is the top-level container for all game state. Each session has:
    - A unique ID for saving/loading
    - Metadata (name, created date, last played)
    - Current state (turn number, status)
    - Relationships to characters, locations, events
    """
    __tablename__ = "game_sessions"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Metadata
    name = Column(String, nullable=False, default="New Adventure")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_played_at = Column(DateTime(timezone=True))

    # Game State
    turn_count = Column(Integer, default=0, nullable=False)
    status = Column(String, default="active", nullable=False)  # active, paused, completed, failed
    current_location_id = Column(String, nullable=True)

    # JSON snapshot of complete game state (for easy save/load)
    state_snapshot = Column(JSON, nullable=True)

    # Quest info
    current_quest = Column(Text, nullable=True)
    quest_progress = Column(JSON, default={}, nullable=False)

    # Settings
    difficulty = Column(String, default="medium", nullable=False)
    ai_model = Column(String, default="mistral", nullable=False)

    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships (will be defined after other models are created)
    # characters = relationship("Character", back_populates="session", cascade="all, delete-orphan")
    # locations = relationship("Location", back_populates="session", cascade="all, delete-orphan")
    # events = relationship("Event", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_played_at": self.last_played_at.isoformat() if self.last_played_at else None,
            "turn_count": self.turn_count,
            "status": self.status,
            "current_location_id": self.current_location_id,
            "current_quest": self.current_quest,
            "quest_progress": self.quest_progress,
            "difficulty": self.difficulty,
            "ai_model": self.ai_model,
        }

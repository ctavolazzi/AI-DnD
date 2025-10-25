"""Location model for world locations"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Location(Base):
    """
    Represents a location in the game world.

    Stores:
    - Location details (name, description, type)
    - Connections to other locations
    - NPCs and services available
    - Visit history
    """
    __tablename__ = "locations"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Key
    session_id = Column(String, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Location Info
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    location_type = Column(String, nullable=False, default="wilderness")  # town, dungeon, cave, etc.

    # Connections (JSON mapping to other location IDs)
    connections = Column(JSON, default={}, nullable=False)  # {"north": "loc_123", "east": "loc_456"}

    # NPCs and Services
    npcs = Column(JSON, default=[], nullable=False)  # ["Shopkeeper", "Guard", ...]
    services = Column(JSON, default=[], nullable=False)  # ["shop", "inn", "temple"]

    # Encounters
    encounter_chance = Column(Integer, default=30, nullable=False)  # Percentage
    encounter_types = Column(JSON, default=[], nullable=False)  # ["Goblin", "Bandit", ...]

    # State
    visited = Column(Integer, default=0, nullable=False)  # Visit count
    cleared = Column(Integer, default=False, nullable=False)  # Has been cleared of enemies

    # Characters present (updated dynamically)
    character_ids = Column(JSON, default=[], nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # session = relationship("GameSession", back_populates="locations")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "location_type": self.location_type,
            "connections": self.connections,
            "npcs": self.npcs,
            "services": self.services,
            "encounter_chance": self.encounter_chance,
            "encounter_types": self.encounter_types,
            "visited": self.visited,
            "cleared": self.cleared,
            "character_ids": self.character_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

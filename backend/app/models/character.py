"""Character model for persistent character data"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Character(Base):
    """
    Represents a character (player or NPC) in the game.

    Stores all character state including:
    - Stats (HP, mana, abilities)
    - Inventory (JSON)
    - Status effects
    - Location
    """
    __tablename__ = "characters"

    # Primary Key
    id = Column(String, primary_key=True, index=True)

    # Foreign Key
    session_id = Column(String, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Character Identity
    name = Column(String, nullable=False, index=True)
    char_class = Column(String, nullable=False)  # Fighter, Wizard, etc.
    team = Column(String, nullable=False, default="players")  # players, enemies, npcs

    # Core Stats
    hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    mana = Column(Integer, default=0, nullable=False)
    max_mana = Column(Integer, default=0, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)

    # D&D Ability Scores
    ability_scores = Column(JSON, nullable=False, default={})  # {"STR": 16, "DEX": 12, ...}

    # State
    alive = Column(Boolean, default=True, nullable=False)
    current_location_id = Column(String, nullable=True)
    status_effects = Column(JSON, default=[], nullable=False)  # ["stunned", "blessed", ...]

    # Inventory (JSON for flexibility)
    inventory = Column(JSON, default={"items": {}, "equipped": {}, "capacity": 20}, nullable=False)

    # Spellbook
    spells = Column(JSON, default=[], nullable=False)  # ["fireball", "heal", ...]

    # Skills
    proficiency_bonus = Column(Integer, default=2, nullable=False)
    skill_proficiencies = Column(JSON, default=[], nullable=False)  # ["Stealth", "Perception", ...]

    # Biography
    bio = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # session = relationship("GameSession", back_populates="characters")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "name": self.name,
            "char_class": self.char_class,
            "team": self.team,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "attack": self.attack,
            "defense": self.defense,
            "ability_scores": self.ability_scores,
            "alive": self.alive,
            "current_location_id": self.current_location_id,
            "status_effects": self.status_effects,
            "inventory": self.inventory,
            "spells": self.spells,
            "proficiency_bonus": self.proficiency_bonus,
            "skill_proficiencies": self.skill_proficiencies,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

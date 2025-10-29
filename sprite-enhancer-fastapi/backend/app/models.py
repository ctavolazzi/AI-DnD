"""Database models for Sprite Enhancer."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    """User model for authentication and ownership."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sprites = relationship("Sprite", back_populates="user", cascade="all, delete-orphan")


class Sprite(Base):
    """Sprite model for pixel art generations."""
    __tablename__ = "sprites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    image_url = Column(String, nullable=False)  # S3 URL or base64
    size = Column(Integer, default=64)
    style = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sprites")
    enhanced = relationship("Enhanced", back_populates="sprite", uselist=False, cascade="all, delete-orphan")


class Enhanced(Base):
    """Enhanced image model for AI-enhanced versions."""
    __tablename__ = "enhanced"

    id = Column(Integer, primary_key=True, index=True)
    sprite_id = Column(Integer, ForeignKey("sprites.id"), unique=True, nullable=False)
    image_url = Column(String, nullable=False)  # S3 URL or base64
    enhancement_prompt = Column(Text, nullable=False)
    style = Column(String, nullable=True)
    generation_time = Column(Integer)  # Time in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sprite = relationship("Sprite", back_populates="enhanced")


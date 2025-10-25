"""Image Asset model for storing generated images"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.sql import func
from ..database import Base


class ImageAsset(Base):
    """Image asset with filesystem storage and comprehensive metadata"""
    __tablename__ = "image_assets"

    # Use INTEGER PRIMARY KEY (SQLite optimized)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core metadata
    component = Column(String(50), nullable=False)  # scene-viewer, item-modal
    subject_type = Column(String(50), nullable=False)  # scene, item, character
    subject_name = Column(String(200), nullable=False, index=True)

    # Prompts
    prompt_used = Column(Text, nullable=False)
    custom_prompt = Column(Text, nullable=True)

    # Storage (filesystem only)
    storage_path_full = Column(String(500), nullable=False, unique=True)
    storage_path_thumbnail = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)

    # Generation metadata
    model_used = Column(String(100), default="gemini-2.5-flash-image")
    aspect_ratio = Column(String(10), nullable=False)
    generation_time_ms = Column(Integer, nullable=False)

    # Usage tracking
    use_count = Column(Integer, default=1)
    last_used = Column(DateTime, default=func.now(), onupdate=func.now())
    is_featured = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # EXPLICIT INDEXES (not just "indexed" comments)
    __table_args__ = (
        Index('idx_subject_lookup', 'subject_type', 'subject_name'),
        Index('idx_component_lookup', 'component', 'subject_name'),
        Index('idx_featured', 'subject_name', 'is_featured'),
        Index('idx_active', 'deleted_at'),  # For "not deleted" queries
    )

    def __repr__(self):
        return f"<ImageAsset(id={self.id}, subject_name='{self.subject_name}', type='{self.subject_type}')>"


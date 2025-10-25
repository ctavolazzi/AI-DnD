"""Scene Cache model for caching generated scenes"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class SceneCache(Base):
    """Scene cache with expiry management"""
    __tablename__ = "scene_cache"

    id = Column(Integer, primary_key=True)

    # Cache key components
    location = Column(String(200), nullable=False)
    time_of_day = Column(String(50), nullable=False)
    weather = Column(String(50), nullable=False)

    # Reference to image
    image_asset_id = Column(Integer, ForeignKey('image_assets.id'), nullable=False)
    image_asset = relationship("ImageAsset", backref="scene_cache")

    # Cache management
    use_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    last_used = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('idx_cache_key', 'location', 'time_of_day', 'weather'),
        Index('idx_expiry', 'expires_at'),
    )

    def __repr__(self):
        return f"<SceneCache(location='{self.location}', time='{self.time_of_day}', weather='{self.weather}')>"


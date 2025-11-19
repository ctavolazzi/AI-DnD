"""Database model for queued log events"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..database import Base


class LogEvent(Base):
    """Represents a persisted log entry that needs to be flushed to Obsidian."""

    __tablename__ = "log_events"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    level = Column(String, nullable=False, default="INFO", index=True)
    message = Column(Text, nullable=False)
    # Column named "metadata" in DB, but SQLAlchemy reserves attribute name, so expose as log_metadata
    log_metadata = Column("metadata", JSON, default=dict, nullable=False)
    exception = Column(Text, nullable=True)
    status = Column(String, default="pending", nullable=False, index=True)
    attempts = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self) -> dict:
        """Serialize the log event for debugging or API usage."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "level": self.level,
            "message": self.message,
            "metadata": self.log_metadata,
            "exception": self.exception,
            "status": self.status,
            "attempts": self.attempts,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }

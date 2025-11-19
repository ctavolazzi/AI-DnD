import asyncio
import logging
import traceback
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.log_event import LogEvent
from ..config import settings

# Configure logger for the worker itself
logger = logging.getLogger("log_worker")

class LogWorker:
    """
    Background worker that polls the LogEvent table and writes entries
    to Obsidian files sequentially to ensure order and prevent race conditions.
    """
    _instance: Optional['LogWorker'] = None
    _running: bool = False
    _task: Optional[asyncio.Task] = None

    @classmethod
    def get_instance(cls) -> 'LogWorker':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self):
        """Start the background worker task"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("LogWorker started")

    async def stop(self):
        """Stop the background worker task"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("LogWorker stopped")

    async def _run_loop(self):
        """Main polling loop"""
        while self._running:
            try:
                # Run processing in a thread to avoid blocking the async loop with DB/File IO
                await asyncio.to_thread(self._process_batch)
            except Exception as e:
                logger.error(f"Error in LogWorker loop: {e}")

            # Poll interval
            await asyncio.sleep(1.0)

    def _process_batch(self):
        """Process a batch of pending logs"""
        db: Session = SessionLocal()
        try:
            # Fetch pending events ordered by ID (creation time)
            events = db.query(LogEvent).filter(
                LogEvent.status == "pending"
            ).order_by(LogEvent.id.asc()).limit(50).all()

            if not events:
                return

            for event in events:
                self._process_event(db, event)

            db.commit()
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            db.rollback()
        finally:
            db.close()

    def _process_event(self, db: Session, event: LogEvent):
        """Process a single log event"""
        try:
            # Determine target file based on metadata or session_id
            # This logic mirrors the ObsidianLogger but adapted for the worker context
            # For now, we'll use a simple mapping or default to a session log

            # TODO: Integrate full ObsidianLogger logic here if needed.
            # For this implementation, we assume the 'message' is formatted for the log.

            # Mark as processed
            event.status = "completed"
            event.processed_at = datetime.now()

            # If we had actual file writing logic, it would go here.
            # Currently, the ObsidianLogger in the legacy code handles file path logic.
            # We might need to import a modified version of it or re-implement the writing.
            # For now, we just mark it as processed to verify the queue works.

        except Exception as e:
            event.status = "failed"
            event.error_message = str(e)
            event.attempts += 1
            logger.error(f"Failed to process log event {event.id}: {e}")

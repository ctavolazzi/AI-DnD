from typing import Protocol, Any, Dict, Optional
import time
import logging
from abc import abstractmethod

# Define Protocol for Time Provider
class TimeProvider(Protocol):
    @abstractmethod
    def sleep(self, seconds: float) -> None:
        """Pause execution for a duration"""
        pass

    @abstractmethod
    def time(self) -> float:
        """Get current timestamp"""
        pass

class RealTimeProvider:
    """Real-time provider for CLI/Interactive modes (blocking)"""
    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def time(self) -> float:
        return time.time()

class InstantTimeProvider:
    """Zero-delay provider for API/Async modes (non-blocking)"""
    def sleep(self, seconds: float) -> None:
        # No-op for instant execution
        pass

    def time(self) -> float:
        return time.time()

# Define Protocol for Log Provider
class LogProvider(Protocol):
    @abstractmethod
    def log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log a message with a severity level"""
        pass

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.INFO, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.ERROR, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.WARNING, message, extra)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log(logging.DEBUG, message, extra)

class FileLogProvider:
    """Direct python logging provider for CLI"""
    def __init__(self, logger_name: str = "dnd_game"):
        self.logger = logging.getLogger(logger_name)

    def log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.logger.log(level, message, extra=extra)

# Database log provider will be defined in services to avoid circular imports
# or needing models at core level, but we define the interface here.

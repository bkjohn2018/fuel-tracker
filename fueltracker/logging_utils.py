"""
Logging utilities for Fuel Tracker.
Provides structured logging with JSON-like formatting.
"""

from datetime import datetime
import json
import logging
from typing import Optional


class JSONishFormatter(logging.Formatter):
    """Custom formatter that outputs log messages in a JSON-like format."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON-like string."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }

        # Add extra fields if they exist
        if hasattr(record, 'extra') and record.extra:
            log_entry.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger with JSON-like formatting.

    Args:
        name: Logger name (usually __name__)
        level: Optional logging level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Set default level
        if level is None:
            level = logging.INFO

        logger.setLevel(level)

        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)

        # Set formatter
        formatter = JSONishFormatter()
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Prevent propagation to root logger to avoid duplicate messages
        logger.propagate = False

    return logger

"""
Cache management for EIA data with freshness checking.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from .config import DATA_DIR
from .logging_utils import get_logger

logger = get_logger(__name__)

# Cache directory
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Marker file for last successful cache
LAST_SUCCESS_MARKER = CACHE_DIR / "last_success.json"


def get_last_success_path() -> Path:
    """
    Get the path for the last successful cache file.

    Returns:
        Path to the timestamped cache file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_file = CACHE_DIR / f"eia_data_{timestamp}.json"

    logger.debug("Generated cache file path", extra={"cache_file": str(cache_file)})
    return cache_file


def record_successful_payload(payload: Dict[str, Any]) -> Path:
    """
    Record a successful API payload to cache.

    Args:
        payload: The successful API response payload

    Returns:
        Path to the saved cache file
    """
    cache_file = get_last_success_path()

    try:
        # Save the payload with timestamp
        cache_data = {"timestamp": datetime.now().isoformat(), "payload": payload}

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)

        # Update the marker file
        marker_data = {
            "last_success_file": cache_file.name,
            "last_success_time": cache_data["timestamp"],
            "last_success_path": str(cache_file),
        }

        with open(LAST_SUCCESS_MARKER, 'w') as f:
            json.dump(marker_data, f, indent=2)

        logger.info(
            "Successfully cached payload",
            extra={
                "cache_file": str(cache_file),
                "payload_keys": list(payload.keys())
                if isinstance(payload, dict)
                else "non_dict",
            },
        )

        return cache_file

    except Exception as e:
        logger.error("Failed to cache payload", extra={"error": str(e)})
        raise


def is_cache_fresh(business_days: int = 3) -> bool:
    """
    Check if the cache is fresh within the specified business days.

    Args:
        business_days: Number of business days to consider cache fresh

    Returns:
        True if cache is fresh, False otherwise
    """
    if not LAST_SUCCESS_MARKER.exists():
        logger.debug("No cache marker found")
        return False

    try:
        with open(LAST_SUCCESS_MARKER, 'r') as f:
            marker_data = json.load(f)

        last_success_time = datetime.fromisoformat(marker_data["last_success_time"])
        current_time = datetime.now()

        # Calculate business days difference
        business_day_offset = pd.tseries.offsets.BusinessDay(n=business_days)
        cutoff_time = current_time - business_day_offset

        is_fresh = last_success_time > cutoff_time

        logger.debug(
            "Cache freshness check",
            extra={
                "last_success": last_success_time.isoformat(),
                "cutoff_time": cutoff_time.isoformat(),
                "business_days": business_days,
                "is_fresh": is_fresh,
            },
        )

        return is_fresh

    except Exception as e:
        logger.error("Failed to check cache freshness", extra={"error": str(e)})
        return False


def get_last_success_info() -> Optional[Dict[str, Any]]:
    """
    Get information about the last successful cache.

    Returns:
        Dictionary with cache info or None if no cache exists
    """
    if not LAST_SUCCESS_MARKER.exists():
        return None

    try:
        with open(LAST_SUCCESS_MARKER, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to read cache marker", extra={"error": str(e)})
        return None

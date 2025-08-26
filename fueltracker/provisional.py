"""
Provisional mode logic for determining when to block data publishing.
"""

from typing import Dict, Any, Optional
from .cache import is_cache_fresh, get_last_success_info
from .config import CACHE_TTL_BUSINESS_DAYS
from .logging_utils import get_logger

logger = get_logger(__name__)


def should_block_publish() -> bool:
    """
    Determine if publishing should be blocked due to stale cache.
    
    Returns:
        True if publishing should be blocked, False otherwise
    """
    cache_fresh = is_cache_fresh(CACHE_TTL_BUSINESS_DAYS)
    
    if not cache_fresh:
        logger.warning("Cache is stale, blocking publish", extra={
            "cache_ttl_days": CACHE_TTL_BUSINESS_DAYS
        })
        return True
    
    logger.debug("Cache is fresh, allowing publish")
    return False


def get_provisional_status() -> Dict[str, Any]:
    """
    Get the current provisional mode status.
    
    Returns:
        Dictionary with mode information including:
        - mode: "normal" or "provisional"
        - reason: Explanation for the current mode
        - last_asof: Timestamp of last successful data
    """
    cache_fresh = is_cache_fresh(CACHE_TTL_BUSINESS_DAYS)
    last_success_info = get_last_success_info()
    
    if cache_fresh and last_success_info:
        status = {
            "mode": "normal",
            "reason": "Cache is fresh within business day limit",
            "last_asof": last_success_info.get("last_success_time", "unknown"),
            "cache_file": last_success_info.get("last_success_file", "unknown")
        }
    else:
        status = {
            "mode": "provisional",
            "reason": "Cache is stale or missing",
            "last_asof": last_success_info.get("last_success_time", "none") if last_success_info else "none",
            "cache_file": last_success_info.get("last_success_file", "none") if last_success_info else "none"
        }
    
    # Add additional metadata
    status.update({
        "cache_ttl_business_days": CACHE_TTL_BUSINESS_DAYS,
        "cache_fresh": cache_fresh,
        "timestamp": "now"  # This would be better as actual timestamp
    })
    
    logger.info("Provisional status determined", extra=status)
    return status


def check_publish_eligibility(api_success: bool = True) -> Dict[str, Any]:
    """
    Check if data can be published based on cache freshness and API success.
    
    Args:
        api_success: Whether the current API call was successful
        
    Returns:
        Dictionary with publish eligibility information
    """
    cache_fresh = is_cache_fresh(CACHE_TTL_BUSINESS_DAYS)
    last_success_info = get_last_success_info()
    
    # Determine if we should block publishing
    should_block = should_block_publish()
    
    # If cache is stale AND current API call failed, definitely block
    if should_block and not api_success:
        mode = "provisional"
        reason = "Cache is stale and current API call failed"
        can_publish = False
    elif should_block:
        mode = "provisional"
        reason = "Cache is stale, but current API call succeeded"
        can_publish = True  # We can publish new data
    else:
        mode = "normal"
        reason = "Cache is fresh"
        can_publish = True
    
    status = {
        "mode": mode,
        "reason": reason,
        "can_publish": can_publish,
        "last_asof": last_success_info.get("last_success_time", "none") if last_success_info else "none",
        "cache_fresh": cache_fresh,
        "api_success": api_success,
        "cache_ttl_business_days": CACHE_TTL_BUSINESS_DAYS
    }
    
    logger.info("Publish eligibility determined", extra=status)
    return status

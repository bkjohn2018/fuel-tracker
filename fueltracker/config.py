"""
Configuration module for Fuel Tracker.
Loads environment variables and sets up project directories.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Load environment variables
EIA_API_KEY: Optional[str] = os.getenv("EIA_API_KEY")

# Project directories
DATA_DIR = Path("data")
OUTPUTS_DIR = Path("outputs")

# Ensure directories exist at import
DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Output file constants
PANEL_FILE = "panel_monthly.parquet"
METRICS_FILE = "metrics.csv"
FORECAST_FILE = "forecast_12m.csv"

# Cache settings
CACHE_TTL_BUSINESS_DAYS = 3

# EIA endpoints configuration
EIA_ENDPOINTS_FILE = Path("config/eia_endpoints.yml")


def get_eia_endpoint_config(endpoint_key: str) -> Optional[Dict[str, Any]]:
    """
    Get EIA endpoint configuration from YAML file.

    Args:
        endpoint_key: Key for the endpoint configuration

    Returns:
        Endpoint configuration dictionary or None if not found
    """
    if not EIA_ENDPOINTS_FILE.exists():
        return None

    try:
        with open(EIA_ENDPOINTS_FILE, 'r', encoding='utf-8') as f:
            endpoints_config = yaml.safe_load(f)

        return endpoints_config.get(endpoint_key)
    except Exception as e:
        print(f"Warning: Failed to load EIA endpoints config: {e}")
        return None


# Validation
if not EIA_API_KEY:
    print("Warning: EIA_API_KEY not found in environment variables.")
    print("Please set EIA_API_KEY in your .env file or environment.")

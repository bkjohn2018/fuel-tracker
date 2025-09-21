"""
EIA v2 API client with retry logic and data normalization.
"""

from typing import Any, Dict

import pandas as pd
import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .logging_utils import get_logger

logger = get_logger(__name__)


class EIAClient:
    """Client for EIA v2 API with retry logic and data normalization."""

    BASE_URL = "https://api.eia.gov/v2"

    def __init__(self, api_key: str):
        """
        Initialize EIA client.

        Args:
            api_key: EIA API key for authentication
        """
        self.api_key = api_key
        logger.info("EIA client initialized", extra={"base_url": self.BASE_URL})

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(
            (requests.exceptions.RequestException, requests.exceptions.HTTPError)
        ),
    )
    def _get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make GET request with retry logic.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.exceptions.RequestException: On request failure after retries
            requests.exceptions.HTTPError: On HTTP error after retries
        """
        # Inject API key into params
        params_with_key = params.copy()
        params_with_key["api_key"] = self.api_key

        logger.debug(
            "Making EIA API request", extra={"url": url, "params": params_with_key}
        )

        response = requests.get(url, params=params_with_key, timeout=30)

        # Check for rate limiting and server errors
        if response.status_code == 429:
            logger.warning("Rate limited by EIA API", extra={"status_code": 429})
            raise requests.exceptions.HTTPError("Rate limited", response=response)

        if response.status_code >= 500:
            logger.warning(
                "EIA API server error", extra={"status_code": response.status_code}
            )
            raise requests.exceptions.HTTPError(
                f"Server error: {response.status_code}", response=response
            )

        response.raise_for_status()

        data = response.json()
        logger.debug(
            "EIA API response received", extra={"status_code": response.status_code}
        )

        return data

    def fetch_series(self, endpoint: str, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Fetch data series from EIA API and normalize to DataFrame.

        Args:
            endpoint: Full endpoint URL or endpoint key from config
            params: Query parameters for the endpoint

        Returns:
            Normalized pandas DataFrame
        """
        # If endpoint is a key, look it up in config
        if not endpoint.startswith('http'):
            from .config import get_eia_endpoint_config

            endpoint_config = get_eia_endpoint_config(endpoint)
            if endpoint_config:
                url = endpoint_config['endpoint']
                # Merge config params with provided params
                config_params = endpoint_config.get('params', {})
                merged_params = {**config_params, **params}
                logger.info(
                    "Using endpoint config",
                    extra={"endpoint_key": endpoint, "url": url},
                )
            else:
                # Fallback to treating as relative endpoint
                url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
                merged_params = params
                logger.info(
                    "Using relative endpoint", extra={"endpoint": endpoint, "url": url}
                )
        else:
            url = endpoint
            merged_params = params
            logger.info("Using full URL endpoint", extra={"url": url})

        try:
            logger.info(
                "Fetching EIA series",
                extra={"endpoint": endpoint, "url": url, "params": merged_params},
            )
            data = self._get(url, merged_params)

            # Normalize JSON response to DataFrame
            df = self._normalize_response(data)

            logger.info(
                "Series fetched successfully",
                extra={
                    "endpoint": endpoint,
                    "url": url,
                    "rows": len(df),
                    "columns": list(df.columns),
                },
            )

            return df

        except Exception as e:
            logger.error(
                "Failed to fetch EIA series",
                extra={"endpoint": endpoint, "url": url, "error": str(e)},
            )
            raise

    def _normalize_response(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Normalize EIA API response to pandas DataFrame.

        Args:
            data: Raw API response

        Returns:
            Normalized DataFrame
        """
        try:
            # Extract the response data
            if "response" in data and "data" in data["response"]:
                response_data = data["response"]["data"]
            else:
                response_data = data.get("data", [])

            if not response_data:
                logger.warning("No data found in EIA response")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(response_data)

            # Handle common EIA data structures
            if "period" in df.columns and "value" in df.columns:
                # Standard time series format
                df["period"] = pd.to_datetime(df["period"])
                df["value"] = pd.to_numeric(df["value"], errors="coerce")

                # Sort by period
                df = df.sort_values("period").reset_index(drop=True)

            return df

        except Exception as e:
            logger.error("Failed to normalize EIA response", extra={"error": str(e)})
            raise ValueError(f"Failed to normalize EIA response: {e}") from e

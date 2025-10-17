"""EIA v2 API client with retry logic, normalization, and fallbacks."""

from __future__ import annotations

import os
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

    def __init__(self, api_key: str, *, allow_sample_fallback: bool | None = None):
        """
        Initialize EIA client.

        Args:
            api_key: EIA API key for authentication
        """
        self.api_key = api_key
        self.allow_sample_fallback = (
            allow_sample_fallback
            if allow_sample_fallback is not None
            else self._determine_sample_policy()
        )
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

            df = self._normalize_response(data)

            if df.empty:
                logger.warning(
                    "No data found in EIA response",
                    extra={
                        "endpoint": endpoint,
                        "url": url,
                        "params": merged_params,
                    },
                )
                fallback_df = self._maybe_get_sample_data()
                if fallback_df is not None:
                    logger.info(
                        "Using sample fallback data",
                        extra={
                            "endpoint": endpoint,
                            "rows": len(fallback_df),
                        },
                    )
                    return fallback_df

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
                extra={
                    "endpoint": endpoint,
                    "url": url,
                    "params": merged_params,
                    "error": str(e),
                },
            )
            fallback_df = self._maybe_get_sample_data()
            if fallback_df is not None:
                logger.info(
                    "Using sample fallback data after fetch failure",
                    extra={"endpoint": endpoint, "rows": len(fallback_df)},
                )
                return fallback_df
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _determine_sample_policy(self) -> bool:
        """Decide whether the client should fall back to bundled sample data."""

        env_value = os.getenv("FUELTRACKER_ALLOW_SAMPLE_DATA")
        if env_value is not None:
            return env_value.lower() in {"1", "true", "yes", "on"}

        placeholder_tokens = {"test", "sample", "demo", "placeholder", "fake", "dummy"}
        api_key_lower = self.api_key.lower()
        return any(token in api_key_lower for token in placeholder_tokens)

    def _maybe_get_sample_data(self) -> pd.DataFrame | None:
        """Return bundled sample data when fallback policy allows it."""

        if not self.allow_sample_fallback:
            return None

        sample_payload = {
            "response": {
                "data": [
                    {
                        "period": "2024-01",
                        "value": "75.50",
                        "unit": "dollars per barrel",
                    },
                    {
                        "period": "2024-02",
                        "value": "78.20",
                        "unit": "dollars per barrel",
                    },
                    {
                        "period": "2024-03",
                        "value": "82.10",
                        "unit": "dollars per barrel",
                    },
                ]
            }
        }

        logger.debug("Loaded bundled sample data for fallback")
        return self._normalize_response(sample_payload)

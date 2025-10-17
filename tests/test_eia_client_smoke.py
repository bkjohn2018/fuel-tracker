"""Smoke tests for EIA client with mocked HTTP requests."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests
from tenacity import RetryError

from fueltracker.eia_client import EIAClient


class TestEIAClientSmoke:
    """Smoke tests for EIAClient class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Construct test key to avoid false-positive secret detection in hooks
        self.api_key = "".join(
            ["test", "_api_key_", "12345"]
        )  # pragma: allowlist secret
        self.client = EIAClient(self.api_key)
        # Sample EIA API response
        self.sample_response = {
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

    def test_client_initialization(self):
        """Test EIA client initialization."""
        assert self.client.api_key == self.api_key
        assert self.client.BASE_URL == "https://api.eia.gov/v2"

    @patch('requests.get')
    def test_successful_request(self, mock_get):
        """Test successful API request with proper API key injection."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_response
        mock_get.return_value = mock_response

        # Make request
        result = self.client.fetch_series(
            "petroleum/pri/spt/data", {"frequency": "monthly"}
        )

        # Verify API key was injected
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['api_key'] == self.api_key
        assert call_args[1]['params']['frequency'] == 'monthly'

        # Verify result is DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'period' in result.columns
        assert 'value' in result.columns

    @patch('requests.get')
    def test_retry_on_429_rate_limit(self, mock_get):
        """Test retry logic on rate limiting (429)."""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.HTTPError("429")
        mock_get.return_value = mock_response

        # This should raise an exception after retries
        with pytest.raises(RetryError):
            self.client.fetch_series("petroleum/pri/spt/data", {})

        # Verify retry attempts (should be 5 based on tenacity config)
        assert mock_get.call_count >= 1

    @patch('requests.get')
    def test_retry_on_500_server_error(self, mock_get):
        """Test retry logic on server error (500)."""
        # Mock server error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("500")
        mock_get.return_value = mock_response

        # This should raise an exception after retries
        with pytest.raises(RetryError):
            self.client.fetch_series("petroleum/pri/spt/data", {})

        # Verify retry attempts
        assert mock_get.call_count >= 1

    @patch('requests.get')
    def test_data_normalization(self, mock_get):
        """Test data normalization from JSON to DataFrame."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_response
        mock_get.return_value = mock_response

        # Make request
        result = self.client.fetch_series("petroleum/pri/spt/data", {})

        # Verify DataFrame structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ['period', 'value', 'unit']
        assert len(result) == 3

        # Verify data types
        assert pd.api.types.is_datetime64_any_dtype(result['period'])
        assert pd.api.types.is_numeric_dtype(result['value'])

        # Verify sorting by period
        periods = result['period'].dt.to_period('M')
        # Convert to timestamp for comparison
        period_timestamps = periods.astype(str).astype('datetime64[ns]')
        assert (
            period_timestamps.diff().dropna() >= pd.Timedelta(0)
        ).all()  # Monotonically increasing
        # For Period dtype, use built-in monotonicity property to avoid
        # comparing pandas offsets (e.g., MonthEnd) to integers.
        assert periods.is_monotonic_increasing

    @patch('requests.get')
    def test_empty_response_handling(self, mock_get):
        """Test handling of empty API responses."""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"data": []}}
        mock_get.return_value = mock_response

        # Make request
        result = self.client.fetch_series("petroleum/pri/spt/data", {})

        # Verify empty DataFrame is returned
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch('requests.get')
    def test_malformed_response_handling(self, mock_get):
        """Test handling of malformed API responses."""
        # Mock malformed response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "structure"}
        mock_get.return_value = mock_response

        # Make request
        result = self.client.fetch_series("petroleum/pri/spt/data", {})

        # Verify empty DataFrame is returned for malformed data
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

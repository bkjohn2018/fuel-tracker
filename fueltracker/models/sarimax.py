"""
SARIMAX forecasting model for Fuel Tracker.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


class SARIMAX:
    """SARIMAX forecasting model with exogenous variable support."""

    def __init__(
        self,
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 12),
        exog_columns: Optional[List[str]] = None,
    ):
        """
        Initialize SARIMAX model.

        Args:
            order: (p, d, q) order for non-seasonal components
            seasonal_order: (P, D, Q, s) order for seasonal components
            exog_columns: List of exogenous variable column names
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.exog_columns = exog_columns or []
        self.fitted = False
        self.last_values = None
        self.seasonal_pattern = None
        self.trend_coef = None

        logger.info(
            "SARIMAX model initialized",
            extra={
                "order": order,
                "seasonal_order": seasonal_order,
                "exog_columns": exog_columns,
            },
        )

    def fit(self, y: pd.Series, exog: Optional[pd.DataFrame] = None) -> 'SARIMAX':
        """
        Fit the model to training data.

        Args:
            y: Training time series
            exog: Exogenous variables DataFrame (optional)

        Returns:
            Self for method chaining
        """
        if len(y) < self.seasonal_order[3] * 2:
            raise ValueError(
                f"Training data must have at least "
                f"{self.seasonal_order[3] * 2} observations"
            )

        # Simple SARIMAX-like implementation
        # Extract seasonal pattern
        seasonal_pattern = self._extract_seasonal_pattern(y, self.seasonal_order[3])

        # Extract trend
        trend = self._extract_trend(y)

        # Handle exogenous variables if present
        if exog is not None and not exog.empty and self.exog_columns:
            self.exog_coefs = self._fit_exog_relationship(y, exog)
            logger.info(
                "Exogenous variables fitted", extra={"exog_coefs": self.exog_coefs}
            )
        else:
            self.exog_coefs = None

        # Store fitted components
        self.seasonal_pattern = seasonal_pattern
        self.trend_coef = trend
        self.last_values = y.tail(self.seasonal_order[3]).values
        self.fitted = True

        logger.info(
            "SARIMAX model fitted",
            extra={
                "training_length": len(y),
                "seasonal_period": self.seasonal_order[3],
                "seasonal_std": np.std(seasonal_pattern),
                "trend_coef": self.trend_coef,
                "has_exog": self.exog_coefs is not None,
            },
        )

        return self

    def predict(self, horizon: int, exog: Optional[pd.DataFrame] = None) -> np.ndarray:
        """
        Generate forecasts.

        Args:
            horizon: Number of steps ahead to forecast
            exog: Exogenous variables for forecast period (optional)

        Returns:
            Array of forecasts
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions")

        forecasts = []
        current_values = self.last_values.copy()

        for i in range(horizon):
            # Seasonal component
            seasonal_idx = i % self.seasonal_order[3]
            seasonal_component = self.seasonal_pattern[seasonal_idx]

            # Trend component
            trend_component = self.trend_coef * (i + 1)

            # Exogenous component
            exog_component = 0.0
            if self.exog_coefs is not None and exog is not None and not exog.empty:
                if i < len(exog):
                    exog_row = exog.iloc[i]
                    for col, coef in self.exog_coefs.items():
                        if col in exog_row:
                            exog_component += coef * exog_row[col]

            # Combine components (SARIMAX-like)
            forecast = (
                current_values[-1]
                + seasonal_component
                + trend_component
                + exog_component
            )

            # Ensure non-negative
            forecast = max(0, forecast)
            forecasts.append(forecast)

            # Update current values for next iteration
            current_values = np.roll(current_values, -1)
            current_values[-1] = forecast

        logger.debug(
            "Generated SARIMAX forecasts",
            extra={
                "horizon": horizon,
                "seasonal_period": self.seasonal_order[3],
                "has_exog": self.exog_coefs is not None,
            },
        )

        return np.array(forecasts)

    def fit_predict(
        self, y: pd.Series, horizon: int, exog: Optional[pd.DataFrame] = None
    ) -> np.ndarray:
        """
        Fit model and generate forecasts in one step.

        Args:
            y: Training time series
            horizon: Number of steps ahead to forecast
            exog: Exogenous variables (optional)

        Returns:
            Array of forecasts
        """
        return self.fit(y, exog).predict(horizon, exog)

    def _extract_seasonal_pattern(self, y: pd.Series, period: int) -> np.ndarray:
        """
        Extract seasonal pattern using simple averaging.

        Args:
            y: Time series data
            period: Seasonal period

        Returns:
            Seasonal pattern array
        """
        # Reshape data into seasonal periods
        n_periods = len(y) // period
        if n_periods == 0:
            return np.zeros(period)

        # Take the last few periods for more recent seasonal pattern
        recent_periods = min(n_periods, 3)
        start_idx = len(y) - (recent_periods * period)

        seasonal_data = y.iloc[start_idx:].values.reshape(-1, period)

        # Calculate seasonal pattern as mean across periods
        seasonal_pattern = np.mean(seasonal_data, axis=0)

        # Center the pattern (remove mean)
        seasonal_pattern = seasonal_pattern - np.mean(seasonal_pattern)

        return seasonal_pattern

    def _extract_trend(self, y: pd.Series) -> float:
        """
        Extract trend using simple linear regression.

        Args:
            y: Time series data

        Returns:
            Trend coefficient
        """
        if len(y) < 2:
            return 0.0

        # Use last portion of data for trend estimation
        trend_length = min(len(y), 24)  # Use last 24 observations
        y_trend = y.tail(trend_length)
        x_trend = np.arange(len(y_trend))

        # Simple linear trend
        if len(y_trend) > 1:
            trend_coef = np.polyfit(x_trend, y_trend, 1)[0]
        else:
            trend_coef = 0.0

        return trend_coef

    def _fit_exog_relationship(
        self, y: pd.Series, exog: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Fit relationship between target and exogenous variables.

        Args:
            y: Target variable
            exog: Exogenous variables

        Returns:
            Dictionary of coefficients for each exogenous variable
        """
        if exog.empty or not self.exog_columns:
            return {}

        # Align data
        common_length = min(len(y), len(exog))
        y_aligned = y.tail(common_length)
        exog_aligned = exog.tail(common_length)

        # Simple linear relationship for each exogenous variable
        coefs = {}
        for col in self.exog_columns:
            if col in exog_aligned.columns:
                # Simple correlation-based coefficient
                correlation = np.corrcoef(y_aligned.values, exog_aligned[col].values)[
                    0, 1
                ]
                if not np.isnan(correlation):
                    # Scale coefficient by target std
                    coefs[col] = (
                        correlation * np.std(y_aligned) / np.std(exog_aligned[col])
                    )
                else:
                    coefs[col] = 0.0
            else:
                coefs[col] = 0.0

        return coefs


def rolling_backtest(
    y: pd.Series,
    horizon: int = 12,
    last_n_months: int = 60,
    model_class=SARIMAX,
    exog: Optional[pd.DataFrame] = None,
    **model_kwargs,
) -> pd.DataFrame:
    """
    Perform rolling backtest with SARIMAX model.

    Args:
        y: Time series data
        horizon: Forecast horizon
        last_n_months: Number of months to use for backtesting
        model_class: Model class to use
        exog: Exogenous variables DataFrame (optional)
        **model_kwargs: Additional arguments for model initialization

    Returns:
        DataFrame with backtest results
    """
    if len(y) < last_n_months:
        raise ValueError(f"Data must have at least {last_n_months} observations")

    # Use only the last N months for backtesting
    y_backtest = y.tail(last_n_months)
    exog_backtest = exog.tail(last_n_months) if exog is not None else None

    logger.info(
        "Starting SARIMAX rolling backtest",
        extra={
            "total_length": len(y),
            "backtest_length": len(y_backtest),
            "horizon": horizon,
            "last_n_months": last_n_months,
            "has_exog": exog_backtest is not None,
        },
    )

    results = []

    # Perform rolling backtest
    for i in range(horizon, len(y_backtest)):
        # Training data: everything up to current position
        train_data = y_backtest.iloc[:i]
        train_exog = exog_backtest.iloc[:i] if exog_backtest is not None else None

        # Skip if we don't have enough training data
        required_period = model_kwargs.get('seasonal_order', (1, 1, 1, 12))[3] * 2
        if len(train_data) < required_period:
            continue

        # Actual values for comparison
        actual = y_backtest.iloc[i : i + horizon]
        # Note: actual_exog not used in current implementation

        # Skip if we don't have enough future data
        if len(actual) < horizon:
            continue

        # Fit model and predict
        model = model_class(**model_kwargs)
        forecasts = model.fit_predict(train_data, horizon, train_exog)

        # Calculate metrics for this split
        split_metrics = _calculate_split_metrics(actual.values, forecasts)

        # Store results
        split_result = {
            'split_end': y_backtest.index[i - 1],
            'forecast_start': y_backtest.index[i],
            'forecast_end': y_backtest.index[min(i + horizon - 1, len(y_backtest) - 1)],
            'train_length': len(train_data),
            'horizon': len(actual),
            **split_metrics,
        }

        results.append(split_result)

    results_df = pd.DataFrame(results)

    logger.info(
        "SARIMAX rolling backtest completed",
        extra={
            "splits": len(results_df),
            "avg_mae": results_df['mae'].mean() if not results_df.empty else 0,
            "avg_smape": results_df['smape'].mean() if not results_df.empty else 0,
        },
    )

    return results_df


def _calculate_split_metrics(
    actual: np.ndarray, forecast: np.ndarray
) -> Dict[str, float]:
    """
    Calculate metrics for a single backtest split.

    Args:
        actual: Actual values
        forecast: Forecasted values

    Returns:
        Dictionary with metrics
    """
    # Ensure arrays have the same length
    min_len = min(len(actual), len(forecast))
    actual = actual[:min_len]
    forecast = forecast[:min_len]

    # Calculate MAE
    mae = np.mean(np.abs(actual - forecast))

    # Calculate sMAPE
    smape_numerator = np.abs(actual - forecast)
    smape_denominator = (np.abs(actual) + np.abs(forecast)) / 2
    smape = 100 * np.mean(smape_numerator / smape_denominator)

    # Additional metrics
    rmse = np.sqrt(np.mean((actual - forecast) ** 2))
    mape = 100 * np.mean(np.abs((actual - forecast) / actual))

    return {
        'mae': float(mae),
        'smape': float(smape),
        'rmse': float(rmse),
        'mape': float(mape),
    }


def generate_sarimax_forecast(
    y: pd.Series, horizon: int = 12, exog: Optional[pd.DataFrame] = None, **model_kwargs
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Generate SARIMAX forecast and return with model info.

    Args:
        y: Historical time series
        horizon: Forecast horizon
        exog: Exogenous variables (optional)
        **model_kwargs: Additional arguments for model initialization

    Returns:
        Tuple of (forecasts, model_info)
    """
    model = SARIMAX(**model_kwargs)
    forecasts = model.fit_predict(y, horizon, exog)

    model_info = {
        'model_type': 'SARIMAX',
        'order': model.order,
        'seasonal_order': model.seasonal_order,
        'fitted': model.fitted,
        'training_length': len(y),
        'horizon': horizon,
        'has_exog': model.exog_coefs is not None,
    }

    logger.info("SARIMAX forecast generated", extra=model_info)

    return forecasts, model_info

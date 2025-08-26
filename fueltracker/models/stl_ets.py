"""
STL-ETS forecasting model for Fuel Tracker.
"""

from typing import Dict, Tuple

import numpy as np
import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


class STLETS:
    """STL-ETS forecasting model combining seasonal decomposition with 
    exponential smoothing."""

    def __init__(
        self, period: int = 12, seasonal_window: int = 7, trend_window: int = 21
    ):
        """
        Initialize STL-ETS model.

        Args:
            period: Seasonal period (default 12 for monthly data)
            seasonal_window: Window size for seasonal decomposition
            trend_window: Window size for trend decomposition
        """
        self.period = period
        self.seasonal_window = seasonal_window
        self.trend_window = trend_window
        self.fitted = False
        self.seasonal_pattern = None
        self.trend_coef = None
        self.last_value = None

        logger.info(
            "STL-ETS model initialized",
            extra={
                "period": period,
                "seasonal_window": seasonal_window,
                "trend_window": trend_window,
            },
        )

    def fit(self, y: pd.Series) -> 'STLETS':
        """
        Fit the model to training data.

        Args:
            y: Training time series

        Returns:
            Self for method chaining
        """
        if len(y) < self.period * 2:
            raise ValueError(
                f"Training data must have at least {self.period * 2} observations"
            )

        # Simple seasonal decomposition (STL-like)
        seasonal_pattern = self._extract_seasonal_pattern(y)
        trend = self._extract_trend(y)

        # Store fitted components
        self.seasonal_pattern = seasonal_pattern
        self.trend_coef = trend
        self.last_value = y.iloc[-1]
        self.fitted = True

        logger.info(
            "STL-ETS model fitted",
            extra={
                "training_length": len(y),
                "period": self.period,
                "seasonal_std": np.std(seasonal_pattern),
                "trend_coef": self.trend_coef,
            },
        )

        return self

    def predict(self, horizon: int) -> np.ndarray:
        """
        Generate forecasts.

        Args:
            horizon: Number of steps ahead to forecast

        Returns:
            Array of forecasts
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before making predictions")

        forecasts = []
        current_value = self.last_value

        for i in range(horizon):
            # Seasonal component
            seasonal_idx = i % self.period
            seasonal_component = self.seasonal_pattern[seasonal_idx]

            # Trend component
            trend_component = self.trend_coef * (i + 1)

            # Combine components
            forecast = current_value + seasonal_component + trend_component

            # Ensure non-negative (fuel consumption can't be negative)
            forecast = max(0, forecast)
            forecasts.append(forecast)

            # Update current value for next iteration
            current_value = forecast

        logger.debug(
            "Generated STL-ETS forecasts",
            extra={"horizon": horizon, "period": self.period},
        )

        return np.array(forecasts)

    def fit_predict(self, y: pd.Series, horizon: int) -> np.ndarray:
        """
        Fit model and generate forecasts in one step.

        Args:
            y: Training time series
            horizon: Number of steps ahead to forecast

        Returns:
            Array of forecasts
        """
        return self.fit(y).predict(horizon)

    def _extract_seasonal_pattern(self, y: pd.Series) -> np.ndarray:
        """
        Extract seasonal pattern using simple averaging.

        Args:
            y: Time series data

        Returns:
            Seasonal pattern array
        """
        # Reshape data into seasonal periods
        n_periods = len(y) // self.period
        if n_periods == 0:
            return np.zeros(self.period)

        # Take the last few periods for more recent seasonal pattern
        recent_periods = min(n_periods, 3)
        start_idx = len(y) - (recent_periods * self.period)

        seasonal_data = y.iloc[start_idx:].values.reshape(-1, self.period)

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
        trend_length = min(len(y), self.trend_window)
        y_trend = y.tail(trend_length)
        x_trend = np.arange(len(y_trend))

        # Simple linear trend
        if len(y_trend) > 1:
            trend_coef = np.polyfit(x_trend, y_trend, 1)[0]
        else:
            trend_coef = 0.0

        return trend_coef


def rolling_backtest(
    y: pd.Series,
    horizon: int = 12,
    last_n_months: int = 60,
    model_class=STLETS,
    **model_kwargs,
) -> pd.DataFrame:
    """
    Perform rolling backtest with STL-ETS model.

    Args:
        y: Time series data
        horizon: Forecast horizon
        last_n_months: Number of months to use for backtesting
        model_class: Model class to use
        **model_kwargs: Additional arguments for model initialization

    Returns:
        DataFrame with backtest results
    """
    if len(y) < last_n_months:
        raise ValueError(f"Data must have at least {last_n_months} observations")

    # Use only the last N months for backtesting
    y_backtest = y.tail(last_n_months)

    logger.info(
        "Starting STL-ETS rolling backtest",
        extra={
            "total_length": len(y),
            "backtest_length": len(y_backtest),
            "horizon": horizon,
            "last_n_months": last_n_months,
        },
    )

    results = []

    # Perform rolling backtest
    for i in range(horizon, len(y_backtest)):
        # Training data: everything up to current position
        train_data = y_backtest.iloc[:i]

        # Skip if we don't have enough training data
        required_period = model_kwargs.get('period', 12) * 2
        if len(train_data) < required_period:
            continue

        # Actual values for comparison
        actual = y_backtest.iloc[i : i + horizon]

        # Skip if we don't have enough future data
        if len(actual) < horizon:
            continue

        # Fit model and predict
        model = model_class(**model_kwargs)
        forecasts = model.fit_predict(train_data, horizon)

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
        "STL-ETS rolling backtest completed",
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


def generate_stl_ets_forecast(
    y: pd.Series, horizon: int = 12, **model_kwargs
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Generate STL-ETS forecast and return with model info.

    Args:
        y: Historical time series
        horizon: Forecast horizon
        **model_kwargs: Additional arguments for model initialization

    Returns:
        Tuple of (forecasts, model_info)
    """
    model = STLETS(**model_kwargs)
    forecasts = model.fit_predict(y, horizon)

    model_info = {
        'model_type': 'STLETS',
        'period': model.period,
        'fitted': model.fitted,
        'training_length': len(y),
        'horizon': horizon,
    }

    logger.info("STL-ETS forecast generated", extra=model_info)

    return forecasts, model_info

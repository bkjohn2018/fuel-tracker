"""
Baseline forecasting models for Fuel Tracker.
"""

from typing import Dict, Tuple

import numpy as np
import pandas as pd

from ..logging_utils import get_logger

logger = get_logger(__name__)


class SeasonalNaive:
    """Seasonal Naïve forecasting model."""

    def __init__(self, period: int = 12):
        """
        Initialize Seasonal Naïve model.

        Args:
            period: Seasonal period (default 12 for monthly data)
        """
        self.period = period
        self.fitted = False
        self.last_values = None

        logger.info("Seasonal Naïve model initialized", extra={"period": period})

    def fit(self, y: pd.Series) -> 'SeasonalNaive':
        """
        Fit the model to training data.

        Args:
            y: Training time series

        Returns:
            Self for method chaining
        """
        if len(y) < self.period:
            raise ValueError(
                f"Training data must have at least {self.period} observations"
            )

        # Store the last 'period' values for forecasting
        self.last_values = y.tail(self.period).values
        self.fitted = True

        logger.info(
            "Seasonal Naïve model fitted",
            extra={"training_length": len(y), "period": self.period},
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

        # Repeat the seasonal pattern
        forecasts = []
        for i in range(horizon):
            forecast_idx = i % self.period
            forecasts.append(self.last_values[forecast_idx])

        logger.debug(
            "Generated forecasts", extra={"horizon": horizon, "period": self.period}
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


def rolling_backtest(
    y: pd.Series,
    horizon: int = 12,
    last_n_months: int = 60,
    model_class=SeasonalNaive,
    **model_kwargs,
) -> pd.DataFrame:
    """
    Perform rolling backtest with frozen-origin style.

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
        "Starting rolling backtest",
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
        # Check if we have enough data for the seasonal period
        required_period = model_kwargs.get(
            'period', 12
        )  # Default to 12 if not specified
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
        "Rolling backtest completed",
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


def generate_baseline_forecast(
    y: pd.Series, horizon: int = 12, model_class=SeasonalNaive, **model_kwargs
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Generate baseline forecast and return with model info.

    Args:
        y: Historical time series
        horizon: Forecast horizon
        model_class: Model class to use
        **model_kwargs: Additional arguments for model initialization

    Returns:
        Tuple of (forecasts, model_info)
    """
    model = model_class(**model_kwargs)
    forecasts = model.fit_predict(y, horizon)

    model_info = {
        'model_type': model_class.__name__,
        'period': getattr(model, 'period', None),
        'fitted': model.fitted,
        'training_length': len(y),
        'horizon': horizon,
    }

    logger.info("Baseline forecast generated", extra=model_info)

    return forecasts, model_info

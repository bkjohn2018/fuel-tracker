"""STL-ETS forecasting model stub for Fuel Tracker."""

import pandas as pd
import numpy as np
from typing import Type, Dict, Any, Tuple
from ..logging_utils import get_logger

logger = get_logger(__name__)


class STLETS:
    """STL-ETS forecasting model stub."""
    
    def __init__(self, period: int = 12):
        """
        Initialize STL-ETS model.
        
        Args:
            period: Seasonal period (e.g., 12 for monthly data)
        """
        self.period = period
        self.fitted = False
        self.training_data = None
    
    def fit(self, y: pd.Series) -> 'STLETS':
        """
        Fit the model to training data.
        
        Args:
            y: Training time series
            
        Returns:
            Self for method chaining
        """
        self.training_data = y.copy()
        self.fitted = True
        logger.info("STL-ETS model fitted", extra={"period": self.period, "training_length": len(y)})
        return self
    
    def predict(self, horizon: int) -> pd.Series:
        """
        Generate predictions.
        
        Args:
            horizon: Number of periods to forecast
            
        Returns:
            Forecast series
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        if len(self.training_data) < self.period:
            raise ValueError(f"Training data must have at least {self.period} observations")
        
        # Simple seasonal decomposition + linear trend
        # This is a stub implementation
        seasonal_pattern = self._extract_seasonal_pattern()
        trend = self._extract_trend()
        
        # Generate forecasts
        forecasts = []
        for i in range(horizon):
            seasonal_idx = i % self.period
            trend_value = trend * (len(self.training_data) + i)
            forecast = seasonal_pattern[seasonal_idx] + trend_value
            forecasts.append(max(0, forecast))  # Ensure non-negative
        
        # Create forecast series with proper index
        last_date = self.training_data.index[-1]
        if hasattr(last_date, 'freq'):
            forecast_index = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq=last_date.freq)
        else:
            forecast_index = range(len(self.training_data), len(self.training_data) + horizon)
        
        forecast_series = pd.Series(forecasts, index=forecast_index)
        
        logger.info("STL-ETS forecast generated", extra={"horizon": horizon, "period": self.period})
        return forecast_series
    
    def fit_predict(self, y: pd.Series, horizon: int) -> pd.Series:
        """
        Fit the model and generate predictions.
        
        Args:
            y: Training time series
            horizon: Number of periods to forecast
            
        Returns:
            Forecast series
        """
        return self.fit(y).predict(horizon)
    
    def _extract_seasonal_pattern(self) -> np.ndarray:
        """Extract seasonal pattern from training data."""
        # Simple seasonal averaging
        seasonal_values = []
        for i in range(self.period):
            seasonal_values.append(self.training_data.iloc[i::self.period].mean())
        return np.array(seasonal_values)
    
    def _extract_trend(self) -> float:
        """Extract linear trend from training data."""
        # Simple linear trend
        x = np.arange(len(self.training_data))
        y = self.training_data.values
        trend = np.polyfit(x, y, 1)[0]
        return trend


def rolling_backtest(
    y: pd.Series,
    horizon: int,
    last_n_months: int,
    model_class: Type[STLETS],
    **model_kwargs
) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Run rolling backtest with frozen origin.
    
    Args:
        y: Time series data
        horizon: Forecast horizon
        last_n_months: Number of months to use for backtesting
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
        'horizon': horizon
    }
    
    logger.info("STL-ETS forecast generated", extra=model_info)
    return forecasts, model_info

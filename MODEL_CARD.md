# Fuel Tracker Model Card

## Model Information
- **Model Name**: Fuel Consumption Forecasting
- **Version**: 0.1.0
- **Last Updated**: 2025-08-26 16:39:05 UTC
- **Batch ID**: 9a2b5201-f6a4-4922-b916-67f5c74e0230

## Objective
Forecast monthly pipeline compressor fuel consumption in million cubic feet (MMcf) to support operational planning and resource allocation.

## Target Variable
- **Variable**: `value_mmcf`
- **Unit**: Million cubic feet (MMcf)
- **Frequency**: Monthly
- **Type**: Continuous, non-negative

## Data Sources
- **Primary**: EIA (Energy Information Administration) API v2
- **Metric**: Pipeline compressor fuel consumption
- **Coverage**: United States
- **Update Frequency**: Monthly (with provisional data handling)

## Lineage Rules
- **Data Freshness**: Cache TTL of 3 business days
- **Provisional Mode**: Blocks publishing when cache is stale or API fails
- **Batch Tracking**: Each data update creates a new batch with UUID and timestamp
- **Append-Only**: Panel data uses append-only revisions with lineage tracking

## Model Selection
- **Current Winner**: baseline
- **Selection Criteria**: [To be implemented]
- **Backtest Performance**: [Auto-updated]

## Forecast Details
## Latest Forecast Statistics
- **Model Used**: baseline
- **Forecast Horizon**: 12 months
- **Forecast Mean**: 77.04 MMcf
- **PI Half-Width**: 9.32 MMcf
- **Generated**: 2025-08-26 18:18:44 UTC

## Tolerance & Performance
- **Target MAE**: [To be defined]
- **Target sMAPE**: [To be defined]
- **Acceptable Range**: [To be defined]

## Backtest Protocol
- **Method**: Rolling backtest with frozen-origin style
- **Horizon**: 12 months (configurable)
- **Lookback**: 60 months (configurable)
- **Metrics**: MAE, sMAPE, RMSE, MAPE
- **Validation**: Time series cross-validation

## Success Criteria
- **Accuracy**: Forecasts within acceptable error bounds
- **Stability**: Consistent performance across backtest periods
- **Reliability**: Robust handling of data updates and model revisions

## Limitations
- **Seasonality**: Assumes stable seasonal patterns
- **Trend**: Linear trend assumption may not capture complex dynamics
- **Exogenous Variables**: Limited incorporation of external factors
- **Data Quality**: Dependent on EIA data availability and accuracy

## Revision Stability
- **Log Flips**: Model performance changes tracked through batch lineage
- **Version Control**: Each forecast run creates new batch with full traceability
- **Rollback Capability**: Previous forecasts preserved in lineage log
- **Impact Assessment**: Performance changes can be traced to specific data updates

## Technical Details
- **Framework**: Python with pandas, numpy
- **Storage**: Parquet format with PyArrow
- **Lineage**: JSONL logs with batch metadata
- **Configuration**: Environment-based with .env files

## Maintenance
- **Regular Updates**: Monthly with new EIA data
- **Performance Monitoring**: Continuous backtesting
- **Model Refresh**: Quarterly model selection updates
- **Documentation**: Living document updated with each forecast run

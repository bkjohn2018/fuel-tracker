# MODEL CARD — FIRE (Fuel Integrity & Reconciliation Engine)

## Model Information
- **Model Name**: Pipeline Compressor Fuel Consumption Forecasting
- **Version**: 0.1.0
- **Last Updated**: 2025-10-17 22:50:00 UTC
- **Batch ID**: ddcaa3e1-7e5c-4b9c-85ce-12f6bbaa33ea

## Objective
Forecast monthly US pipeline compressor fuel consumption in million cubic feet (MMcf) to support operational planning, resource allocation, and regulatory compliance for FERC Account 820 reporting.

## Target Variable
- **Variable**: `value_mmcf`
- **Unit**: Million cubic feet (MMcf)
- **Frequency**: Monthly (month-end dates)
- **Type**: Continuous, non-negative
- **FERC Account**: 820 (Pipeline Compressor Fuel)

## Data Sources
- **Primary**: EIA (Energy Information Administration) API v2
- **Endpoint**: `petroleum/pri/spt/data` (Pipeline compressor fuel consumption)
- **Coverage**: United States
- **Update Frequency**: Monthly (with provisional data handling)
- **Data Quality**: ±2% tolerance vs source snapshot

## Model Family
1. **Seasonal-Naïve Baseline**: Simple seasonal pattern replication
2. **STL+ETS**: Seasonal-Trend decomposition with Exponential Smoothing
3. **SARIMAX**: Seasonal ARIMA with eXogenous variables (HDD/CDD, Henry Hub)

## Features & Exogenous Variables
- **Heating Degree Days (HDD)**: Population-weighted heating degree days
- **Cooling Degree Days (CDD)**: Population-weighted cooling degree days
- **Henry Hub Natural Gas Price**: Monthly average spot price
- **Seasonality**: 12-month seasonal patterns
- **Trend**: Linear trend component

## Training & Backtest Protocol
- **Method**: Rolling-origin backtesting with frozen panels per data vintage
- **Horizon**: 12 months (configurable)
- **Lookback**: 60 months (configurable)
- **Window**: Rolling window approach
- **Metrics**: MAE, sMAPE, RMSE, MAPE
- **Validation**: Time series cross-validation
- **Success Criteria**: Beat Seasonal-Naïve by ≥10% median MAE/sMAPE

## Lineage & Reproducibility
- **Batch Tracking**: Each data update creates new batch with UUID and UTC timestamp
- **Append-Only**: Panel data uses append-only revisions with lineage tracking
- **No Overwrites**: Previous data vintages preserved for auditability
- **Frozen Panels**: Backtests use frozen panels per data vintage
- **State Idempotence**: Same source snapshot → same outputs; new snapshot → new batch_id

## Tolerance Rules & Data Integrity
- **Source Tolerance**: ±2% variance vs EIA source snapshot
- **Exception Handling**: Out-of-tolerance data flagged for review
- **Provisional Mode**: Blocks publishing when cache stale >3 business days
- **Cache TTL**: 3 business days maximum staleness
- **Data Freshness**: Real-time validation against source

## Stability Log & Escalation
- **Model Performance Tracking**: Rolling performance metrics across revisions
- **Stability Flags**: Alert when top model flips ≥N times across M revisions
- **Revision Logging**: Complete audit trail in JSONL format
- **Escalation Path**: Variance >2% triggers review process
- **Rollback Capability**: Previous forecasts preserved in lineage log

## Forecast Details
## Latest Forecast Statistics
- **Model Used**: baseline
- **Forecast Horizon**: 12 months
- **Forecast Mean**: 77.04 MMcf
- **PI Half-Width**: 9.32 MMcf
- **Generated**: 2025-10-17 22:50:00 UTC

- **Horizon**: 12 months
- **Frequency**: Monthly (month-end dates)
- **Prediction Intervals**: Naive bands using historical MAE
- **Last Forecast**: 2025-10-17 22:50:00 UTC
- **Confidence Level**: 95% (configurable)

## Compliance & Controls
### Lineage Philosophy: PTA vs. PPA

In accounting, Prior Period Adjustments (PPAs) are formal restatements of prior financial results to reflect new or corrected information under GAAP/FERC guidance.
In FIRE, the analogous concept for forecasting and reconciliation is the Point-in-Time Archive (PTA) - a complete analytical snapshot that captures all data and model context as they existed at a specific time.

- PPA (Accounting) → Ensures financial transparency and compliance for restatements.
- PTA (Analytics) → Ensures analytical reproducibility and lineage integrity across forecast vintages.

Each PTA carries a unique `batch_id` and `asof_ts`, forming a verifiable lineage chain that allows the system to reproduce any historical forecast or reconciliation exactly as it was run.

This deliberate terminology avoids confusion for accounting and audit audiences, reinforcing that FIRE's revision logic is analytical, not financial - designed to preserve the integrity of forecasts, not to restate results.
- **FERC Alignment**: Designed for Account 820 reporting requirements
- **ASC 980 Compliance**: Probable recovery assessment for fuel surcharge recognition
- **GAAP Compliance**: Audit trail supports financial reporting
- **Form 2/3-Q Bridge**: Monthly data supports quarterly reporting
- **Cross-Account Integration**: Supports Accounts 182.3/254 for under/over-recovery
- **Tie-out Process**: Monthly variance analysis with ±2% tolerance
- **Retention Policy**: 24 months full data; quarterly snapshots beyond
- **CPA Certification**: Audit-ready documentation for external review

## Limitations & Caveats
- **Seasonality Assumption**: Assumes stable seasonal patterns
- **Trend Assumption**: Linear trend may not capture complex dynamics
- **Exogenous Availability**: Dependent on HDD/CDD and Henry Hub data
- **Data Quality**: Dependent on EIA data availability and accuracy
- **Revision Impact**: Model performance may change with data updates
- **Provisional Mode**: May block publishing during data staleness

## Technical Details
- **Framework**: Python 3.11+ with pandas, numpy, statsmodels
- **Storage**: Parquet format with PyArrow for lineage columns
- **Lineage**: JSONL logs with batch metadata and timestamps
- **Configuration**: Environment-based with YAML config files
- **Validation**: Pydantic v2 schemas with field validators
- **Logging**: Structured logging with batch context

## Performance Monitoring
- **Regular Updates**: Monthly with new EIA data
- **Continuous Backtesting**: Rolling performance evaluation
- **Model Refresh**: Quarterly model selection updates
- **Stability Tracking**: Performance change detection
- **Alert System**: Automated escalation for anomalies

## Accounting Treatment (ASC 980 Alignment)

- **Account 820 – Pipeline Compressor Fuel Expense**
  Operating expense for consumed fuel.

- **Account 489 – Transportation Revenue (Fuel Retainage)**
  Revenue recognition for tariff-based retainage.

- **Account 182.3 – Regulatory Asset: Fuel Under-Recovery (ASC 980-340)**
  Incurred fuel costs deferred when recovery through rates is probable.
  Must be amortized over the recovery period. Write down if recovery is no longer probable.
  Carrying charges may reflect debt component of allowed cost of capital, but exclude equity return.

- **Account 254 – Regulatory Liability: Fuel Over-Recovery (ASC 980-405)**
  Probable future refunds or credits to customers recognized as liabilities.
  Released when refunded or netted in subsequent tariff cycles.

- **Disclosure Requirements:**
  - Basis for recognition of regulatory assets/liabilities.
  - Recovery period assumptions.
  - Rate order or regulatory precedent relied upon.

## Maintenance & Operations
- **Monthly Pipeline**: Automated data fetch and panel building
- **Quarterly Review**: Model performance and selection updates
- **Annual Audit**: Full system review and compliance check
- **CPA Certification**: External audit documentation and review
- **Documentation**: Living document updated with each forecast run
- **Version Control**: Git-based change tracking with semantic versioning

## Release Checklist
- [ ] Data fresh within 3 business days
- [ ] Tolerance within ±2% bounds
- [ ] CI/CD pipeline green
- [ ] Backtest metrics acceptable
- [ ] Model card updated
- [ ] Lineage log complete
- [ ] Provisional mode status normal
- [ ] All outputs generated successfully
- [ ] ASC 980 compliance review completed
- [ ] CPA audit documentation prepared
- [ ] Cross-account reconciliation verified
- [ ] Regulatory reporting data validated

## Contact & Support
- **Team**: FIRE Team
- **Repository**: [GitHub Repository URL]
- **Issues**: [GitHub Issues URL]
- **Documentation**: [Documentation URL]

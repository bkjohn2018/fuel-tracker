# Fuel Tracker Model Card

## Model Information
- **Model Name**: Pipeline Compressor Fuel Consumption Forecasting
- **Version**: 0.1.0
- **Last Updated**: [Auto-updated]
- **Batch ID**: [Auto-updated]

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
- **Horizon**: 12 months
- **Frequency**: Monthly (month-end dates)
- **Prediction Intervals**: Naive bands using historical MAE
- **Last Forecast**: [Auto-updated]
- **Confidence Level**: 95% (configurable)

## Compliance & Controls
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

## Accounting Treatment & ASC 980 Compliance

### FERC Account Structure
- **Account 820**: Pipeline Compressor Fuel Expense (primary forecast target)
- **Account 489**: Transportation Revenue - Fuel Retainage (surcharge collection)
- **Account 182.3**: Fuel Cost Under-Recovery (deferred regulatory asset)
- **Account 254**: Fuel Cost Over-Recovery (deferred regulatory liability)

### ASC 980 Requirements
- **Probable Recovery**: Forecasts support assessment of probable fuel cost recovery
- **Regulatory Asset Recognition**: Under-recovery amounts recognized as regulatory assets
- **Regulatory Liability Recognition**: Over-recovery amounts recognized as regulatory liabilities
- **Rate Case Support**: Historical data and forecasts support rate case filings
- **Variance Analysis**: Monthly reconciliation supports regulatory compliance

### Cross-Account Integration
- **Fuel Surcharge Calculation**: Forecasts drive fuel surcharge rate determination
- **Under/Over-Recovery Tracking**: Variance analysis feeds Accounts 182.3/254
- **Regulatory Reporting**: Data supports FERC Form 2/3-Q quarterly filings
- **Audit Trail**: Complete lineage supports external audit requirements

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
- **Team**: Fuel Tracker Team
- **Repository**: [GitHub Repository URL]
- **Issues**: [GitHub Issues URL]
- **Documentation**: [Documentation URL]

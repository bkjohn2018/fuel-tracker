# FIRE Ecosystem Brief — Fuel Integrity & Reconciliation Engine

Integrity at the speed of compression.

FIRE (Fuel Integrity & Reconciliation Engine) automates compressor‑fuel accounting and reconciliation from measurement to regulatory reporting. It preserves revision‑aware lineage, validates against source snapshots within ±2%, and logs revisions as new batches for an immutable audit trail.

- Analytics lens: CompressionSight (diagnostics & forecasting)
- Governance frame: The Compliance Curve (continuous assurance)

## FIRE
- Purpose: Reconciliation engine for compressor fuel (FERC 820) with point‑in‑time lineage and reproducibility.
- Lineage: Append‑only batches with `batch_id` and `asof_ts`; frozen backtests by data vintage.
- Controls: ±2% tolerance vs source; provisional mode for stale upstream; JSONL audit trail.

## CompressionSight (Analytics Lens)
- Diagnostics: Stability tracking, variance analysis, driver attribution.
- Forecasting: Baseline and advanced models (STL+ETS, SARIMAX) with exogenous features.
- Readouts: Metrics, prediction intervals, change summaries between vintages.

## The Compliance Curve (Governance Frame)
- Ownership: Clear roles for measurement, scheduling, accounting, and regulatory.
- KPIs: Data freshness, tolerance exceptions, stability flips, reproducibility checks.
- Escalation: Provisional runs blocked; >2% variance triggers review and traceable ticket.

Formerly: “Fuel Tracker” (no functional changes)

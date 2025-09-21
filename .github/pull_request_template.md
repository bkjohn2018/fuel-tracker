## Fuel Tracker — PR Review Checklist

### Compliance & Accounting
- [ ] README and MODEL_CARD reference FERC 820, 489, 182.3, 254 correctly
- [ ] ±2% variance rule documented (and escalation path noted)
- [ ] Provisional mode behavior (stale >3 business days) documented

### Data Contracts & Lineage
- [ ] Panel schema documented (incl. `batch_id`, `asof_ts`, exog cols)
- [ ] Idempotence defined (same snapshot ⇒ same outputs; new snapshot ⇒ new batch)
- [ ] Retention policy (24m full runs; quarterly archives beyond) included

### Modeling & Backtests
- [ ] Baseline + advanced models listed (Seasonal-Naïve, STL+ETS, SARIMAX+exog)
- [ ] Rolling-origin rules (last 60m) + success criterion (≥10% vs Seasonal-Naïve) stated
- [ ] Stability-flip logging described

### Quickstart & CLI
- [ ] Env & prerequisites accurate (`EIA_API_KEY`, Python version)
- [ ] Commands run as documented (build → backtest → forecast)
- [ ] Paths for outputs match (`panel_monthly.parquet`, `metrics.csv`, `forecast_12m.csv`)

### Ops & Governance
- [ ] Ops runbook covers stale upstream, >2% variance, failed checks
- [ ] Architecture diagram renders (Mermaid) on GitHub
- [ ] No code behavior changes (docs-only) unless explicitly stated

### Technical Quality
- [ ] Code follows project style guidelines (Ruff)
- [ ] Tests pass and coverage maintained
- [ ] No hardcoded secrets or credentials
- [ ] Documentation updated for any API changes

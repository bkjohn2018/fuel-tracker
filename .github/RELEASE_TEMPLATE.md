# Fuel Tracker – Release {{VERSION}} ({{DATE}})

## Summary
Production-lean, compliance-ready release focused on documentation, governance scaffolding, and audit traceability. No runtime behavior changes.

## Highlights
- ASC 980 alignment (scope criteria; 182.3/254 recognition; fuel tracker/true-up support)
- Lineage & reproducibility (batch_id, asof_ts; frozen backtests by data vintage)
- Ops runbook for ±2% variance and provisional mode
- Stakeholder-ready README, model card, architecture diagram

## Changes
- See [CHANGELOG.md](../CHANGELOG.md#v{{VERSION}}) for the complete list.

## Compliance & Controls
- **FERC/GAAP context:** Accounts 820, 489, 182.3, 254 documented
- **Tolerance:** ±2% vs source snapshot; escalation path included
- **Retention:** 24 months full runs; quarterly archive snapshots beyond
- **Lineage:** Append-only PPAs; idempotence within snapshot

## Verification
- `make lint` / `make test` pass
- `verify_setup.sh` confirms CLI help and artifacts presence
- Architecture Mermaid renders on GitHub

## Upgrade Notes
- No migrations or config changes required
- Reconfirm `EIA_API_KEY` in environment/secrets for CI

---
_Release prepared with Conventional Commits and Keep a Changelog._

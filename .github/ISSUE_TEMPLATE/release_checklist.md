---
name: Release Checklist
about: Pre-release verification for FIRE (Fuel Integrity & Reconciliation Engine)
title: "Release {{VERSION}} – Checklist"
labels: release
---

## Pre-Flight
- [ ] CHANGELOG updated for v{{VERSION}} with date
- [ ] README badges reflect current CI path
- [ ] Mermaid diagrams render (README/docs/architecture)
- [ ] `verify_setup.sh` passes locally and in CI

## Compliance
- [ ] ASC 980 section present & accurate (scope, 182.3/254, tracker/true-up)
- [ ] ±2% variance & provisional mode procedures present
- [ ] Model Card contains lineage/tolerance/stability log language
- [ ] Retention policy (24m + quarterly archives) documented

## Governance
- [ ] PR template in place; CODEOWNERS routes docs correctly
- [ ] Make targets present (lint/test/build/backtest/forecast)

## Tag & Publish
- [ ] Create tag `v{{VERSION}}`
- [ ] Publish GitHub Release using `.github/RELEASE_TEMPLATE.md`

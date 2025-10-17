# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.1.0] - 2025-09-21
### Added
- **Compliance documentation:** Explicit ASC 980 sections (scope criteria, 182.3/254 recognition, fuel tracker/true-up support, disclosure requirements).
- **Model governance:** `MODEL_CARD.md` with assumptions, lineage, tolerance rules, stability log, and release checklist.
- **Architecture documentation:** `docs/architecture.md` with Mermaid dataflow diagrams and compliance flow visualization.
- **Ops runbook snippets:** Variance analysis (±2% tolerance) and escalation procedures; provisional mode triggers for stale upstream data.
- **Stakeholder polish:** README badges, quick-reference journal entries for FERC accounts, PR review checklist, and CODEOWNERS file.
- **Tooling enhancements:** Makefile targets (`lint`, `test`, `build`, `backtest`, `forecast`); `verify_setup.sh` verification script.
- **GitHub templates:** PR template, issue templates for bugs and documentation updates, release checklist template.
- **Release management:** CHANGELOG.md, release template, and contributing guidelines.

### Changed
- README rewritten to production-lean, stakeholder-ready format (no code behavior changes).
- Documentation structure enhanced with compliance-focused sections and cross-functional team support.

### Security
- Documented credential handling for API keys and high-level guidance on audit trail retention.
- Added security considerations for FERC, SOX, and ASC 980 compliance requirements.

### Fixed
- Restored corrupted stl_ets.py with proper formatting.
- Resolved merge conflicts and formatting issues from repair/undo-minify branch integration.

### Technical
- Enhanced Makefile with quality-of-life targets and ASOF date parameter support.
- Added comprehensive verification script for post-merge sanity checks.
- Improved pre-commit hooks and CI/CD pipeline configuration.

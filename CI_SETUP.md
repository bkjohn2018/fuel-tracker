# Fuel Tracker CI/CD Setup Guide

## 🚀 Quick Start

### 1. Development Environment Setup

**Windows:**
```powershell
.\setup-dev.ps1
```

**Unix/Linux/macOS:**
```bash
./setup-dev.sh
```

This will install all development dependencies and set up pre-commit hooks.

### 2. Pre-commit Hooks

The project uses pre-commit hooks for:
- **detect-secrets**: Scans for potential secrets in code
- **ruff**: Fast Python linter and formatter

Hooks are automatically installed and run on every `git commit`.

### 3. Local Development

**Setup (one-time):**
```bash
# Windows
.\run.ps1 setup

# Unix/Linux/macOS
make setup
```

**Regular workflow:**
```bash
# Windows
.\run.ps1 pull      # Pull data from EIA API
.\run.ps1 backtest  # Run backtests
.\run.ps1 forecast  # Generate forecasts

# Unix/Linux/macOS
make pull      # Pull data from EIA API
make backtest  # Run backtests
make forecast  # Generate forecasts
```

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow

The CI pipeline runs on:
- **Push to main/develop**: Full pipeline including data operations
- **Pull requests**: Linting and testing only (no secrets)

### Jobs

#### 1. `lint-and-test` (All events)
- **Python 3.11** on Ubuntu
- **Linting**: `ruff check .`
- **Testing**: `pytest -q`
- **No secrets required**

#### 2. `pipeline` (Main branch pushes only)
- **Dependencies**: `lint-and-test` must pass first
- **Data operations**: Pull → Backtest → Forecast
- **Secrets**: `EIA_API_KEY` scoped to data pull step only
- **Artifacts**: Uploads outputs (7-day retention)

### Security Features

- **Step-scoped secrets**: `EIA_API_KEY` only available during `make pull`
- **Secret masking**: API key is masked in logs
- **Conditional execution**: Pipeline only runs on main branch pushes
- **Artifact retention**: 7-day limit on sensitive outputs

## 🛡️ Security Hardening

### Current (Phase 1)
- Repository-level `EIA_API_KEY` secret
- Step-scoped secret usage in CI
- Pre-commit hooks for secret detection
- Local `.env` files (gitignored)

### Future (Phase 2+)
See `SECURITY_HARDENING.md` for upgrade path including:
- OIDC + Cloud Secret Manager
- GitHub Environments with approvals
- Action hardening and CODEOWNERS
- Operational hygiene practices

## 📋 Configuration Files

### `.github/workflows/ci.yml`
- CI/CD pipeline definition
- Two jobs: lint-and-test, pipeline
- Conditional execution based on branch/event

### `.pre-commit-config.yaml`
- Pre-commit hook configuration
- detect-secrets and ruff integration

### `pyproject.toml`
- Project configuration
- Ruff linting rules
- Pytest settings

### `.gitignore`
- Excludes sensitive files
- Development artifacts
- Build outputs

## 🧪 Testing

### Running Tests Locally
```bash
pytest                    # Run all tests
pytest tests/            # Run specific test directory
pytest -v               # Verbose output
pytest -k "test_name"   # Run specific test
```

### Test Structure
```
tests/
├── __init__.py
├── test_eia_client_smoke.py    # EIA client tests
└── test_contracts_lineage.py   # Data contract tests
```

## 🔍 Linting and Formatting

### Ruff Configuration
- **Target**: Python 3.11+
- **Line length**: 88 characters
- **Rules**: E, W, F, I, B, C4, UP (see pyproject.toml)

### Running Linters
```bash
ruff check .           # Check for issues
ruff format .          # Format code
pre-commit run --all-files  # Run all pre-commit hooks
```

## 🚨 Troubleshooting

### Common Issues

**Pre-commit hooks failing:**
```bash
pre-commit run --all-files  # Run manually to see errors
pre-commit clean            # Clean up hook state
```

**CI pipeline failing:**
- Check that `EIA_API_KEY` secret is set in repository
- Verify branch protection rules
- Check workflow permissions

**Local setup issues:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install pre-commit detect-secrets ruff
```

### Getting Help

1. Check GitHub Actions logs for detailed error messages
2. Verify all required secrets are configured
3. Ensure development environment matches CI (Python 3.11)
4. Check pre-commit hook output for local issues

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Framework](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Detect Secrets](https://github.com/Yelp/detect-secrets)
- [Pytest Documentation](https://docs.pytest.org/)

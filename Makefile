# Fuel Tracker Makefile
# Quick run order for common operations

.PHONY: help setup pull backtest forecast clean lint test build status

SHELL := bash
.SHELLFLAGS := -euo pipefail -c

# Default target
help:
	@echo "Fuel Tracker - Quick Run Commands"
	@echo ""
	@echo "Commands:"
	@echo "  setup     - Install dependencies and setup environment"
	@echo "  lint      - Run Ruff linting and formatting checks"
	@echo "  test      - Run pytest test suite"
	@echo "  build     - Pull data from EIA API and build panel (with ASOF date)"
	@echo "  pull      - Pull data from EIA API and build panel"
	@echo "  backtest  - Run baseline backtest on last 60 months (with ASOF date)"
	@echo "  forecast  - Generate forecast using winning model (with ASOF date)"
	@echo "  clean     - Clean up generated files and caches"
	@echo ""
	@echo "Quick run order:"
	@echo "  make setup     # once"
	@echo "  make pull      # data pull + panel (writes append-only parquet + lineage log)"
	@echo "  make backtest  # baseline backtest on last 60 months (writes metrics.csv)"
	@echo "  make forecast  # stubbed forecast (writes forecast_12m.csv)"

# Install dependencies and setup environment
setup:
	@echo "Setting up Fuel Tracker environment..."
	pip install -r requirements.txt
	@echo "Setup complete!"

# Run Ruff linting and formatting checks
lint:
	@echo "Running Ruff linting and formatting checks..."
	ruff check . && ruff format --check .
	@echo "Linting complete!"

# Run pytest test suite
test:
	@echo "Running pytest test suite..."
	pytest -q
	@echo "Tests complete!"

# Pull data from EIA API and build panel (with ASOF date)
build:
	@echo "Pulling data from EIA API and building panel..."
	python -m fueltracker.pipeline.fetch_and_build --asof $(ASOF)
	@echo "Data pull complete!"

# Pull data from EIA API and build panel
pull:
	@echo "==> fueltracker pull (mode=$${FT_MODE:-publish})"
	python -m fueltracker.cli pull --mode "$$${FT_MODE:-publish}"

# Run baseline backtest on last 60 months (with ASOF date)
backtest:
	@echo "==> fueltracker backtest (mode=$${FT_MODE:-publish})"
	python -m fueltracker.cli backtest --mode "$$${FT_MODE:-publish}"

# Generate forecast using winning model (with ASOF date)
forecast:
	@echo "==> fueltracker forecast (mode=$${FT_MODE:-publish})"
	python -m fueltracker.cli forecast --mode "$$${FT_MODE:-publish}"

# Snapshot utilities
.PHONY: snapshot-show snapshot-seed snapshot-clear

snapshot-show:
	@ls -lh snapshots || true

snapshot-seed:
	@test -n "$(SRC)" || (echo "Usage: make snapshot-seed SRC=path/to/panel.parquet" && exit 1)
	mkdir -p snapshots
cp -f "$(SRC)" snapshots/panel_monthly_prev.parquet
	@echo "Seeded snapshot from $(SRC)"

snapshot-clear:
	rm -f snapshots/panel_monthly_prev.parquet
	@echo "Snapshot cleared"

# Clean up generated files and caches
clean:
	@echo "Cleaning up generated files and caches..."
	rm -rf data/cache/*
	rm -rf outputs/*
	rm -f MODEL_CARD.md
	@echo "Cleanup complete!"

# Show current status
status:
	@echo "Fuel Tracker Status:"
	@echo ""
	@echo "Files:"
	@ls -la outputs/ 2>/dev/null || echo "  No outputs directory"
	@echo ""
	@echo "Panel info:"
	@python -c "from fueltracker.io_parquet import get_panel_info; print(get_panel_info())" 2>/dev/null || echo "  No panel data"
	@echo ""
	@echo "Metrics:"
	@wc -l outputs/metrics.csv 2>/dev/null || echo "  No metrics file"
	@echo ""
	@echo "Forecast:"
	@wc -l outputs/forecast_12m.csv 2>/dev/null || echo "  No forecast file"

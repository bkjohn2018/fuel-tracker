# Fuel Tracker Makefile
# Quick run order for common operations

.PHONY: help setup pull backtest forecast clean

# Default target
help:
	@echo "Fuel Tracker - Quick Run Commands"
	@echo ""
	@echo "Commands:"
	@echo "  setup     - Install dependencies and setup environment"
	@echo "  pull      - Pull data from EIA API and build panel"
	@echo "  backtest  - Run baseline backtest on last 60 months"
	@echo "  forecast  - Generate forecast using winning model"
	@echo "  clean     - Clean up generated files and caches"
	@echo ""
	@echo "Quick run order:"
	@echo "  make setup     # once"
	@echo "  make pull      # data pull → panel (writes append-only parquet + lineage log)"
	@echo "  make backtest  # baseline backtest on last 60 months (writes metrics.csv)"
	@echo "  make forecast  # stubbed forecast (writes forecast_12m.csv)"

# Install dependencies and setup environment
setup:
	@echo "🔧 Setting up Fuel Tracker environment..."
	pip install -r requirements.txt
	@echo "✅ Setup complete!"

# Pull data from EIA API and build panel
pull:
	@echo "📥 Pulling data from EIA API and building panel..."
	python -m fueltracker.pipeline.fetch_and_build
	@echo "✅ Data pull complete!"

# Run baseline backtest on last 60 months
backtest:
	@echo "🧪 Running baseline backtest on last 60 months..."
	python -m fueltracker.backtest --model baseline --last-n-months 60
	@echo "✅ Backtest complete!"

# Generate forecast using winning model
forecast:
	@echo "🔮 Generating forecast using winning model..."
	python -m fueltracker.forecast
	@echo "✅ Forecast complete!"

# Clean up generated files and caches
clean:
	@echo "🧹 Cleaning up generated files and caches..."
	rm -rf data/cache/*
	rm -rf outputs/*
	rm -f MODEL_CARD.md
	@echo "✅ Cleanup complete!"

# Show current status
status:
	@echo "📊 Fuel Tracker Status:"
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

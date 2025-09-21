#!/bin/bash
# Fuel Tracker - Quick Verification Script
# Sanity check after merges and deployments

echo "🔍 Fuel Tracker Verification Script"
echo "=================================="
echo ""

# Check CLI help text
echo "📋 Checking CLI help text..."
echo ""

echo "Pipeline fetch_and_build:"
python -m fueltracker.pipeline.fetch_and_build --help | head -5
echo ""

echo "Backtest:"
python -m fueltracker.run_backtest --help | head -5
echo ""

echo "Forecast:"
python -m fueltracker.forecast --help | head -5
echo ""

# Check output files
echo "📁 Checking output files..."
echo ""

if [ -f "outputs/panel_monthly.parquet" ]; then
    echo "✅ panel_monthly.parquet exists"
    # Get basic info about the file
    python -c "
import pandas as pd
try:
    df = pd.read_parquet('outputs/panel_monthly.parquet')
    print(f'   Rows: {len(df)}')
    print(f'   Columns: {list(df.columns)}')
    if 'period' in df.columns:
        print(f'   Date range: {df[\"period\"].min()} to {df[\"period\"].max()}')
except Exception as e:
    print(f'   Error reading file: {e}')
"
else
    echo "❌ panel_monthly.parquet missing"
fi

if [ -f "outputs/metrics.csv" ]; then
    echo "✅ metrics.csv exists"
    wc -l outputs/metrics.csv
else
    echo "❌ metrics.csv missing"
fi

if [ -f "outputs/forecast_12m.csv" ]; then
    echo "✅ forecast_12m.csv exists"
    wc -l outputs/forecast_12m.csv
else
    echo "❌ forecast_12m.csv missing"
fi

echo ""

# Check documentation files
echo "📚 Checking documentation files..."
echo ""

if [ -f "README.md" ]; then
    echo "✅ README.md exists"
    wc -l README.md
else
    echo "❌ README.md missing"
fi

if [ -f "MODEL_CARD.md" ]; then
    echo "✅ MODEL_CARD.md exists"
    wc -l MODEL_CARD.md
else
    echo "❌ MODEL_CARD.md missing"
fi

if [ -f "docs/architecture.md" ]; then
    echo "✅ docs/architecture.md exists"
    wc -l docs/architecture.md
else
    echo "❌ docs/architecture.md missing"
fi

echo ""

# Check GitHub templates
echo "🔧 Checking GitHub templates..."
echo ""

if [ -f ".github/pull_request_template.md" ]; then
    echo "✅ PR template exists"
else
    echo "❌ PR template missing"
fi

if [ -f ".github/CODEOWNERS" ]; then
    echo "✅ CODEOWNERS exists"
else
    echo "❌ CODEOWNERS missing"
fi

echo ""

# Check environment
echo "🌍 Checking environment..."
echo ""

if [ -n "$EIA_API_KEY" ]; then
    echo "✅ EIA_API_KEY is set"
else
    echo "⚠️  EIA_API_KEY not set (required for data operations)"
fi

python_version=$(python --version 2>&1)
echo "Python version: $python_version"

echo ""
echo "🎉 Verification complete!"
echo ""
echo "Next steps:"
echo "1. Set EIA_API_KEY if not already set"
echo "2. Run 'make pull' to fetch data"
echo "3. Run 'make backtest' to test models"
echo "4. Run 'make forecast' to generate predictions"

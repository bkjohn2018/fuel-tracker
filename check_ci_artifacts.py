#!/usr/bin/env python3
"""CI Artifacts Integrity Check Script
Run this after downloading artifacts from GitHub Actions"""

from pathlib import Path
import sys

import pandas as pd


def test_panel(artifacts_path="artifacts"):
    """Test panel data integrity"""
    print("==> Testing Panel Integrity...")
    panel_path = Path(artifacts_path) / "outputs" / "panel_monthly.parquet"

    if not panel_path.exists():
        print(f"❌ Panel missing: {panel_path}")
        return False

    try:
        df = pd.read_parquet(panel_path)
        need = {"period", "value_mmcf", "metric", "freq", "batch_id", "asof_ts"}
        missing = need - set(df.columns)
        assert not missing, f"missing columns: {missing}"

        # Handle datetime conversion
        if df["period"].dtype == 'object':
            df["period"] = pd.to_datetime(df["period"])

        assert df["period"].dt.is_month_end.all(), "not all month-end"
        assert df["metric"].eq("pipeline_compressor_fuel").all(), "metric mismatch"
        assert df["freq"].eq("monthly").all(), "freq mismatch"
        assert df["value_mmcf"].ge(0).all(), "negative values in value_mmcf"

        print(
            f"✅ Panel sanity OK: {len(df)} rows, "
            f"period range: {df['period'].min()} to {df['period'].max()}"
        )
        return True
    except Exception as e:
        print(f"❌ Panel test failed: {e}")
        return False


def test_metrics(artifacts_path="artifacts"):
    """Test metrics data integrity"""
    print("==> Testing Metrics Integrity...")
    metrics_path = Path(artifacts_path) / "outputs" / "metrics.csv"

    if not metrics_path.exists():
        print(f"❌ Metrics missing: {metrics_path}")
        return False

    try:
        df = pd.read_csv(metrics_path)
        cols = set(df.columns)
        assert "model" in cols, "model column missing"
        assert ({"metric", "value"} <= cols) or (
            {"metric_name", "metric_value"} <= cols
        ), "metric columns missing"
        assert (df["model"] == "seasonal_naive").any(), "baseline missing"

        print(
            f"✅ Metrics sanity OK: {len(df)} rows, "
            f"has baseline: {(df['model'] == 'seasonal_naive').any()}"
        )
        return True
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False


def test_forecast(artifacts_path="artifacts"):
    """Test forecast data integrity"""
    print("==> Testing Forecast Integrity...")
    forecast_path = Path(artifacts_path) / "outputs" / "forecast_12m.csv"

    if not forecast_path.exists():
        print(f"❌ Forecast missing: {forecast_path}")
        return False

    try:
        df = pd.read_csv(forecast_path, parse_dates=["period"])
        assert len(df) == 12, f"Expected 12 rows, got {len(df)}"
        assert df["forecast"].notna().all(), "NaNs in forecast"

        if {"pi_lo", "pi_hi"} <= set(df.columns):
            assert (df["pi_lo"] <= df["pi_hi"]).all(), "PI bounds inverted"

        print(
            f"✅ Forecast sanity OK: {len(df)} rows, "
            f"future months: {(df['period'] > pd.Timestamp.now()).all()}"
        )
        return True
    except Exception as e:
        print(f"❌ Forecast test failed: {e}")
        return False


def main():
    """Main execution"""
    print("🔍 CI Artifacts Integrity Check")

    # Get artifacts path from command line or use default
    artifacts_path = sys.argv[1] if len(sys.argv) > 1 else "artifacts"
    print(f"Artifacts path: {artifacts_path}")
    print()

    results = []
    results.append(test_panel(artifacts_path))
    results.append(test_metrics(artifacts_path))
    results.append(test_forecast(artifacts_path))

    print()
    if False in results:
        print("❌ Some integrity checks failed!")
        sys.exit(1)
    else:
        print("🎉 All CI artifacts integrity checks passed!")


if __name__ == "__main__":
    main()

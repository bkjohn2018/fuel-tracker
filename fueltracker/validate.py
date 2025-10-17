"""Validation helpers for panel data.

Provides schema, staleness, and optional tolerance checks.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from dateutil.relativedelta import relativedelta
import pandas as pd


def _as_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_period(s: str) -> datetime:
    """Parse period strings like YYYY-MM or YYYY-MM-DD to a datetime.

    Normalizes YYYY-MM to month start.
    """
    if len(s) == 7:
        return datetime.fromisoformat(s + "-01")
    return datetime.fromisoformat(s[:10])


def validate_panel_schema(panel: pd.DataFrame) -> List[str]:
    issues: List[str] = []
    expected = {"period", "value"}
    missing = expected.difference(panel.columns)
    if missing:
        issues.append(f"schema: missing columns {sorted(missing)}")
    if panel.empty:
        issues.append("schema: panel is empty")
    if "period" in panel.columns and panel["period"].duplicated().any():
        issues.append("schema: duplicate periods present")
    return issues


def validate_staleness(panel: pd.DataFrame, max_business_days: int = 3) -> List[str]:
    if "period" not in panel.columns or panel.empty:
        return []

    if isinstance(panel.index, pd.RangeIndex):
        last_period = panel["period"].iloc[-1]
    else:
        last_period = panel.sort_values("period")["period"].iloc[-1]

    dt = _parse_period(str(last_period))
    today = _as_utc_now().date()
    # Month end for the parsed date
    month_end = (dt + relativedelta(months=1) - relativedelta(days=dt.day)).date()
    days_diff = (today - month_end).days

    if days_diff <= 0:
        return []

    # Simple business-day approximation (Mon-Fri only)
    biz_days = sum(
        1
        for d in range(days_diff + 1)
        if (month_end + relativedelta(days=d)).weekday() < 5
    )
    return (
        [f"staleness: {biz_days} business days past month-end (> {max_business_days})"]
        if biz_days > max_business_days
        else []
    )


def validate_tolerance_vs_snapshot(
    panel: pd.DataFrame, snapshot: Optional[pd.DataFrame], pct: float = 0.02
) -> List[str]:
    """Optional +/- pct tolerance check vs prior snapshot on overlapping periods."""
    if snapshot is None:
        return []

    if not {"period", "value"}.issubset(snapshot.columns):
        return ["tolerance: snapshot missing period/value"]

    merged = panel[["period", "value"]].merge(
        snapshot[["period", "value"]].rename(columns={"value": "snap_value"}),
        on="period",
        how="inner",
    )
    if merged.empty:
        return []

    merged["pct_diff"] = (merged["value"] - merged["snap_value"]).abs() / merged[
        "snap_value"
    ].replace(0, pd.NA)
    breaches = merged.loc[merged["pct_diff"] > pct, ["period", "pct_diff"]]
    if not breaches.empty:
        rows = ", ".join(
            f"{r.period}={r.pct_diff:.1%}" for r in breaches.itertuples(index=False)
        )
        return [f"tolerance: +/-{int(pct * 100)}% breached on {rows}"]
    return []


def validate_panel(
    panel: pd.DataFrame, snapshot: Optional[pd.DataFrame] = None
) -> List[str]:
    issues: List[str] = []
    issues += validate_panel_schema(panel)
    issues += validate_staleness(panel, max_business_days=3)
    issues += validate_tolerance_vs_snapshot(panel, snapshot, pct=0.02)
    return issues

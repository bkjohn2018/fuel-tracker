from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List

LOG_DIR = Path("logs")
OUT_DIR = Path("outputs")
LOG_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)


# Exit codes
EXIT_OK = 0
EXIT_HARD_VALIDATION_FAIL = 2
EXIT_API_FAIL = 3
EXIT_SCHEMA_FAIL = 4


class ValidationWarning(Exception): ...


class ApiFailure(Exception): ...


class SchemaError(Exception): ...


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_status(
    status: str,
    reasons: List[str] | None = None,
    extra: Dict[str, Any] | None = None,
) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    payload: Dict[str, Any] = {
        "schema_version": 1,
        "status": status,
        "reasons": reasons or [],
        "mode": os.getenv("FT_MODE", "publish"),
        "asof_ts": _utcnow(),
    }
    if extra:
        payload.update(extra)
    (OUT_DIR / "status.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


def run_pull(mode: str) -> None:
    import pandas as pd

    from fueltracker.config import OUTPUTS_DIR, PANEL_FILE
    from fueltracker.io_parquet import read_panel
    from fueltracker.pipeline.fetch_and_build import fetch_and_build_panel
    from fueltracker.validate import validate_panel

    results = fetch_and_build_panel(dry_run=False)
    # Block publish if result is provisional
    if mode == "publish" and bool(results.get("provisional", False)):
        raise ValidationWarning("provisional data — publish blocked")
    if "error" in results:
        # Soft in CI mode
        if mode == "ci":
            write_status(
                "needs_review",
                [results.get("error", "unknown")],
                extra={
                    "provisional": bool(results.get("provisional", False)),
                },
            )
            return
        raise ValidationWarning(results.get("error", "unknown"))

    # Validate produced panel
    panel_path = OUTPUTS_DIR / PANEL_FILE
    panel_df = read_panel(panel_path)
    # Try to load previous published snapshot for tolerance comparison
    SNAP_DIR = Path("snapshots")
    SNAP_DIR.mkdir(exist_ok=True)
    snap_path = SNAP_DIR / "panel_monthly_prev.parquet"
    snapshot = None
    snapshot_issue = []
    if snap_path.exists():
        try:
            snapshot = pd.read_parquet(snap_path)
        except Exception as e:  # noqa: BLE001
            snapshot_issue = [f"snapshot: failed to load previous panel ({e})"]
    issues = snapshot_issue + validate_panel(panel_df, snapshot)

    if issues:
        if mode == "ci":
            write_status(
                "needs_review",
                issues,
                extra={
                    "provisional": bool(results.get("provisional", False)),
                },
            )
            return
        raise ValidationWarning("; ".join(issues))

    write_status(
        "ok",
        extra={
            "provisional": bool(results.get("provisional", False)),
        },
    )

    # Update snapshot only after successful publish runs
    if mode == "publish":
        try:
            panel_df.to_parquet(snap_path)
        except Exception:
            # Non-fatal: snapshot is best-effort and should not break runs
            pass


def run_backtest(mode: str, model: str = "baseline", horizon: int = 12) -> None:
    from fueltracker.backtest import run_backtest_pipeline

    try:
        results = run_backtest_pipeline(model=model, horizon=horizon)
    except Exception as e:  # noqa: BLE001 - map to API fail for CI summary
        if mode == "ci":
            write_status("api_failed", [str(e)])
            return
        raise ApiFailure(str(e)) from e

    if "error" in results:
        if mode == "ci":
            write_status("needs_review", [results.get("error", "unknown")])
            return
        raise ValidationWarning(results.get("error", "unknown"))

    write_status("ok")


def run_forecast(mode: str, model: str = "baseline", horizon: int = 12) -> None:
    from fueltracker.forecast import run_forecast_pipeline

    try:
        results = run_forecast_pipeline(model=model, horizon=horizon)
    except Exception as e:  # noqa: BLE001
        if mode == "ci":
            write_status("api_failed", [str(e)])
            return
        raise ApiFailure(str(e)) from e

    if "error" in results:
        if mode == "ci":
            write_status("needs_review", [results.get("error", "unknown")])
            return
        raise ValidationWarning(results.get("error", "unknown"))

    write_status("ok")


def main() -> int:
    parser = argparse.ArgumentParser(prog="fueltracker")
    sub = parser.add_subparsers(dest="cmd", required=True)
    # pull
    s_pull = sub.add_parser("pull")
    s_pull.add_argument(
        "--mode",
        choices=["ci", "publish"],
        default=os.getenv("FT_MODE", "publish"),
    )
    # backtest
    s_bt = sub.add_parser("backtest")
    s_bt.add_argument(
        "--mode",
        choices=["ci", "publish"],
        default=os.getenv("FT_MODE", "publish"),
    )
    s_bt.add_argument(
        "--model",
        choices=["baseline", "stl_ets", "sarimax"],
        default="baseline",
    )
    s_bt.add_argument("--horizon", type=int, default=12)
    # forecast
    s_fc = sub.add_parser("forecast")
    s_fc.add_argument(
        "--mode",
        choices=["ci", "publish"],
        default=os.getenv("FT_MODE", "publish"),
    )
    s_fc.add_argument(
        "--model",
        choices=["baseline", "stl_ets", "sarimax"],
        default="baseline",
    )
    s_fc.add_argument("--horizon", type=int, default=12)

    args = parser.parse_args()

    try:
        if args.cmd == "pull":
            run_pull(args.mode)
        elif args.cmd == "backtest":
            run_backtest(args.mode, args.model, args.horizon)
        elif args.cmd == "forecast":
            run_forecast(args.mode, args.model, args.horizon)
        return EXIT_OK
    except ValidationWarning as w:
        if args.mode == "ci":
            write_status("needs_review", [str(w)])
            return EXIT_OK
        write_status("failed_validation", [str(w)])
        return EXIT_HARD_VALIDATION_FAIL
    except ApiFailure as e:
        write_status("api_failed", [str(e)])
        return EXIT_API_FAIL
    except SchemaError as e:
        write_status("schema_failed", [str(e)])
        return EXIT_SCHEMA_FAIL


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # last-resort guard for CI visibility
        try:
            OUT_DIR.mkdir(exist_ok=True)
            (OUT_DIR / "status.json").write_text(
                json.dumps(
                    {
                        "status": "unhandled_exception",
                        "reasons": [str(e)],
                        "mode": os.getenv("FT_MODE", "publish"),
                        "asof_ts": _utcnow(),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:
            pass
        if os.getenv("FT_MODE") == "ci":
            sys.exit(0)
        sys.exit(EXIT_SCHEMA_FAIL)

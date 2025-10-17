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
    from fueltracker.config import OUTPUTS_DIR, PANEL_FILE
    from fueltracker.io_parquet import read_panel
    from fueltracker.pipeline.fetch_and_build import fetch_and_build_panel
    from fueltracker.validate import validate_panel

    results = fetch_and_build_panel(dry_run=False)
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
    snapshot = None  # Load a prior snapshot here if available
    issues = validate_panel(panel_df, snapshot)

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


def run_backtest(mode: str) -> None:
    from fueltracker.backtest import run_backtest_pipeline

    try:
        results = run_backtest_pipeline()
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


def run_forecast(mode: str) -> None:
    from fueltracker.forecast import run_forecast_pipeline

    try:
        results = run_forecast_pipeline()
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
    for name in ("pull", "backtest", "forecast"):
        s = sub.add_parser(name)
        s.add_argument(
            "--mode",
            choices=["ci", "publish"],
            default=os.getenv("FT_MODE", "publish"),
        )

    args = parser.parse_args()

    try:
        if args.cmd == "pull":
            run_pull(args.mode)
        elif args.cmd == "backtest":
            run_backtest(args.mode)
        elif args.cmd == "forecast":
            run_forecast(args.mode)
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
    sys.exit(main())

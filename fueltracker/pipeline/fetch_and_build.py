"""
Pipeline for fetching EIA data and building monthly panel.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List

from ..config import OUTPUTS_DIR, PANEL_FILE
from ..eia_client import EIAClient
from ..io_parquet import append_revision, read_panel, write_lineage_log
from ..lineage import start_batch
from ..logging_utils import get_logger
from ..panel import build_monthly_panel, get_panel_summary

logger = get_logger(__name__)

# Lineage log file
LINEAGE_LOG_FILE = OUTPUTS_DIR / "lineage_log.jsonl"


def _get_mode() -> str:
    """Return execution mode: 'ci' or 'publish' (default)."""
    mode = os.getenv("FT_MODE", "publish").lower()
    return mode if mode in {"ci", "publish"} else "publish"


def _write_status(status: Dict[str, Any]) -> None:
    from ..config import OUTPUTS_DIR

    OUTPUTS_DIR.mkdir(exist_ok=True)
    status_path = OUTPUTS_DIR / "status.json"
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


def _write_notice(provisional: bool, reasons: List[str]) -> None:
    from ..config import OUTPUTS_DIR

    if not provisional:
        return
    notice = (
        "This run used SAMPLE DATA due to missing/failed EIA API calls.\n"
        "Artifacts are provisional and not for publish.\n"
        f"Reasons: {', '.join(reasons)}\n"
    )
    with open(OUTPUTS_DIR / "FORECAST_NOTICE.txt", "w", encoding="utf-8") as f:
        f.write(notice)


def _write_run_meta(
    batch_id: str, asof_ts: str, provisional: bool, reasons: List[str]
) -> None:
    from ..config import OUTPUTS_DIR

    meta = {
        "batch_id": batch_id,
        "asof_ts": asof_ts,
        "ci": _get_mode() == "ci",
        "provisional": provisional,
        "reasons": reasons,
    }
    with open(OUTPUTS_DIR / "run_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def fetch_and_build_panel(dry_run: bool = False) -> Dict[str, Any]:
    """
    Main pipeline: fetch EIA data and build monthly panel.

    Args:
        dry_run: If True, only print counts without writing files

    Returns:
        Dictionary with pipeline results
    """
    logger.info("Starting fetch and build pipeline", extra={"dry_run": dry_run})

    try:
        # Start batch
        batch = start_batch(source="EIA", notes="Monthly fuel data pipeline")
        logger.info("Batch started", extra={"batch_id": str(batch.batch_id)})

        # Initialize EIA client
        from ..config import EIA_API_KEY

        if not EIA_API_KEY:
            raise ValueError("EIA_API_KEY not found in environment")

        fallback_env = os.getenv("FUELTRACKER_ALLOW_SAMPLE_DATA")
        if fallback_env is None:
            allow_sample_fallback = os.getenv("CI", "").lower() == "true"
        else:
            allow_sample_fallback = fallback_env.lower() in {"1", "true", "yes", "on"}

        if allow_sample_fallback:
            logger.info(
                "Sample data fallback enabled",
                extra={
                    "allow_sample_fallback": allow_sample_fallback,
                    "ci_env": os.getenv("CI"),
                },
            )

        client = EIAClient(
            EIA_API_KEY,
            allow_sample_fallback=allow_sample_fallback,
        )

        # Fetch data from EIA API
        logger.info(
            "Fetching data from EIA API",
            extra={
                "endpoint": "petroleum/pri/spt/data",
                "params": {
                    "frequency": "monthly",
                    "data[]": "value",
                    "facets[product][]": "EPD0",
                    "sort[0][column]": "period",
                    "sort[0][direction]": "desc",
                    "offset": 0,
                    "length": 5000,
                },
            },
        )
        raw_df = client.fetch_series(
            endpoint="petroleum/pri/spt/data",
            params={
                "frequency": "monthly",
                "data[]": "value",
                "facets[product][]": "EPD0",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": 0,
                "length": 5000,
            },
        )

        if raw_df.empty:
            logger.error(
                "No data fetched from EIA API after applying fallbacks",
                extra={
                    "endpoint": "petroleum/pri/spt/data",
                    "allow_sample_fallback": allow_sample_fallback,
                    "ci_env": os.getenv("CI"),
                },
            )
            return {
                "error": "No data fetched",
                "batch_id": str(batch.batch_id),
                "provisional": False,
                "reasons": ["empty_eia_response"],
            }

        logger.info(
            "Data fetched from EIA API",
            extra={"raw_rows": len(raw_df), "raw_columns": list(raw_df.columns)},
        )

        # Build monthly panel
        panel_df = build_monthly_panel(raw_df, batch)

        if panel_df.empty:
            logger.warning("Panel building resulted in empty DataFrame")
            return {"error": "Empty panel", "batch_id": str(batch.batch_id)}

        # Get panel summary
        panel_summary = get_panel_summary(panel_df)

        # Read existing panel for comparison
        panel_path = OUTPUTS_DIR / PANEL_FILE
        existing_df = read_panel(panel_path)

        # Calculate what would be added
        if not existing_df.empty:
            # Find new periods
            existing_periods = set(existing_df['period'])
            new_periods = set(panel_df['period']) - existing_periods
            rows_to_add = len(panel_df[panel_df['period'].isin(new_periods)])
        else:
            rows_to_add = len(panel_df)

        # Pipeline results
        results = {
            "batch_id": str(batch.batch_id),
            "asof_ts": batch.asof_ts.isoformat(),
            "raw_rows": len(raw_df),
            "panel_rows": len(panel_df),
            "existing_rows": len(existing_df),
            "rows_to_add": rows_to_add,
            "date_range": panel_summary.get("date_range", {}),
            "dry_run": dry_run,
            "provisional": getattr(client, "used_sample_fallback", False),
            "reasons": (
                ["sample_fallback"]
                if getattr(client, "used_sample_fallback", False)
                else []
            ),
        }

        logger.info("Pipeline completed successfully", extra=results)

        if not dry_run:
            # Write panel
            append_revision(panel_df, panel_path)

            # Write lineage log
            start_date = panel_df['period'].min().isoformat()
            end_date = panel_df['period'].max().isoformat()
            write_lineage_log(
                batch=batch,
                rows_added=rows_to_add,
                start_date=start_date,
                end_date=end_date,
                log_path=LINEAGE_LOG_FILE,
            )

            logger.info(
                "Files written successfully",
                extra={
                    "panel_path": str(panel_path),
                    "lineage_log_path": str(LINEAGE_LOG_FILE),
                },
            )
            # Write run metadata & notice
            _write_run_meta(
                batch_id=str(batch.batch_id),
                asof_ts=batch.asof_ts.isoformat(),
                provisional=results["provisional"],
                reasons=results["reasons"],
            )
            _write_notice(results["provisional"], results["reasons"])
        else:
            logger.info("Dry run completed - no files written")

        return results

    except Exception as e:
        logger.error("Pipeline failed", extra={"error": str(e)})
        raise


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description="Fetch EIA data and build monthly panel"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print counts but don't write files"
    )

    args = parser.parse_args()

    try:
        results = fetch_and_build_panel(dry_run=args.dry_run)

        if "error" in results:
            mode = _get_mode()
            if mode == "ci":
                status = {
                    "status": "needs_review",
                    "error": results.get("error"),
                    "batch_id": results.get("batch_id"),
                    "reasons": results.get("reasons", []),
                }
                _write_status(status)
                print("WARNING: CI soft-fail. See outputs/status.json for details.")
                sys.exit(0)
            print(f"ERROR: Pipeline failed: {results['error']}")
            sys.exit(2)

        # Print results
        print("\nPipeline Results:")
        print(f"   Batch ID: {results['batch_id']}")
        print(f"   Timestamp: {results['asof_ts']}")
        print(f"   Raw data rows: {results['raw_rows']}")
        print(f"   Panel rows: {results['panel_rows']}")
        print(f"   Existing rows: {results['existing_rows']}")
        print(f"   Rows to add: {results['rows_to_add']}")

        if results.get("date_range"):
            print(
                f"   Date range: {results['date_range']['start']} to "
                f"{results['date_range']['end']}"
            )

        if args.dry_run:
            print("\nDRY RUN - No files written")
        else:
            print("\nSUCCESS: Pipeline completed - files written")

        sys.exit(0)

    except Exception as e:
        mode = _get_mode()
        if mode == "ci":
            _write_status({"status": "error", "error": str(e)})
            print("WARNING: CI soft-fail due to exception. See outputs/status.json.")
            sys.exit(0)
        print(f"ERROR: Pipeline failed: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()

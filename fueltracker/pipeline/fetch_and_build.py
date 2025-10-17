"""
Pipeline for fetching EIA data and building monthly panel.
"""

import argparse
import os
import sys
from typing import Any, Dict

from ..config import OUTPUTS_DIR, PANEL_FILE
from ..eia_client import EIAClient
from ..io_parquet import append_revision, read_panel, write_lineage_log
from ..lineage import start_batch
from ..logging_utils import get_logger
from ..panel import build_monthly_panel, get_panel_summary

logger = get_logger(__name__)

# Lineage log file
LINEAGE_LOG_FILE = OUTPUTS_DIR / "lineage_log.jsonl"


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
                extra={"allow_sample_fallback": allow_sample_fallback},
            )

        client = EIAClient(
            EIA_API_KEY,
            allow_sample_fallback=allow_sample_fallback,
        )

        # Fetch data from EIA API
        logger.info("Fetching data from EIA API")
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
                extra={"endpoint": "petroleum/pri/spt/data"},
            )
            return {
                "error": "No data fetched",
                "batch_id": str(batch.batch_id),
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
            print(f"ERROR: Pipeline failed: {results['error']}")
            sys.exit(1)

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
        print(f"ERROR: Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""I/O operations for Fuel Tracker using PyArrow and Parquet."""

import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import Dict, Any, Optional
from .contracts import BatchMeta
from .logging_utils import get_logger

logger = get_logger(__name__)


def read_panel(path: Path) -> pd.DataFrame:
    """
    Read panel from parquet file if it exists, otherwise return empty DataFrame with correct dtypes.

    Args:
        path: Path to the parquet file

    Returns:
        DataFrame with panel data or empty DataFrame with correct dtypes
    """
    if not path.exists():
        logger.info("Panel file does not exist, returning empty DataFrame", extra={"path": str(path)})
        return _create_empty_panel()

    try:
        logger.info("Reading existing panel", extra={"path": str(path)})
        df = pd.read_parquet(path)
        
        # Ensure simple index (no multiindex)
        if isinstance(df.index, pd.MultiIndex):
            logger.warning("Panel has multiindex, resetting to simple index")
            df = df.reset_index(drop=True)
        
        logger.info("Panel read successfully", extra={
            "path": str(path),
            "rows": len(df),
            "columns": list(df.columns)
        })
        return df
    except Exception as e:
        logger.error("Failed to read panel", extra={"path": str(path), "error": str(e)})
        logger.info("Returning empty DataFrame due to read error")
        return _create_empty_panel()


def _create_empty_panel() -> pd.DataFrame:
    """
    Create empty DataFrame with correct dtypes for panel.

    Returns:
        Empty DataFrame with correct schema
    """
    empty_df = pd.DataFrame({
        'period': pd.Series(dtype='object'),  # date
        'value_mmcf': pd.Series(dtype='float64'),
        'metric': pd.Series(dtype='object'),
        'freq': pd.Series(dtype='object'),
        'batch_id': pd.Series(dtype='object'),  # UUID
        'asof_ts': pd.Series(dtype='object')   # datetime
    })
    return empty_df


def append_revision(df: pd.DataFrame, path: Path) -> None:
    """
    Append revision to existing panel using PyArrow (append-only, no overwrites).

    Args:
        df: DataFrame to append
        path: Path to the parquet file

    Raises:
        ValueError: If DataFrame is empty
        FileExistsError: If trying to overwrite existing file
    """
    if df.empty:
        raise ValueError("Cannot append empty DataFrame")

    if path.exists():
        # Read existing data
        existing_df = read_panel(path)
        
        # Combine existing and new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        
        # Remove duplicates based on period and batch_id
        combined_df = combined_df.drop_duplicates(subset=['period', 'batch_id'], keep='last')
        
        # Sort by period
        combined_df = combined_df.sort_values('period').reset_index(drop=True)
        
        logger.info("Appending revision to existing panel", extra={
            "path": str(path),
            "existing_rows": len(existing_df),
            "new_rows": len(df),
            "combined_rows": len(combined_df),
            "duplicates_removed": len(existing_df) + len(df) - len(combined_df)
        })
        
        # Write combined data
        _write_panel(combined_df, path)
    else:
        # Create new file
        logger.info("Creating new panel file", extra={
            "path": str(path),
            "rows": len(df)
        })
        _write_panel(df, path)


def _write_panel(df: pd.DataFrame, path: Path) -> None:
    """
    Write panel DataFrame to parquet file using PyArrow.

    Args:
        df: DataFrame to write
        path: Path to the output file
    """
    try:
        # Ensure simple index
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index(drop=True)
        
        # Convert UUIDs to strings for PyArrow compatibility
        df_copy = df.copy()
        if 'batch_id' in df_copy.columns:
            df_copy['batch_id'] = df_copy['batch_id'].astype(str)
        
        # Convert to PyArrow table
        table = pa.Table.from_pandas(df_copy)
        
        # Write using PyArrow
        pq.write_table(table, path, compression='snappy')
        
        logger.info("Panel written successfully", extra={
            "path": str(path),
            "rows": len(df),
            "columns": list(df.columns)
        })
    except Exception as e:
        logger.error("Failed to write panel", extra={
            "path": str(path),
            "error": str(e)
        })
        raise


def write_lineage_log(batch: BatchMeta, rows_added: int, start_date: str, end_date: str,
                     log_path: Path) -> None:
    """
    Write lineage log entry to JSONL file.

    Args:
        batch: Batch metadata
        rows_added: Number of rows added
        start_date: Start date of the data
        end_date: End date of the data
        log_path: Path to the lineage log file
    """
    log_entry = {
        "batch_id": str(batch.batch_id),
        "asof_ts": batch.asof_ts.isoformat(),
        "rows_added": rows_added,
        "start": start_date,
        "end": end_date,
        "source": batch.source,
        "notes": batch.notes
    }
    
    try:
        # Ensure directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL file
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info("Lineage log entry written", extra=log_entry)
    except Exception as e:
        logger.error("Failed to write lineage log", extra={
            "error": str(e),
            "log_path": str(log_path)
        })
        raise


def get_panel_info(path: Path) -> Dict[str, Any]:
    """
    Get information about a panel file.

    Args:
        path: Path to the panel file

    Returns:
        Dictionary with panel information
    """
    if not path.exists():
        return {"exists": False, "error": "File does not exist"}
    
    try:
        # Get file metadata
        file_info = path.stat()
        
        # Read panel for additional info
        df = read_panel(path)
        
        info = {
            "exists": True,
            "file_size_mb": round(file_info.st_size / (1024 * 1024), 2),
            "last_modified": pd.Timestamp(file_info.st_mtime, unit='s').isoformat(),
            "rows": len(df),
            "columns": list(df.columns) if not df.empty else [],
            "has_lineage": all(col in df.columns for col in ['batch_id', 'asof_ts']) if not df.empty else False
        }
        
        if not df.empty:
            info.update({
                "date_range": {
                    "start": df['period'].min().isoformat(),
                    "end": df['period'].max().isoformat()
                },
                "unique_batches": df['batch_id'].nunique() if 'batch_id' in df.columns else 0
            })
        
        return info
    except Exception as e:
        return {
            "exists": True,
            "error": f"Failed to read file: {str(e)}"
        }
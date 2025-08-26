"""
Panel building and validation for Fuel Tracker.
"""

from typing import Any, Dict, List

import pandas as pd

from .contracts import BatchMeta, MonthlyFuelRow
from .lineage import attach_lineage_columns
from .logging_utils import get_logger

logger = get_logger(__name__)


def build_monthly_panel(raw_df: pd.DataFrame, batch: BatchMeta) -> pd.DataFrame:
    """
    Build monthly panel from raw DataFrame with proper schema mapping.

    Args:
        raw_df: Raw DataFrame with EIA data
        batch: Batch metadata for lineage tracking

    Returns:
        DataFrame conforming to MonthlyFuelRow schema with lineage columns
    """
    if raw_df.empty:
        logger.warning("Raw DataFrame is empty, returning empty panel")
        return pd.DataFrame()

    logger.info(
        "Building monthly panel",
        extra={
            "raw_rows": len(raw_df),
            "raw_columns": list(raw_df.columns),
            "batch_id": str(batch.batch_id),
        },
    )

    try:
        # Create a copy to avoid modifying the original
        panel_df = raw_df.copy()

        # Map raw columns to schema
        panel_df = _map_columns_to_schema(panel_df)

        # Enforce month-end dates
        panel_df = _enforce_month_end_dates(panel_df)

        # Add required schema fields
        panel_df['metric'] = "pipeline_compressor_fuel"
        panel_df['freq'] = "monthly"

        # Attach lineage columns
        panel_df = attach_lineage_columns(panel_df, batch)

        # Validate the panel
        panel_df = _validate_panel(panel_df)

        logger.info(
            "Monthly panel built successfully",
            extra={
                "final_rows": len(panel_df),
                "final_columns": list(panel_df.columns),
                "date_range": (
                    f"{panel_df['period'].min()} to {panel_df['period'].max()}"
                ),
            },
        )

        return panel_df

    except Exception as e:
        logger.error(
            "Failed to build monthly panel",
            extra={"error": str(e), "batch_id": str(batch.batch_id)},
        )
        raise


def _map_columns_to_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map raw DataFrame columns to MonthlyFuelRow schema.

    Args:
        df: Raw DataFrame

    Returns:
        DataFrame with mapped columns
    """
    # Expected column mappings
    column_mappings = {
        'period': ['period', 'date', 'time', 'timestamp'],
        'value_mmcf': ['value', 'value_mmcf', 'consumption', 'fuel_consumption'],
    }

    mapped_df = df.copy()

    # Map period column
    period_col = _find_column(df, column_mappings['period'])
    if period_col:
        mapped_df['period'] = df[period_col]
        logger.debug(f"Mapped period column: {period_col} -> period")
    else:
        raise ValueError("Could not find period column in raw data")

    # Map value column
    value_col = _find_column(df, column_mappings['value_mmcf'])
    if value_col:
        mapped_df['value_mmcf'] = df[value_col]
        logger.debug(f"Mapped value column: {value_col} -> value_mmcf")
    else:
        raise ValueError("Could not find value column in raw data")

    # Keep only the mapped columns
    mapped_df = mapped_df[['period', 'value_mmcf']]

    return mapped_df


def _find_column(df: pd.DataFrame, possible_names: List[str]) -> str:
    """
    Find a column by trying possible names.

    Args:
        df: DataFrame to search
        possible_names: List of possible column names

    Returns:
        Found column name or None
    """
    for name in possible_names:
        if name in df.columns:
            return name

    # Try case-insensitive matching
    for name in possible_names:
        for col in df.columns:
            if col.lower() == name.lower():
                return col

    return None


def _enforce_month_end_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce month-end dates by coercing to Period('M') then to timestamp('M').

    Args:
        df: DataFrame with period column

    Returns:
        DataFrame with month-end dates
    """
    df_copy = df.copy()

    # Convert to pandas Period and then to month-end timestamp
    df_copy['period'] = (
        pd.to_datetime(df_copy['period']).dt.to_period('M').dt.to_timestamp('M')
    )

    # Convert to date objects for consistency
    df_copy['period'] = df_copy['period'].dt.date

    logger.debug(
        "Enforced month-end dates",
        extra={"date_range": f"{df_copy['period'].min()} to {df_copy['period'].max()}"},
    )

    return df_copy


def _validate_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate panel DataFrame using MonthlyFuelRow model.

    Args:
        df: DataFrame to validate

    Returns:
        Validated DataFrame
    """
    if df.empty:
        return df

    # Validate a sample of rows
    sample_size = min(10, len(df))
    sample_indices = df.sample(n=sample_size, random_state=42).index

    validation_errors = []

    for idx in sample_indices:
        row = df.loc[idx]
        try:
            # Create a mock BatchMeta for validation 
            # (we'll use the real one from lineage)
            mock_batch = BatchMeta(
                batch_id=row['batch_id'], asof_ts=row['asof_ts'], source="EIA"
            )

            # Validate the row
            MonthlyFuelRow(
                period=row['period'],
                value_mmcf=row['value_mmcf'],
                metric=row['metric'],
                freq=row['freq'],
                lineage=mock_batch,
            )

        except Exception as e:
            validation_errors.append(f"Row {idx}: {str(e)}")

    if validation_errors:
        error_msg = f"Panel validation failed: {'; '.join(validation_errors)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(
        "Panel validation passed",
        extra={"sample_size": sample_size, "total_rows": len(df)},
    )

    return df


def get_panel_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary information about the panel.

    Args:
        df: Panel DataFrame

    Returns:
        Dictionary with panel summary
    """
    if df.empty:
        return {"error": "Panel is empty"}

    summary = {
        "total_rows": len(df),
        "date_range": {
            "start": df['period'].min().isoformat(),
            "end": df['period'].max().isoformat(),
        },
        "value_stats": {
            "min": float(df['value_mmcf'].min()),
            "max": float(df['value_mmcf'].max()),
            "mean": float(df['value_mmcf'].mean()),
            "std": float(df['value_mmcf'].std()),
        },
        "columns": list(df.columns),
        "has_lineage": all(col in df.columns for col in ['batch_id', 'asof_ts']),
    }

    return summary

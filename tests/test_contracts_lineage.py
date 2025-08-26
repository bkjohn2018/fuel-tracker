"""
Unit tests for contracts and lineage modules.
"""

import pytest
import pandas as pd
from datetime import date, datetime, timezone
from uuid import UUID
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, '.')

from fueltracker.contracts import BatchMeta, MonthlyFuelRow, PanelFrameMeta
from fueltracker.lineage import (
    start_batch, 
    attach_lineage_columns, 
    validate_lineage_columns,
    get_lineage_summary
)


class TestBatchMeta:
    """Test BatchMeta model validation and behavior."""
    
    def test_valid_batch_meta(self):
        """Test creating valid BatchMeta."""
        batch_id = UUID('12345678-1234-5678-1234-567812345678')
        asof_ts = datetime.now(timezone.utc)
        
        batch_meta = BatchMeta(
            batch_id=batch_id,
            asof_ts=asof_ts,
            source="EIA",
            notes="Test batch"
        )
        
        assert batch_meta.batch_id == batch_id
        assert batch_meta.asof_ts == asof_ts
        assert batch_meta.source == "EIA"
        assert batch_meta.notes == "Test batch"
    
    def test_batch_meta_without_notes(self):
        """Test BatchMeta without optional notes."""
        batch_id = UUID('12345678-1234-5678-1234-567812345678')
        asof_ts = datetime.now(timezone.utc)
        
        batch_meta = BatchMeta(
            batch_id=batch_id,
            asof_ts=asof_ts,
            source="EIA"
        )
        
        assert batch_meta.notes is None
    
    def test_batch_meta_timezone_validation(self):
        """Test that asof_ts must be timezone-aware."""
        batch_id = UUID('12345678-1234-5678-1234-567812345678')
        asof_ts = datetime.now()  # No timezone
        
        with pytest.raises(ValueError, match="asof_ts must be timezone-aware"):
            BatchMeta(
                batch_id=batch_id,
                asof_ts=asof_ts,
                source="EIA"
            )
    
    def test_batch_meta_source_validation(self):
        """Test that source must be 'EIA'."""
        batch_id = UUID('12345678-1234-5678-1234-567812345678')
        asof_ts = datetime.now(timezone.utc)
        
        with pytest.raises(ValueError):
            BatchMeta(
                batch_id=batch_id,
                asof_ts=asof_ts,
                source="INVALID_SOURCE"
            )


class TestMonthlyFuelRow:
    """Test MonthlyFuelRow model validation and behavior."""
    
    def test_valid_monthly_fuel_row(self):
        """Test creating valid MonthlyFuelRow."""
        batch_meta = BatchMeta(
            batch_id=UUID('12345678-1234-5678-1234-567812345678'),
            asof_ts=datetime.now(timezone.utc),
            source="EIA"
        )
        
        # Use month-end date
        period = date(2024, 1, 31)
        
        fuel_row = MonthlyFuelRow(
            period=period,
            value_mmcf=75.5,
            metric="pipeline_compressor_fuel",
            freq="monthly",
            lineage=batch_meta
        )
        
        assert fuel_row.period == period
        assert fuel_row.value_mmcf == 75.5
        assert fuel_row.metric == "pipeline_compressor_fuel"
        assert fuel_row.freq == "monthly"
        assert fuel_row.lineage == batch_meta
    
    def test_monthly_fuel_row_period_validation(self):
        """Test that period must be month-end date."""
        batch_meta = BatchMeta(
            batch_id=UUID('12345678-1234-5678-1234-567812345678'),
            asof_ts=datetime.now(timezone.utc),
            source="EIA"
        )
        
        # Use non-month-end date
        period = date(2024, 1, 15)
        
        with pytest.raises(ValueError, match="period must be month-end date"):
            MonthlyFuelRow(
                period=period,
                value_mmcf=75.5,
                metric="pipeline_compressor_fuel",
                freq="monthly",
                lineage=batch_meta
            )
    
    def test_monthly_fuel_row_value_validation(self):
        """Test that value_mmcf must be non-negative."""
        batch_meta = BatchMeta(
            batch_id=UUID('12345678-1234-5678-1234-567812345678'),
            asof_ts=datetime.now(timezone.utc),
            source="EIA"
        )
        
        period = date(2024, 1, 31)
        
        with pytest.raises(ValueError, match="value_mmcf must be non-negative"):
            MonthlyFuelRow(
                period=period,
                value_mmcf=-5.0,
                metric="pipeline_compressor_fuel",
                freq="monthly",
                lineage=batch_meta
            )


class TestPanelFrameMeta:
    """Test PanelFrameMeta model validation and behavior."""
    
    def test_valid_panel_frame_meta(self):
        """Test creating valid PanelFrameMeta."""
        panel_meta = PanelFrameMeta(
            vintage_label="2024-01-15T10:30Z",
            n_rows=100,
            start=date(2020, 1, 31),
            end=date(2024, 1, 31)
        )
        
        assert panel_meta.vintage_label == "2024-01-15T10:30Z"
        assert panel_meta.n_rows == 100
        assert panel_meta.start == date(2020, 1, 31)
        assert panel_meta.end == date(2024, 1, 31)
    
    def test_panel_frame_meta_vintage_label_validation(self):
        """Test vintage label format validation."""
        with pytest.raises(ValueError, match="vintage_label must be in format"):
            PanelFrameMeta(
                vintage_label="invalid_format",
                n_rows=100,
                start=date(2020, 1, 31),
                end=date(2024, 1, 31)
            )
    
    def test_panel_frame_meta_n_rows_validation(self):
        """Test that n_rows must be non-negative."""
        with pytest.raises(ValueError, match="n_rows must be non-negative"):
            PanelFrameMeta(
                vintage_label="2024-01-15T10:30Z",
                n_rows=-5,
                start=date(2020, 1, 31),
                end=date(2024, 1, 31)
            )
    
    def test_panel_frame_meta_date_validation(self):
        """Test that end date must be after start date."""
        with pytest.raises(ValueError, match="end date must be after start date"):
            PanelFrameMeta(
                vintage_label="2024-01-15T10:30Z",
                n_rows=100,
                start=date(2024, 1, 31),
                end=date(2020, 1, 31)  # End before start
            )


class TestLineageFunctions:
    """Test lineage management functions."""
    
    def test_start_batch(self):
        """Test starting a new batch."""
        batch_meta = start_batch(source="EIA", notes="Test batch")
        
        assert isinstance(batch_meta, BatchMeta)
        assert batch_meta.source == "EIA"
        assert batch_meta.notes == "Test batch"
        assert batch_meta.asof_ts.tzinfo is not None  # Timezone-aware
        assert isinstance(batch_meta.batch_id, UUID)
    
    def test_attach_lineage_columns(self):
        """Test attaching lineage columns to DataFrame."""
        # Create test DataFrame
        df = pd.DataFrame({
            'period': [date(2024, 1, 31), date(2024, 2, 29)],
            'value': [75.5, 78.2]
        })
        
        batch_meta = start_batch()
        df_with_lineage = attach_lineage_columns(df, batch_meta)
        
        # Check that lineage columns were added
        assert 'batch_id' in df_with_lineage.columns
        assert 'asof_ts' in df_with_lineage.columns
        
        # Check that original data is preserved
        assert len(df_with_lineage) == len(df)
        assert all(df_with_lineage['period'] == df['period'])
        assert all(df_with_lineage['value'] == df['value'])
        
        # Check lineage values
        assert all(df_with_lineage['batch_id'] == batch_meta.batch_id)
        assert all(df_with_lineage['asof_ts'] == batch_meta.asof_ts)
    
    def test_attach_lineage_columns_empty_df(self):
        """Test attaching lineage columns to empty DataFrame."""
        df = pd.DataFrame()
        batch_meta = start_batch()
        
        df_with_lineage = attach_lineage_columns(df, batch_meta)
        
        assert df_with_lineage.empty
        assert 'batch_id' not in df_with_lineage.columns
        assert 'asof_ts' not in df_with_lineage.columns
    
    def test_validate_lineage_columns_valid(self):
        """Test validation of valid lineage columns."""
        df = pd.DataFrame({
            'period': [date(2024, 1, 31)],
            'value': [75.5],
            'batch_id': [UUID('12345678-1234-5678-1234-567812345678')],
            'asof_ts': [datetime.now(timezone.utc)]
        })
        
        assert validate_lineage_columns(df)
    
    def test_validate_lineage_columns_missing(self):
        """Test validation with missing lineage columns."""
        df = pd.DataFrame({
            'period': [date(2024, 1, 31)],
            'value': [75.5]
        })
        
        assert not validate_lineage_columns(df)
    
    def test_get_lineage_summary(self):
        """Test getting lineage summary."""
        df = pd.DataFrame({
            'period': [date(2024, 1, 31), date(2024, 2, 29)],
            'value': [75.5, 78.2],
            'batch_id': [UUID('12345678-1234-5678-1234-567812345678')] * 2,
            'asof_ts': [datetime.now(timezone.utc)] * 2
        })
        
        summary = get_lineage_summary(df)
        
        assert summary['total_rows'] == 2
        assert summary['unique_batches'] == 1
        assert 'earliest_timestamp' in summary
        assert 'latest_timestamp' in summary
        assert summary['lineage_columns'] == ['batch_id', 'asof_ts']
    
    def test_get_lineage_summary_empty_df(self):
        """Test getting lineage summary from empty DataFrame."""
        df = pd.DataFrame()
        summary = get_lineage_summary(df)
        
        assert summary['error'] == "DataFrame is empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

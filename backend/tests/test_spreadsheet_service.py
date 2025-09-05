"""
Pandas Skill Tests with Sample Finance Data
Tests spreadsheet analysis functionality using pytest
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from services.spreadsheet_service import SpreadsheetService


@pytest.fixture
def sample_finance_data():
    """Create sample finance data for testing"""
    data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'Revenue': [1000.50, 1250.75, 980.25, 1500.00, 1100.80],
        'Expenses': [450.25, 520.30, 380.15, 650.40, 490.60],
        'Profit': [550.25, 730.45, 600.10, 849.60, 610.20],
        'Category': ['Sales', 'Marketing', 'Sales', 'Operations', 'Sales'],
        'Region': ['North', 'South', 'North', 'East', 'West']
    }
    return pd.DataFrame(data)


@pytest.fixture
def finance_xlsx_file(sample_finance_data):
    """Create a temporary Excel file with finance data"""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        sample_finance_data.to_excel(tmp_file.name, index=False)
        yield tmp_file.name
    os.unlink(tmp_file.name)


@pytest.fixture
def finance_csv_file(sample_finance_data):
    """Create a temporary CSV file with finance data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
        sample_finance_data.to_csv(tmp_file.name, index=False)
        yield tmp_file.name
    os.unlink(tmp_file.name)


@pytest.fixture
def spreadsheet_service():
    """Create SpreadsheetService instance"""
    return SpreadsheetService()


class TestSpreadsheetService:
    """Test cases for spreadsheet analysis functionality"""

    @pytest.mark.asyncio
    async def test_sum_operation_excel(self, spreadsheet_service, finance_xlsx_file):
        """Test sum operation on Excel file"""
        result = await spreadsheet_service.analyze(
            path=finance_xlsx_file,
            operation='sum',
            column='Revenue'
        )
        
        assert result['success'] is True
        assert result['result'] == 5832.30  # Sum of all revenue values
        assert result['matched_column'] == 'Revenue'
        assert result['cells_count'] == 5
        assert result['operation'] == 'sum'

    @pytest.mark.asyncio
    async def test_average_operation_csv(self, spreadsheet_service, finance_csv_file):
        """Test average operation on CSV file"""
        result = await spreadsheet_service.analyze(
            path=finance_csv_file,
            operation='avg',
            column='Profit'
        )
        
        assert result['success'] is True
        assert abs(result['result'] - 668.12) < 0.01  # Average of profit values
        assert result['matched_column'] == 'Profit'
        assert result['cells_count'] == 5

    @pytest.mark.asyncio
    async def test_count_operation(self, spreadsheet_service, finance_csv_file):
        """Test count operation"""
        result = await spreadsheet_service.analyze(
            path=finance_csv_file,
            operation='count',
            column='Category'
        )
        
        assert result['success'] is True
        assert result['result'] == 5
        assert result['matched_column'] == 'Category'

    @pytest.mark.asyncio
    async def test_fuzzy_column_matching(self, spreadsheet_service, finance_xlsx_file):
        """Test fuzzy column name matching"""
        # Test partial match
        result = await spreadsheet_service.analyze(
            path=finance_xlsx_file,
            operation='sum',
            column='rev'  # Should match 'Revenue'
        )
        
        assert result['success'] is True
        assert result['matched_column'] == 'Revenue'

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self, spreadsheet_service, finance_csv_file):
        """Test case-insensitive column matching"""
        result = await spreadsheet_service.analyze(
            path=finance_csv_file,
            operation='avg',
            column='EXPENSES'  # Should match 'Expenses'
        )
        
        assert result['success'] is True
        assert result['matched_column'] == 'Expenses'
        assert abs(result['result'] - 498.34) < 0.01

    @pytest.mark.asyncio
    async def test_total_operation_same_as_sum(self, spreadsheet_service, finance_xlsx_file):
        """Test that total operation works the same as sum"""
        sum_result = await spreadsheet_service.analyze(
            path=finance_xlsx_file,
            operation='sum',
            column='Revenue'
        )
        
        total_result = await spreadsheet_service.analyze(
            path=finance_xlsx_file,
            operation='total',
            column='Revenue'
        )
        
        assert sum_result['result'] == total_result['result']

    @pytest.mark.asyncio
    async def test_nonexistent_file(self, spreadsheet_service):
        """Test handling of nonexistent file"""
        with pytest.raises(FileNotFoundError):
            await spreadsheet_service.analyze(
                path='nonexistent.xlsx',
                operation='sum',
                column='Revenue'
            )

    @pytest.mark.asyncio
    async def test_invalid_column_name(self, spreadsheet_service, finance_csv_file):
        """Test handling of invalid column name"""
        with pytest.raises(ValueError, match="Column .* not found"):
            await spreadsheet_service.analyze(
                path=finance_csv_file,
                operation='sum',
                column='NonexistentColumn'
            )

    @pytest.mark.asyncio
    async def test_invalid_operation(self, spreadsheet_service, finance_xlsx_file):
        """Test handling of invalid operation"""
        with pytest.raises(ValueError, match="Unsupported operation"):
            await spreadsheet_service.analyze(
                path=finance_xlsx_file,
                operation='invalid_op',
                column='Revenue'
            )

    @pytest.mark.asyncio
    async def test_non_numeric_column_sum(self, spreadsheet_service, finance_csv_file):
        """Test sum operation on non-numeric column"""
        with pytest.raises(ValueError, match="contains no numeric data"):
            await spreadsheet_service.analyze(
                path=finance_csv_file,
                operation='sum',
                column='Category'
            )

    @pytest.mark.asyncio
    async def test_mixed_data_types(self, spreadsheet_service):
        """Test handling of mixed data types in numeric columns"""
        # Create data with mixed types
        mixed_data = pd.DataFrame({
            'Values': [100, '200', 300, 'invalid', 400],
            'Names': ['A', 'B', 'C', 'D', 'E']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            mixed_data.to_csv(tmp_file.name, index=False)
            
            try:
                result = await spreadsheet_service.analyze(
                    path=tmp_file.name,
                    operation='sum',
                    column='Values'
                )
                
                # Should sum only valid numeric values: 100 + 200 + 300 + 400 = 1000
                assert result['result'] == 1000
                assert result['cells_count'] == 4  # Only 4 valid numeric values
                
            finally:
                os.unlink(tmp_file.name)

    @pytest.mark.asyncio
    async def test_empty_spreadsheet(self, spreadsheet_service):
        """Test handling of empty spreadsheet"""
        empty_data = pd.DataFrame()
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            empty_data.to_csv(tmp_file.name, index=False)
            
            try:
                with pytest.raises(ValueError, match="Spreadsheet is empty"):
                    await spreadsheet_service.analyze(
                        path=tmp_file.name,
                        operation='sum',
                        column='Revenue'
                    )
            finally:
                os.unlink(tmp_file.name)

    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, spreadsheet_service):
        """Test performance with larger dataset"""
        # Create larger dataset
        large_data = pd.DataFrame({
            'Revenue': [1000 + i for i in range(1000)],
            'Expenses': [500 + i * 0.5 for i in range(1000)],
            'ID': range(1000)
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            large_data.to_excel(tmp_file.name, index=False)
            
            try:
                import time
                start_time = time.time()
                
                result = await spreadsheet_service.analyze(
                    path=tmp_file.name,
                    operation='avg',
                    column='Revenue'
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                assert result['success'] is True
                assert result['cells_count'] == 1000
                assert processing_time < 5.0  # Should complete within 5 seconds
                
            finally:
                os.unlink(tmp_file.name)

    def test_column_info_extraction(self, spreadsheet_service, sample_finance_data):
        """Test column information extraction"""
        column_info = spreadsheet_service.get_column_info(sample_finance_data)
        
        assert 'Revenue' in column_info
        assert 'Category' in column_info
        
        revenue_info = column_info['Revenue']
        assert revenue_info['is_numeric'] is True
        assert revenue_info['non_null_count'] == 5
        assert revenue_info['null_count'] == 0
        
        category_info = column_info['Category']
        assert category_info['is_numeric'] is False
        assert category_info['unique_values'] == 3  # Sales, Marketing, Operations

    @pytest.mark.asyncio
    async def test_different_file_formats(self, spreadsheet_service, sample_finance_data):
        """Test support for different file formats"""
        formats = ['.csv', '.xlsx']
        
        for fmt in formats:
            with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as tmp_file:
                if fmt == '.csv':
                    sample_finance_data.to_csv(tmp_file.name, index=False)
                else:
                    sample_finance_data.to_excel(tmp_file.name, index=False)
                
                try:
                    result = await spreadsheet_service.analyze(
                        path=tmp_file.name,
                        operation='sum',
                        column='Revenue'
                    )
                    
                    assert result['success'] is True
                    assert result['result'] == 5832.30
                    
                finally:
                    os.unlink(tmp_file.name)
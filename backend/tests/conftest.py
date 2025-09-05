"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture(scope="session")
def sample_finance_xlsx():
    """Create sample finance Excel file for testing"""
    import pandas as pd
    
    data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'Revenue': [1000.50, 1250.75, 980.25, 1500.00, 1100.80],
        'Expenses': [450.25, 520.30, 380.15, 650.40, 490.60],
        'Profit': [550.25, 730.45, 600.10, 849.60, 610.20],
        'Category': ['Sales', 'Marketing', 'Sales', 'Operations', 'Sales'],
        'Region': ['North', 'South', 'North', 'East', 'West']
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        yield tmp_file.name
    
    os.unlink(tmp_file.name)


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from unittest.mock import MagicMock
    
    settings = MagicMock()
    settings.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    settings.ALLOWED_FILE_EXTENSIONS = ['.txt', '.csv', '.xlsx', '.pdf']
    settings.SAFE_DIRECTORIES = ['./documents', './data', './temp']
    settings.HF_API_TOKEN = 'test-token'
    
    return settings
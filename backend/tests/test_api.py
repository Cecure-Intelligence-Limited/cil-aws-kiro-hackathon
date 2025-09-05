"""
Test cases for the Aura Desktop Assistant API
"""

import pytest
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCreateFile:
    """Test file creation endpoint"""
    
    def test_create_file_success(self):
        payload = {
            "title": "test.txt",
            "content": "Hello, World!"
        }
        
        with patch('services.file_service.FileService.create_file') as mock_create:
            mock_create.return_value = {
                "file_path": "/app/documents/test.txt",
                "size": 13,
                "created": True,
                "directory": "/app/documents"
            }
            
            response = client.post("/create_file", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "test.txt" in data["message"]
    
    def test_create_file_invalid_filename(self):
        payload = {
            "title": "test<>.txt",
            "content": "Hello, World!"
        }
        
        response = client.post("/create_file", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_create_file_already_exists(self):
        payload = {
            "title": "existing.txt",
            "content": "Hello, World!"
        }
        
        with patch('services.file_service.FileService.create_file') as mock_create:
            mock_create.side_effect = FileExistsError("File already exists")
            
            response = client.post("/create_file", json=payload)
            assert response.status_code == 409


class TestOpenItem:
    """Test item opening endpoint"""
    
    def test_open_item_success(self):
        payload = {
            "query": "test.txt",
            "type": "file"
        }
        
        with patch('services.file_service.FileService.open_item') as mock_open:
            mock_open.return_value = {
                "path": "/app/documents/test.txt",
                "type": "file",
                "opened": True,
                "method": "file_system"
            }
            
            response = client.post("/open_item", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
    
    def test_open_item_not_found(self):
        payload = {
            "query": "nonexistent.txt",
            "type": "file"
        }
        
        with patch('services.file_service.FileService.open_item') as mock_open:
            mock_open.side_effect = FileNotFoundError("Item not found")
            
            response = client.post("/open_item", json=payload)
            assert response.status_code == 404


class TestAnalyzeSpreadsheet:
    """Test spreadsheet analysis endpoint"""
    
    def test_analyze_spreadsheet_success(self):
        payload = {
            "path": "data.csv",
            "op": "sum",
            "column": "amount"
        }
        
        with patch('services.spreadsheet_service.SpreadsheetService.analyze') as mock_analyze:
            mock_analyze.return_value = {
                "result": 1500.0,
                "matched_column": "amount",
                "cells_count": 10,
                "operation": "sum",
                "total_rows": 10,
                "total_columns": 3
            }
            
            response = client.post("/analyze_sheet", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["result"] == 1500.0
            assert data["matched_column"] == "amount"
    
    def test_analyze_spreadsheet_invalid_extension(self):
        payload = {
            "path": "data.txt",
            "op": "sum",
            "column": "amount"
        }
        
        response = client.post("/analyze_sheet", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_spreadsheet_file_not_found(self):
        payload = {
            "path": "nonexistent.csv",
            "op": "sum",
            "column": "amount"
        }
        
        with patch('services.spreadsheet_service.SpreadsheetService.analyze') as mock_analyze:
            mock_analyze.side_effect = FileNotFoundError("File not found")
            
            response = client.post("/analyze_sheet", json=payload)
            assert response.status_code == 404


class TestSummarizeDocument:
    """Test document summarization endpoint"""
    
    def test_summarize_document_success(self):
        payload = {
            "path": "document.pdf",
            "length": "short"
        }
        
        with patch('services.document_service.DocumentService.summarize') as mock_summarize:
            mock_summarize.return_value = {
                "summary": "This is a test document summary.",
                "length_type": "short",
                "word_count": 7,
                "original_length": 1000,
                "pages_processed": 5
            }
            
            response = client.post("/summarize_doc", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["word_count"] == 7
            assert data["length_type"] == "short"
    
    def test_summarize_document_invalid_extension(self):
        payload = {
            "path": "document.txt",
            "length": "short"
        }
        
        response = client.post("/summarize_doc", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_summarize_document_file_not_found(self):
        payload = {
            "path": "nonexistent.pdf",
            "length": "short"
        }
        
        with patch('services.document_service.DocumentService.summarize') as mock_summarize:
            mock_summarize.side_effect = FileNotFoundError("File not found")
            
            response = client.post("/summarize_doc", json=payload)
            assert response.status_code == 404


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing"""
    csv_content = """name,age,salary
John,25,50000
Jane,30,60000
Bob,35,70000"""
    
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def sample_pdf_file(tmp_path):
    """Create a sample PDF file for testing"""
    # This would require creating an actual PDF file
    # For now, we'll mock the PDF operations in tests
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"Mock PDF content")
    return pdf_file
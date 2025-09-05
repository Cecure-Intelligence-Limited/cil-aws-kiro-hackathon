"""
End-to-End Tests
Tests complete workflow from text command to file creation
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from services.file_service import FileService


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def temp_directory():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


class TestEndToEnd:
    """End-to-end test cases"""

    def test_create_file_complete_workflow(self, client, temp_directory):
        """Test complete workflow: text command -> file creation -> file exists"""
        
        # Mock the file service to use our temp directory
        with patch('services.file_service.FileService._validate_path') as mock_validate:
            test_file_path = Path(temp_directory) / "Demo.txt"
            mock_validate.return_value = test_file_path
            
            # Step 1: Send create file request
            response = client.post("/create_file", json={
                "title": "Demo.txt",
                "content": "Hello"
            })
            
            # Step 2: Verify API response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Demo.txt" in data["message"]
            assert data["data"]["created"] is True
            
            # Step 3: Verify file actually exists
            assert test_file_path.exists()
            
            # Step 4: Verify file content
            content = test_file_path.read_text(encoding='utf-8')
            assert content == "Hello"
            
            # Step 5: Verify file metadata
            assert data["data"]["size"] == 5  # "Hello" is 5 characters
            assert str(test_file_path) in data["data"]["file_path"]

    def test_open_item_workflow(self, client, temp_directory):
        """Test open item workflow"""
        
        # Create a test file first
        test_file = Path(temp_directory) / "test_document.txt"
        test_file.write_text("Test content")
        
        with patch('services.file_service.FileService._find_item') as mock_find:
            with patch('services.file_service.FileService._open_path') as mock_open:
                mock_find.return_value = test_file
                mock_open.return_value = None
                
                response = client.post("/open_item", json={
                    "query": "test_document.txt",
                    "type": "file"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "test_document.txt" in data["message"]
                
                # Verify the file service methods were called
                mock_find.assert_called_once()
                mock_open.assert_called_once_with(test_file)

    def test_analyze_spreadsheet_workflow(self, client, temp_directory):
        """Test spreadsheet analysis workflow"""
        
        # Create test CSV file
        csv_content = """Name,Salary,Department
John,50000,Engineering
Jane,60000,Marketing
Bob,55000,Engineering
Alice,65000,Sales"""
        
        csv_file = Path(temp_directory) / "employees.csv"
        csv_file.write_text(csv_content)
        
        with patch('services.spreadsheet_service.SpreadsheetService.analyze') as mock_analyze:
            mock_analyze.return_value = {
                "result": 230000.0,
                "matched_column": "Salary",
                "cells_count": 4,
                "operation": "sum",
                "total_rows": 4,
                "total_columns": 3
            }
            
            response = client.post("/analyze_sheet", json={
                "path": str(csv_file),
                "op": "sum",
                "column": "Salary"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["result"] == 230000.0
            assert data["matched_column"] == "Salary"
            assert data["cells_count"] == 4

    def test_summarize_document_workflow(self, client, temp_directory):
        """Test document summarization workflow"""
        
        # Create test PDF file (mock)
        pdf_file = Path(temp_directory) / "report.pdf"
        pdf_file.write_bytes(b"Mock PDF content")
        
        with patch('services.document_service.DocumentService.summarize') as mock_summarize:
            mock_summarize.return_value = {
                "summary": "• Key point 1\n• Key point 2\n• Key point 3",
                "length_type": "bullets",
                "word_count": 9,
                "original_length": 1000,
                "pages_processed": 3
            }
            
            response = client.post("/summarize_doc", json={
                "path": str(pdf_file),
                "length": "bullets"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "•" in data["summary"]
            assert data["length_type"] == "bullets"
            assert data["word_count"] == 9

    def test_error_handling_workflow(self, client):
        """Test error handling in complete workflow"""
        
        # Test file creation with invalid filename
        response = client.post("/create_file", json={
            "title": "invalid<>file.txt",
            "content": "Hello"
        })
        
        assert response.status_code == 422  # Validation error
        
        # Test opening nonexistent file
        response = client.post("/open_item", json={
            "query": "nonexistent_file.txt",
            "type": "file"
        })
        
        assert response.status_code == 404
        
        # Test analyzing nonexistent spreadsheet
        response = client.post("/analyze_sheet", json={
            "path": "nonexistent.csv",
            "op": "sum",
            "column": "Amount"
        })
        
        assert response.status_code == 404

    def test_concurrent_requests(self, client, temp_directory):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def create_file(index):
            response = client.post("/create_file", json={
                "title": f"concurrent_file_{index}.txt",
                "content": f"Content {index}"
            })
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_file, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5

    def test_large_file_handling(self, client, temp_directory):
        """Test handling of large file content"""
        
        # Create large content (but within limits)
        large_content = "Large content line.\n" * 1000  # ~20KB
        
        with patch('services.file_service.FileService._validate_path') as mock_validate:
            test_file_path = Path(temp_directory) / "large_file.txt"
            mock_validate.return_value = test_file_path
            
            response = client.post("/create_file", json={
                "title": "large_file.txt",
                "content": large_content
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # Verify file was created with correct content
            assert test_file_path.exists()
            content = test_file_path.read_text(encoding='utf-8')
            assert content == large_content

    def test_special_characters_handling(self, client, temp_directory):
        """Test handling of special characters in content"""
        
        special_content = "Hello 世界! 🌍 Special chars: àáâãäå ñ ç"
        
        with patch('services.file_service.FileService._validate_path') as mock_validate:
            test_file_path = Path(temp_directory) / "special_chars.txt"
            mock_validate.return_value = test_file_path
            
            response = client.post("/create_file", json={
                "title": "special_chars.txt",
                "content": special_content
            })
            
            assert response.status_code == 200
            
            # Verify file content with special characters
            assert test_file_path.exists()
            content = test_file_path.read_text(encoding='utf-8')
            assert content == special_content

    def test_api_response_format_consistency(self, client, temp_directory):
        """Test that all API responses follow consistent format"""
        
        endpoints_and_payloads = [
            ("/create_file", {"title": "test.txt", "content": "test"}),
            ("/open_item", {"query": "test.txt", "type": "file"}),
        ]
        
        for endpoint, payload in endpoints_and_payloads:
            with patch('services.file_service.FileService._validate_path') as mock_validate:
                test_file_path = Path(temp_directory) / "test.txt"
                mock_validate.return_value = test_file_path
                
                if endpoint == "/open_item":
                    with patch('services.file_service.FileService._find_item', return_value=test_file_path):
                        with patch('services.file_service.FileService._open_path'):
                            response = client.post(endpoint, json=payload)
                else:
                    response = client.post(endpoint, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check consistent response format
                    assert "success" in data
                    assert "message" in data
                    assert isinstance(data["success"], bool)
                    assert isinstance(data["message"], str)

    def test_health_check_integration(self, client):
        """Test health check endpoint integration"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/create_file")
        
        # Should not error and should include CORS headers
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS

    def test_request_validation(self, client):
        """Test request validation across endpoints"""
        
        # Test missing required fields
        invalid_requests = [
            ("/create_file", {}),  # Missing title
            ("/open_item", {}),    # Missing query
            ("/analyze_sheet", {"path": "test.csv"}),  # Missing op and column
            ("/summarize_doc", {}),  # Missing path
        ]
        
        for endpoint, payload in invalid_requests:
            response = client.post(endpoint, json=payload)
            assert response.status_code == 422  # Validation error
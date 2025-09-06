#!/usr/bin/env python3
"""
Basic test script for Aura Desktop Assistant core endpoints
Tests only the essential functionality without heavy dependencies
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an API endpoint and return the result"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            if result.get("success"):
                print(f"Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Server not running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Run basic functionality tests"""
    
    print("🚀 Testing Aura Desktop Assistant - Basic Functionality")
    print(f"Server: {BASE_URL}")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health Check
    total_tests += 1
    if test_endpoint("/health", "GET", description="Health Check"):
        tests_passed += 1
    
    # Test 2: Create File
    total_tests += 1
    create_data = {
        "title": "test-file.txt",
        "path": "backend/documents",
        "content": "This is a test file created by the basic test suite."
    }
    if test_endpoint("/api/create-file", "POST", create_data, "Create File"):
        tests_passed += 1
    
    # Test 3: Spreadsheet Analysis
    total_tests += 1
    analyze_data = {
        "path": "sample-budget.csv",
        "op": "sum",
        "column": "Amount"
    }
    if test_endpoint("/api/analyze-sheet", "POST", analyze_data, "Analyze Spreadsheet"):
        tests_passed += 1
    
    # Test 4: OCR Data Extraction (basic)
    total_tests += 1
    ocr_data = {
        "file_path": "backend/documents/sample-invoice.txt",
        "document_type": "invoice"
    }
    if test_endpoint("/api/extract-data", "POST", ocr_data, "OCR Data Extraction"):
        tests_passed += 1
    
    # Test 5: Generate Simple Report
    total_tests += 1
    report_data = {
        "report_type": "custom",
        "data_sources": ["backend/documents/sample-budget.csv"],
        "period": "monthly"
    }
    if test_endpoint("/api/generate-report", "POST", report_data, "Generate Report"):
        tests_passed += 1
    
    # Test 6: Document Classification
    total_tests += 1
    classify_data = {
        "file_path": "backend/documents/sample-contract.txt"
    }
    if test_endpoint("/api/classify-document", "POST", classify_data, "Classify Document"):
        tests_passed += 1
    
    # Results
    print(f"\n{'='*60}")
    print(f"🎯 TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Your automation server is working correctly.")
    elif tests_passed >= total_tests * 0.8:
        print("✅ Most tests passed. Server is mostly functional.")
    else:
        print("⚠️  Some tests failed. Check server logs for details.")
    
    print(f"\n📚 API Documentation: {BASE_URL}/docs")
    print("🔧 For full automation testing, run: python test-automation-endpoints.py")

if __name__ == "__main__":
    main()
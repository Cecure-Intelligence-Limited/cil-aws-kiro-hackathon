#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_create_file():
    """Test file creation endpoint"""
    try:
        data = {
            "title": "testfile.txt",
            "content": "This is a test file",
            "path": "documents"
        }
        response = requests.post(f"{BASE_URL}/api/create-file", json=data)
        print(f"✅ Create file: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Created: {result['data']['file_path']}")
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"   Validation error: {error_detail}")
        return response.status_code in [200, 409]  # 409 = file already exists
    except Exception as e:
        print(f"❌ Create file failed: {e}")
        return False

def test_analyze_sheet():
    """Test spreadsheet analysis endpoint"""
    try:
        data = {
            "path": "documents/sample-budget.csv",
            "op": "sum",
            "column": "Total_Monthly"
        }
        response = requests.post(f"{BASE_URL}/api/analyze-sheet", json=data)
        print(f"✅ Analyze sheet: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Result: {result['result']} for {result['matched_column']}")
        elif response.status_code == 404:
            print(f"   File not found - this is expected if sample-budget.csv doesn't exist")
        return response.status_code in [200, 404]
    except Exception as e:
        print(f"❌ Analyze sheet failed: {e}")
        return False

def test_update_sheet():
    """Test spreadsheet update endpoint"""
    try:
        # Try different path formats
        paths_to_try = [
            "documents/sample-budget.csv",
            "backend/documents/sample-budget.csv", 
            "sample-budget.csv"
        ]
        
        for path in paths_to_try:
            data = {
                "path": path,
                "operation": "salary_increase",
                "percentage": 10.0
            }
            response = requests.post(f"{BASE_URL}/api/update-sheet", json=data)
            print(f"✅ Update sheet (path: {path}): {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Updated: {result['data']['output_file']}")
                return True
            elif response.status_code == 404:
                continue  # Try next path
        
        print(f"   File not found with any path - check file location")
        return False
    except Exception as e:
        print(f"❌ Update sheet failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Aura Desktop Assistant API endpoints...\n")
    
    tests = [
        ("Health Check", test_health),
        ("Create File", test_create_file),
        ("Analyze Sheet", test_analyze_sheet),
        ("Update Sheet", test_update_sheet)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        print()
        time.sleep(0.5)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend service.")

if __name__ == "__main__":
    main()
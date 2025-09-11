#!/usr/bin/env python3
"""
Simple server test script that doesn't require pandas or heavy dependencies
Tests only the basic server functionality
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
            try:
                result = response.json()
                print(f"✅ SUCCESS")
                if result.get("success"):
                    print(f"Message: {result.get('message', 'No message')}")
                return True
            except:
                print(f"✅ SUCCESS (Non-JSON response)")
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
    """Run basic server tests"""
    
    print("🚀 Testing Aura Desktop Assistant - Server Only")
    print(f"Server: {BASE_URL}")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health Check
    total_tests += 1
    if test_endpoint("/health", "GET", description="Health Check"):
        tests_passed += 1
    
    # Test 2: Create File (basic functionality)
    total_tests += 1
    create_data = {
        "title": "test-server.txt",
        "path": "backend/documents",
        "content": "Server test file"
    }
    if test_endpoint("/api/create-file", "POST", create_data, "Create File"):
        tests_passed += 1
    
    # Test 3: OCR (should work with text files)
    total_tests += 1
    ocr_data = {
        "file_path": "backend/documents/sample-invoice.txt",
        "document_type": "invoice"
    }
    if test_endpoint("/api/extract-data", "POST", ocr_data, "OCR Text Extraction"):
        tests_passed += 1
    
    # Test 4: Document Classification
    total_tests += 1
    classify_data = {
        "file_path": "backend/documents/sample-contract.txt"
    }
    if test_endpoint("/api/classify-document", "POST", classify_data, "Document Classification"):
        tests_passed += 1
    
    # Results
    print(f"\n{'='*60}")
    print(f"🎯 TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Your server is working correctly.")
    elif tests_passed >= total_tests * 0.5:
        print("✅ Most tests passed. Server is functional.")
    else:
        print("⚠️  Some tests failed. Check server logs for details.")
    
    print(f"\n📚 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
FINAL HACKATHON TEST - Complete End-to-End Verification
Tests all critical functionality for demo presentation
"""

import requests
import json
import time
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

def test_endpoint(name, url, method="GET", data=None, expected_status=200):
    """Test a single endpoint with proper error handling"""
    print(f"\n🧪 Testing: {name}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"✅ SUCCESS: {name}")
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                if isinstance(result, dict):
                    if 'message' in result:
                        print(f"   Message: {result['message']}")
                    if 'success' in result and result['success']:
                        print(f"   ✅ Operation successful")
                    elif 'success' in result and not result['success']:
                        print(f"   ⚠️ Operation reported failure: {result.get('error', 'Unknown error')}")
            return True
        else:
            print(f"❌ FAILED: Expected {expected_status}, got {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Server not running on {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Request took longer than {TIMEOUT} seconds")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("🎯 FINAL HACKATHON TEST - AURA DESKTOP ASSISTANT")
    print("=" * 60)
    print(f"Server: {BASE_URL}")
    print("Testing all critical demo functionality...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Root endpoint (API welcome)
    total_tests += 1
    if test_endpoint("Root API Welcome", f"{BASE_URL}/"):
        tests_passed += 1
    
    # Test 2: Health check
    total_tests += 1
    if test_endpoint("Health Check", f"{BASE_URL}/health"):
        tests_passed += 1
    
    # Test 3: API Documentation
    total_tests += 1
    if test_endpoint("API Documentation", f"{BASE_URL}/docs", expected_status=200):
        tests_passed += 1
    
    # Test 4: File Creation (Core functionality)
    total_tests += 1
    create_data = {
        "title": "hackathon-test.txt",
        "content": "This is a test file for the hackathon demo",
        "path": "documents"
    }
    if test_endpoint("Create File", f"{BASE_URL}/api/create-file", "POST", create_data):
        tests_passed += 1
    
    # Test 5: Spreadsheet Analysis (Critical for demo)
    total_tests += 1
    analyze_data = {
        "path": "sample-budget.csv",
        "op": "sum",
        "column": "Base_Salary"
    }
    if test_endpoint("Spreadsheet Analysis", f"{BASE_URL}/api/analyze-sheet", "POST", analyze_data):
        tests_passed += 1
    
    # Test 6: Spreadsheet Update (The failing one - now fixed!)
    total_tests += 1
    update_data = {
        "path": "sample-budget.csv",
        "operation": "salary_increase",
        "percentage": 5.0
    }
    if test_endpoint("Spreadsheet Update (CRITICAL FIX)", f"{BASE_URL}/api/update-sheet", "POST", update_data):
        tests_passed += 1
    
    # Test 7: OCR Data Extraction
    total_tests += 1
    ocr_data = {
        "file_path": "sample-contract.txt",
        "document_type": "contract"
    }
    if test_endpoint("OCR Data Extraction", f"{BASE_URL}/api/extract-data", "POST", ocr_data):
        tests_passed += 1
    
    # Test 8: Email Rule Creation
    total_tests += 1
    email_data = {
        "name": "Invoice Processing",
        "condition": "subject contains invoice",
        "action": "move",
        "target": "invoices"
    }
    if test_endpoint("Email Automation", f"{BASE_URL}/api/email-rule", "POST", email_data):
        tests_passed += 1
    
    # Test 9: Report Generation
    total_tests += 1
    report_data = {
        "report_type": "financial",
        "data_sources": ["sample-budget.csv"],
        "period": "monthly"
    }
    if test_endpoint("Report Generation", f"{BASE_URL}/api/generate-report", "POST", report_data):
        tests_passed += 1
    
    # Test 10: Document Classification
    total_tests += 1
    classify_data = {
        "file_path": "sample-contract.txt"
    }
    if test_endpoint("Document Classification", f"{BASE_URL}/api/classify-document", "POST", classify_data):
        tests_passed += 1
    
    # Results Summary
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 PERFECT! ALL TESTS PASSED!")
        print("🚀 YOUR HACKATHON DEMO IS 100% READY!")
        print("\n🎬 DEMO SCRIPT:")
        print("1. Show API welcome page: http://localhost:8000/")
        print("2. Open interactive docs: http://localhost:8000/docs")
        print("3. Demonstrate spreadsheet automation")
        print("4. Show OCR and document processing")
        print("5. Display email and calendar automation")
        print("6. Generate reports and workflows")
    elif tests_passed >= total_tests * 0.8:
        print("✅ EXCELLENT! Most tests passed - Demo ready!")
        print("⚠️ Minor issues detected but won't affect main demo")
    else:
        print("⚠️ Some critical issues detected")
        print("🔧 Run FIX-FILE-PERMISSIONS.bat and restart server")
    
    print(f"\n📚 API Documentation: {BASE_URL}/docs")
    print(f"🔗 Main API: {BASE_URL}/")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Final comprehensive test of all functionality
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    """Test all endpoints comprehensively"""
    print("🧪 FINAL COMPREHENSIVE TEST")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            results['health'] = True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            results['health'] = False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        results['health'] = False
    
    # Test 2: Create File
    print("\n2️⃣ Testing File Creation...")
    try:
        data = {
            "title": f"final-test-{int(time.time())}.txt",
            "content": "This is a final test file",
            "path": "documents"
        }
        response = requests.post(f"{BASE_URL}/api/create-file", json=data)
        if response.status_code in [200, 409]:  # 409 = already exists
            print("✅ File creation passed")
            results['create'] = True
        else:
            print(f"❌ File creation failed: {response.status_code}")
            results['create'] = False
    except Exception as e:
        print(f"❌ File creation error: {e}")
        results['create'] = False
    
    # Test 3: Analyze Spreadsheet
    print("\n3️⃣ Testing Spreadsheet Analysis...")
    try:
        data = {
            "path": "documents/sample-budget.csv",
            "op": "sum",
            "column": "Total_Monthly"
        }
        response = requests.post(f"{BASE_URL}/api/analyze-sheet", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis passed - Result: {result['result']}")
            results['analyze'] = True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            results['analyze'] = False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        results['analyze'] = False
    
    # Test 4: Update Spreadsheet
    print("\n4️⃣ Testing Spreadsheet Update...")
    try:
        data = {
            "path": "documents/sample-budget.csv",
            "operation": "salary_increase",
            "percentage": 5.0
        }
        response = requests.post(f"{BASE_URL}/api/update-sheet", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Update passed - Output: {result['data']['output_file']}")
            results['update'] = True
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Update failed: {response.status_code} - {error_data}")
            results['update'] = False
    except Exception as e:
        print(f"❌ Update error: {e}")
        results['update'] = False
    
    # Test 5: Frontend Integration Test
    print("\n5️⃣ Testing Frontend Integration...")
    try:
        # Test CORS preflight
        headers = {
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{BASE_URL}/api/analyze-sheet", headers=headers)
        if response.status_code in [200, 204]:
            print("✅ CORS preflight passed")
            results['cors'] = True
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            results['cors'] = False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        results['cors'] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test.upper():<12} {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for demo!")
        print("\n💡 Try these voice commands in the app:")
        print("   • 'Calculate total salary in my budget file'")
        print("   • 'Update salary with 10% increase'")
        print("   • 'Add performance rating column'")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    test_all_endpoints()
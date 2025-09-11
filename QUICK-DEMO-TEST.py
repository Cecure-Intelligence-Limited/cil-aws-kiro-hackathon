#!/usr/bin/env python3
"""
QUICK DEMO TEST - Simple verification
"""

import requests
import sys

def quick_test():
    print("🧪 QUICK DEMO TEST")
    print("=" * 30)
    
    try:
        # Test backend
        print("Testing backend...")
        r = requests.get("http://localhost:8000/health", timeout=5)
        if r.status_code == 200:
            print("✅ Backend working")
        else:
            print("❌ Backend issue")
            return False
        
        # Test file creation
        print("Testing file creation...")
        data = {
            "title": "demo-test.txt",
            "content": "Demo working!",
            "path": "documents"
        }
        r = requests.post("http://localhost:8000/api/create-file", json=data, timeout=5)
        if r.status_code == 200:
            print("✅ File creation working")
        else:
            print("❌ File creation issue")
            return False
        
        # Test analysis
        print("Testing spreadsheet analysis...")
        data = {
            "path": "sample-budget.csv",
            "op": "sum",
            "column": "Total_Monthly"
        }
        r = requests.post("http://localhost:8000/api/analyze-sheet", json=data, timeout=5)
        if r.status_code == 200:
            result = r.json()
            print(f"✅ Analysis working - Total: ${result['result']:,.0f}")
        else:
            print("❌ Analysis issue")
            return False
        
        print("\n🏆 ALL TESTS PASSED!")
        print("🎯 DEMO IS READY!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 GO WIN THAT HACKATHON!")
    else:
        print("\n🔧 Check BACKEND and FRONTEND windows")
    sys.exit(0 if success else 1)
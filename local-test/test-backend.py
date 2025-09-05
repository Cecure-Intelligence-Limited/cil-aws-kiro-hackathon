#!/usr/bin/env python3
"""
Backend connectivity and API test for Aura Desktop Assistant
"""

import requests
import sys
import time

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_file_creation():
    """Test file creation API"""
    try:
        payload = {
            "title": "test-integration.txt",
            "content": "This file was created by Aura integration test!"
        }
        response = requests.post("http://localhost:8000/create_file", json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ File creation API test passed")
            return True
        else:
            print(f"❌ File creation failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File creation error: {e}")
        return False

def main():
    """Run backend tests"""
    print("🧪 Testing Aura Backend Connection")
    print("=" * 40)
    
    # Wait for backend to be ready
    max_retries = 10
    for attempt in range(max_retries):
        if test_backend_health():
            break
        if attempt < max_retries - 1:
            print(f"⏳ Waiting for backend... ({attempt + 1}/{max_retries})")
            time.sleep(2)
        else:
            print("❌ Backend not responding after retries")
            return False
    
    # Run API tests
    success = test_file_creation()
    
    if success:
        print("\n✅ All backend tests passed!")
        return True
    else:
        print("\n❌ Some backend tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
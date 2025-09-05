#!/usr/bin/env python3
"""
Check what endpoints are actually available
"""

import requests

BASE_URL = "http://localhost:8000"

def check_available_endpoints():
    """Check what endpoints are available"""
    print("🔍 Checking available endpoints...")
    
    # Try to get OpenAPI docs
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API docs available at /docs")
        else:
            print(f"❌ API docs not available: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing docs: {e}")
    
    # Try to get OpenAPI spec
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            spec = response.json()
            print(f"\n📋 Available endpoints:")
            for path, methods in spec.get('paths', {}).items():
                for method in methods.keys():
                    print(f"  {method.upper()} {path}")
        else:
            print(f"❌ OpenAPI spec not available: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting OpenAPI spec: {e}")
    
    # Test specific endpoints
    endpoints_to_test = [
        "/health",
        "/api/create-file",
        "/api/analyze-sheet", 
        "/api/update-sheet"
    ]
    
    print(f"\n🧪 Testing specific endpoints:")
    for endpoint in endpoints_to_test:
        try:
            response = requests.options(f"{BASE_URL}{endpoint}")
            print(f"  {endpoint:<20} {response.status_code}")
        except Exception as e:
            print(f"  {endpoint:<20} ERROR: {e}")

if __name__ == "__main__":
    check_available_endpoints()
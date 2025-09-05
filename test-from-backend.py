#!/usr/bin/env python3
"""
Test update endpoint from backend directory context
"""

import requests
import json
import os
from pathlib import Path

# Change to backend directory to match server context
os.chdir('backend')
print(f"Testing from: {Path.cwd()}")
print(f"Sample file exists: {Path('documents/sample-budget.csv').exists()}")

BASE_URL = "http://localhost:8000"

def test_update_from_backend():
    """Test update endpoint with backend directory context"""
    try:
        data = {
            "path": "documents/sample-budget.csv",
            "operation": "salary_increase", 
            "percentage": 10.0
        }
        
        print(f"Testing update with data: {data}")
        response = requests.post(f"{BASE_URL}/api/update-sheet", json=data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Updated file: {result['data']['output_file']}")
            return True
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_update_from_backend()
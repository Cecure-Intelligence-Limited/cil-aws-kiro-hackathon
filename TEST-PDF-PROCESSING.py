#!/usr/bin/env python3
"""Test PDF processing specifically"""

import requests
import json

def test_pdf_processing():
    """Test PDF processing endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Test document classification
    print("🧪 Testing Document Classification...")
    classify_data = {
        "file_path": "sample-contract.txt"
    }
    
    try:
        response = requests.post(f"{base_url}/api/classify-document", json=classify_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'No message')}")
            print(f"Data: {json.dumps(result.get('data', {}), indent=2)}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "="*50)
    
    # Test OCR data extraction
    print("🧪 Testing OCR Data Extraction...")
    ocr_data = {
        "file_path": "sample-contract.txt",
        "document_type": "contract"
    }
    
    try:
        response = requests.post(f"{base_url}/api/extract-data", json=ocr_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message', 'No message')}")
            print(f"Data: {json.dumps(result.get('data', {}), indent=2)}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_pdf_processing()
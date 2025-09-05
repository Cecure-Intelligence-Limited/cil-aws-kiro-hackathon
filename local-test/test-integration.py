#!/usr/bin/env python3
"""
Integration tests for Aura Desktop Assistant
Tests complete workflows from voice input to file output
"""

import requests
import json
import time
import sys
from pathlib import Path

class AuraIntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
    
    def test_api_health(self):
        """Test API health and availability"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            success = response.status_code == 200
            self.test_results.append(("API Health", success))
            return success
        except Exception as e:
            self.test_results.append(("API Health", False))
            return False
    
    def test_file_operations(self):
        """Test file creation and management"""
        try:
            # Test file creation
            payload = {
                "title": "integration-test-document.txt",
                "content": "This document was created by Aura's integration test suite.\n\nAura demonstrates:\n- Privacy-first AI processing\n- Intelligent natural language understanding\n- Professional desktop integration\n- Extensible architecture\n\nTest completed successfully!"
            }
            response = requests.post(f"{self.base_url}/create_file", json=payload, timeout=10)
            
            if response.status_code == 200:
                # Verify file was created
                expected_path = Path("documents") / "integration-test-document.txt"
                if expected_path.exists():
                    content = expected_path.read_text()
                    if payload["content"] in content:
                        self.test_results.append(("File Operations", True))
                        return True
            
            self.test_results.append(("File Operations", False))
            return False
        except Exception as e:
            self.test_results.append(("File Operations", False))
            return False
    
    def test_spreadsheet_analysis(self):
        """Test spreadsheet analysis capabilities"""
        try:
            # Check if demo spreadsheet exists
            demo_file = Path("documents/sample-budget.csv")
            if not demo_file.exists():
                self.test_results.append(("Spreadsheet Analysis", "SKIPPED - No demo file"))
                return True
            
            payload = {
                "path": str(demo_file),
                "operation": "sum",
                "column": "Amount"
            }
            response = requests.post(f"{self.base_url}/analyze_sheet", json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                # Verify we got a numeric result
                if "result" in result and isinstance(result["result"], (int, float)):
                    self.test_results.append(("Spreadsheet Analysis", True))
                    return True
            
            self.test_results.append(("Spreadsheet Analysis", False))
            return False
        except Exception as e:
            self.test_results.append(("Spreadsheet Analysis", False))
            return False
    
    def test_performance_benchmarks(self):
        """Test performance meets requirements"""
        try:
            # Test API response time
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Performance should be under 500ms for health check
            if response.status_code == 200 and response_time < 500:
                self.test_results.append(("Performance", True))
                return True
            else:
                self.test_results.append(("Performance", False))
                return False
        except Exception as e:
            self.test_results.append(("Performance", False))
            return False
    
    def test_error_handling(self):
        """Test error handling and resilience"""
        try:
            # Test invalid file creation
            payload = {"title": "", "content": ""}
            response = requests.post(f"{self.base_url}/create_file", json=payload, timeout=5)
            
            # Should handle gracefully (either success with default name or proper error)
            if response.status_code in [200, 400, 422]:
                self.test_results.append(("Error Handling", True))
                return True
            else:
                self.test_results.append(("Error Handling", False))
                return False
        except Exception as e:
            self.test_results.append(("Error Handling", False))
            return False
    
    def run_all_tests(self):
        """Execute complete integration test suite"""
        print("🧪 Running Aura Integration Tests")
        print("=" * 40)
        
        tests = [
            ("API Health", self.test_api_health),
            ("File Operations", self.test_file_operations),
            ("Spreadsheet Analysis", self.test_spreadsheet_analysis),
            ("Performance", self.test_performance_benchmarks),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            print(f"Running {test_name} test...")
            test_func()
            time.sleep(1)  # Brief pause between tests
        
        # Print results
        print("\n📊 Integration Test Results:")
        passed = 0
        total = 0
        
        for test_name, result in self.test_results:
            if result == True:
                print(f"✅ {test_name}")
                passed += 1
                total += 1
            elif result == False:
                print(f"❌ {test_name}")
                total += 1
            else:
                print(f"⚠️  {test_name}: {result}")
        
        print(f"\n🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All integration tests passed! Aura is ready for demo.")
            return True
        else:
            print("⚠️  Some tests failed. Check backend logs for details.")
            return False

def main():
    """Main test execution"""
    tester = AuraIntegrationTester()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
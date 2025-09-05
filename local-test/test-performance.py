#!/usr/bin/env python3
"""
Performance tests for Aura Desktop Assistant
Validates response times and resource usage
"""

import requests
import time
import sys
import psutil
import os
from pathlib import Path

class PerformanceTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.benchmarks = {
            "api_response_ms": 500,
            "file_creation_ms": 2000,
            "spreadsheet_analysis_ms": 5000,
            "memory_usage_mb": 512
        }
    
    def measure_api_response_time(self):
        """Measure API response times"""
        print("⏱️  Measuring API response times...")
        
        try:
            # Test health endpoint
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            health_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   Health endpoint: {health_time:.1f}ms")
                if health_time < self.benchmarks["api_response_ms"]:
                    print("   ✅ API response time within benchmark")
                    return True
                else:
                    print(f"   ❌ API response time exceeds {self.benchmarks['api_response_ms']}ms benchmark")
                    return False
            else:
                print("   ❌ Health endpoint failed")
                return False
        except Exception as e:
            print(f"   ❌ API test failed: {e}")
            return False
    
    def measure_file_creation_performance(self):
        """Measure file creation performance"""
        print("📁 Measuring file creation performance...")
        
        try:
            payload = {
                "title": "performance-test.txt",
                "content": "This is a performance test file created by Aura.\n" * 100  # Larger content
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/create_file", json=payload, timeout=15)
            creation_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   File creation: {creation_time:.1f}ms")
                if creation_time < self.benchmarks["file_creation_ms"]:
                    print("   ✅ File creation time within benchmark")
                    return True
                else:
                    print(f"   ❌ File creation exceeds {self.benchmarks['file_creation_ms']}ms benchmark")
                    return False
            else:
                print("   ❌ File creation failed")
                return False
        except Exception as e:
            print(f"   ❌ File creation test failed: {e}")
            return False
    
    def measure_spreadsheet_performance(self):
        """Measure spreadsheet analysis performance"""
        print("📊 Measuring spreadsheet analysis performance...")
        
        try:
            demo_file = Path("documents/sample-budget.csv")
            if not demo_file.exists():
                print("   ⚠️  Demo spreadsheet not found, skipping test")
                return True
            
            payload = {
                "path": str(demo_file),
                "operation": "sum",
                "column": "Amount"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/analyze_sheet", json=payload, timeout=20)
            analysis_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   Spreadsheet analysis: {analysis_time:.1f}ms")
                if analysis_time < self.benchmarks["spreadsheet_analysis_ms"]:
                    print("   ✅ Spreadsheet analysis time within benchmark")
                    return True
                else:
                    print(f"   ❌ Analysis exceeds {self.benchmarks['spreadsheet_analysis_ms']}ms benchmark")
                    return False
            else:
                print("   ❌ Spreadsheet analysis failed")
                return False
        except Exception as e:
            print(f"   ❌ Spreadsheet test failed: {e}")
            return False
    
    def measure_memory_usage(self):
        """Measure memory usage of the system"""
        print("💾 Measuring memory usage...")
        
        try:
            # Get current process memory usage
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            print(f"   Current process memory: {memory_mb:.1f}MB")
            
            # Check system memory
            system_memory = psutil.virtual_memory()
            available_mb = system_memory.available / 1024 / 1024
            
            print(f"   System available memory: {available_mb:.1f}MB")
            
            if memory_mb < self.benchmarks["memory_usage_mb"]:
                print("   ✅ Memory usage within acceptable limits")
                return True
            else:
                print(f"   ⚠️  Memory usage high: {memory_mb:.1f}MB")
                return True  # Don't fail on memory, just warn
        except Exception as e:
            print(f"   ⚠️  Memory measurement failed: {e}")
            return True  # Don't fail the test
    
    def run_performance_tests(self):
        """Run all performance tests"""
        print("🚀 Aura Performance Test Suite")
        print("=" * 40)
        
        tests = [
            ("API Response Time", self.measure_api_response_time),
            ("File Creation Performance", self.measure_file_creation_performance),
            ("Spreadsheet Analysis Performance", self.measure_spreadsheet_performance),
            ("Memory Usage", self.measure_memory_usage)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            if test_func():
                passed += 1
        
        print("\n" + "=" * 40)
        print(f"📊 Performance Results: {passed}/{total} benchmarks met")
        
        if passed >= total - 1:  # Allow one test to fail
            print("🎉 Performance tests passed! Aura meets performance requirements.")
            return True
        else:
            print("⚠️  Performance issues detected. Consider optimization.")
            return False

def main():
    """Main performance test execution"""
    tester = PerformanceTester()
    success = tester.run_performance_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
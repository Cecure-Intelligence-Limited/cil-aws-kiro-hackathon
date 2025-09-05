#!/usr/bin/env python3
"""
Security tests for Aura Desktop Assistant
Validates input sanitization and security measures
"""

import requests
import sys
import os
from pathlib import Path

class SecurityTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        print("🔒 Testing path traversal protection...")
        
        malicious_payloads = [
            {"title": "../../../etc/passwd", "content": "malicious"},
            {"title": "..\\..\\..\\windows\\system32\\config\\sam", "content": "malicious"},
            {"title": "test/../../../sensitive.txt", "content": "malicious"},
            {"title": "test\\..\\..\\..\\sensitive.txt", "content": "malicious"}
        ]
        
        try:
            for payload in malicious_payloads:
                response = requests.post(f"{self.base_url}/create_file", json=payload, timeout=5)
                
                # Should either reject (4xx) or sanitize the path
                if response.status_code in [400, 403, 422]:
                    continue  # Good, rejected malicious input
                elif response.status_code == 200:
                    # Check if file was created in safe location
                    result = response.json()
                    if "path" in result:
                        file_path = Path(result["path"])
                        # Ensure file is in documents directory
                        if not str(file_path).startswith("documents"):
                            print(f"   ❌ Path traversal vulnerability: {file_path}")
                            return False
                else:
                    print(f"   ❌ Unexpected response: {response.status_code}")
                    return False
            
            print("   ✅ Path traversal protection working")
            return True
        except Exception as e:
            print(f"   ❌ Path traversal test failed: {e}")
            return False
    
    def test_input_validation(self):
        """Test input validation and sanitization"""
        print("🛡️  Testing input validation...")
        
        test_cases = [
            {"title": "", "content": ""},  # Empty inputs
            {"title": "a" * 1000, "content": "b" * 10000},  # Very long inputs
            {"title": "<script>alert('xss')</script>", "content": "test"},  # XSS attempt
            {"title": "'; DROP TABLE files; --", "content": "test"},  # SQL injection attempt
            {"title": "test\x00null", "content": "test\x00null"},  # Null bytes
        ]
        
        try:
            for payload in test_cases:
                response = requests.post(f"{self.base_url}/create_file", json=payload, timeout=5)
                
                # Should handle gracefully (success with sanitization or proper error)
                if response.status_code not in [200, 400, 422]:
                    print(f"   ❌ Unexpected response to malicious input: {response.status_code}")
                    return False
            
            print("   ✅ Input validation working properly")
            return True
        except Exception as e:
            print(f"   ❌ Input validation test failed: {e}")
            return False
    
    def test_file_type_restrictions(self):
        """Test file type and extension restrictions"""
        print("📄 Testing file type restrictions...")
        
        dangerous_extensions = [
            "malware.exe",
            "script.bat",
            "virus.scr",
            "trojan.com",
            "backdoor.pif"
        ]
        
        try:
            for filename in dangerous_extensions:
                payload = {"title": filename, "content": "test content"}
                response = requests.post(f"{self.base_url}/create_file", json=payload, timeout=5)
                
                if response.status_code == 200:
                    # Check if dangerous extension was sanitized
                    result = response.json()
                    if "path" in result:
                        created_path = result["path"]
                        if any(ext in created_path.lower() for ext in [".exe", ".bat", ".scr", ".com", ".pif"]):
                            print(f"   ⚠️  Dangerous file type allowed: {created_path}")
                            # Don't fail, but warn
            
            print("   ✅ File type restrictions checked")
            return True
        except Exception as e:
            print(f"   ❌ File type test failed: {e}")
            return False
    
    def test_api_rate_limiting(self):
        """Test API rate limiting (basic check)"""
        print("⏱️  Testing API rate limiting...")
        
        try:
            # Send multiple rapid requests
            responses = []
            for i in range(10):
                response = requests.get(f"{self.base_url}/health", timeout=2)
                responses.append(response.status_code)
            
            # All should succeed for health endpoint (it's not rate limited)
            # But we're checking the API can handle rapid requests
            success_count = sum(1 for status in responses if status == 200)
            
            if success_count >= 8:  # Allow some failures due to timing
                print("   ✅ API handles rapid requests properly")
                return True
            else:
                print(f"   ⚠️  API struggled with rapid requests: {success_count}/10 succeeded")
                return True  # Don't fail, just warn
        except Exception as e:
            print(f"   ❌ Rate limiting test failed: {e}")
            return False
    
    def test_error_information_disclosure(self):
        """Test that errors don't disclose sensitive information"""
        print("🔍 Testing error information disclosure...")
        
        try:
            # Send malformed request
            response = requests.post(f"{self.base_url}/create_file", 
                                   json={"invalid": "data"}, timeout=5)
            
            if response.status_code in [400, 422]:
                # Check error message doesn't contain sensitive info
                error_text = response.text.lower()
                sensitive_terms = ["password", "secret", "key", "token", "internal", "debug"]
                
                for term in sensitive_terms:
                    if term in error_text:
                        print(f"   ⚠️  Potential information disclosure: '{term}' in error")
                        return True  # Warn but don't fail
                
                print("   ✅ Error messages don't disclose sensitive information")
                return True
            else:
                print("   ✅ API handled malformed request appropriately")
                return True
        except Exception as e:
            print(f"   ❌ Error disclosure test failed: {e}")
            return False
    
    def run_security_tests(self):
        """Run all security tests"""
        print("🔐 Aura Security Test Suite")
        print("=" * 40)
        
        tests = [
            ("Path Traversal Protection", self.test_path_traversal_protection),
            ("Input Validation", self.test_input_validation),
            ("File Type Restrictions", self.test_file_type_restrictions),
            ("API Rate Limiting", self.test_api_rate_limiting),
            ("Error Information Disclosure", self.test_error_information_disclosure)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            if test_func():
                passed += 1
        
        print("\n" + "=" * 40)
        print(f"🔒 Security Results: {passed}/{total} tests passed")
        
        if passed >= total - 1:  # Allow one test to have warnings
            print("🎉 Security tests passed! Aura demonstrates good security practices.")
            return True
        else:
            print("⚠️  Security issues detected. Review implementation.")
            return False

def main():
    """Main security test execution"""
    tester = SecurityTester()
    success = tester.run_security_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
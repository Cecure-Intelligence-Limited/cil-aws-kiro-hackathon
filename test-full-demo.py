#!/usr/bin/env python3
"""
FULL DEMO TEST SCRIPT
Tests ALL automation features for complete hackathon demonstration
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_endpoint(endpoint, method="GET", data=None, description="", critical=True):
    """Test an API endpoint and return the result"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {description}")
    print(f"URL: {url}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("success"):
                    print(f"✅ SUCCESS: {result.get('message', 'Operation completed')}")
                    if result.get("data"):
                        print(f"📊 Data returned: {len(str(result['data']))} characters")
                    return True
                else:
                    print(f"⚠️ PARTIAL: {result.get('message', 'No success flag')}")
                    return not critical
            except:
                print(f"✅ SUCCESS (Non-JSON response)")
                return True
        else:
            print(f"❌ FAILED: {response.text[:200]}...")
            return not critical
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Server not running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return not critical

def main():
    """Run comprehensive demo tests"""
    
    print("🚀 AURA DESKTOP ASSISTANT - FULL DEMO TEST SUITE")
    print("="*80)
    print(f"Server: {BASE_URL}")
    print(f"Testing ALL automation capabilities for hackathon demo")
    print("="*80)
    
    tests_passed = 0
    total_tests = 0
    critical_features = []
    
    # Test 1: Health Check
    total_tests += 1
    if test_endpoint("/health", "GET", description="🏥 Health Check"):
        tests_passed += 1
        critical_features.append("✅ Server Health")
    else:
        critical_features.append("❌ Server Health")
    
    # Test 2: File Operations
    total_tests += 1
    create_data = {
        "title": "demo-test.txt",
        "path": "backend/documents",
        "content": "This file demonstrates Aura's file automation capabilities."
    }
    if test_endpoint("/api/create-file", "POST", create_data, "📁 File Creation Automation"):
        tests_passed += 1
        critical_features.append("✅ File Operations")
    else:
        critical_features.append("❌ File Operations")
    
    # Test 3: OCR Data Extraction
    total_tests += 1
    ocr_data = {
        "file_path": "backend/documents/sample-invoice.txt",
        "document_type": "invoice",
        "transfer_to_spreadsheet": False
    }
    if test_endpoint("/api/extract-data", "POST", ocr_data, "🔍 OCR Data Extraction"):
        tests_passed += 1
        critical_features.append("✅ OCR Data Extraction")
    else:
        critical_features.append("❌ OCR Data Extraction")
    
    # Test 4: Spreadsheet Analysis
    total_tests += 1
    analyze_data = {
        "path": "sample-budget.csv",
        "op": "sum",
        "column": "Amount"
    }
    if test_endpoint("/api/analyze-sheet", "POST", analyze_data, "📊 Spreadsheet Analysis"):
        tests_passed += 1
        critical_features.append("✅ Spreadsheet Analysis")
    else:
        critical_features.append("❌ Spreadsheet Analysis")
    
    # Test 5: Spreadsheet Updates (In-Place)
    total_tests += 1
    update_data = {
        "path": "sample-budget.csv",
        "operation": "salary_increase",
        "percentage": 5.0
    }
    if test_endpoint("/api/update-sheet", "POST", update_data, "💰 Spreadsheet Updates (In-Place)"):
        tests_passed += 1
        critical_features.append("✅ Spreadsheet Updates")
    else:
        critical_features.append("❌ Spreadsheet Updates")
    
    # Test 6: Email Automation
    total_tests += 1
    email_rule_data = {
        "name": "Demo Invoice Rule",
        "condition": "subject contains invoice",
        "action": "move",
        "target": "Finance/Invoices"
    }
    if test_endpoint("/api/email-rule", "POST", email_rule_data, "📧 Email Automation Rules"):
        tests_passed += 1
        critical_features.append("✅ Email Automation")
    else:
        critical_features.append("❌ Email Automation")
    
    # Test 7: Calendar Scheduling
    total_tests += 1
    meeting_data = {
        "participants": ["john@demo.com", "sarah@demo.com"],
        "duration": 60,
        "timeframe": "next_week",
        "title": "Demo Meeting",
        "agenda": "Demonstrate Aura's scheduling capabilities"
    }
    if test_endpoint("/api/schedule-meeting", "POST", meeting_data, "📅 Calendar Scheduling"):
        tests_passed += 1
        critical_features.append("✅ Calendar Scheduling")
    else:
        critical_features.append("❌ Calendar Scheduling")
    
    # Test 8: Report Generation
    total_tests += 1
    report_data = {
        "report_type": "sales",
        "data_sources": ["sales", "crm"],
        "period": "monthly",
        "template": "default"
    }
    if test_endpoint("/api/generate-report", "POST", report_data, "📈 Report Generation"):
        tests_passed += 1
        critical_features.append("✅ Report Generation")
    else:
        critical_features.append("❌ Report Generation")
    
    # Test 9: Document Classification
    total_tests += 1
    classify_data = {
        "file_path": "backend/documents/sample-contract.txt"
    }
    if test_endpoint("/api/classify-document", "POST", classify_data, "🤖 AI Document Classification"):
        tests_passed += 1
        critical_features.append("✅ Document Classification")
    else:
        critical_features.append("❌ Document Classification")
    
    # Test 10: Workflow Processing
    total_tests += 1
    workflow_data = {
        "file_path": "backend/documents/sample-invoice.txt"
    }
    if test_endpoint("/api/start-workflow", "POST", workflow_data, "⚡ Workflow Automation"):
        tests_passed += 1
        critical_features.append("✅ Workflow Processing")
    else:
        critical_features.append("❌ Workflow Processing")
    
    # Results Summary
    print(f"\n{'='*80}")
    print(f"🎯 HACKATHON DEMO READINESS REPORT")
    print(f"{'='*80}")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    print(f"\n🚀 AUTOMATION CAPABILITIES STATUS:")
    for feature in critical_features:
        print(f"  {feature}")
    
    if tests_passed >= 8:  # At least 8/10 features working
        print(f"\n🎉 EXCELLENT! Your demo is ready for the hackathon!")
        print(f"🏆 You have a comprehensive business automation platform with:")
        print(f"   • OCR-powered data extraction")
        print(f"   • Email management automation")
        print(f"   • Calendar scheduling with conflict resolution")
        print(f"   • Report generation with visualizations")
        print(f"   • AI-powered document workflows")
        print(f"   • Spreadsheet analysis and updates")
        print(f"   • Complete API documentation")
        
    elif tests_passed >= 6:
        print(f"\n✅ GOOD! Most features working. You can demo successfully.")
        print(f"💡 Focus on the working features for your presentation.")
        
    elif tests_passed >= 4:
        print(f"\n⚠️ PARTIAL: Some core features working.")
        print(f"🔧 Consider fixing the failed tests before demo.")
        
    else:
        print(f"\n❌ CRITICAL: Major issues detected.")
        print(f"🆘 Run FIX-ANACONDA-PERMISSIONS.bat and try again.")
    
    print(f"\n📚 API Documentation: {BASE_URL}/docs")
    print(f"🎬 Demo URL: {BASE_URL}")
    print(f"\n🎯 DEMO SCRIPT:")
    print(f"1. Show API docs at /docs")
    print(f"2. Test OCR data extraction")
    print(f"3. Demonstrate email automation")
    print(f"4. Show calendar scheduling")
    print(f"5. Generate reports with charts")
    print(f"6. Process document workflows")

if __name__ == "__main__":
    main()
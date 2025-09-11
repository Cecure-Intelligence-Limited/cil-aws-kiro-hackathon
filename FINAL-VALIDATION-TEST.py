#!/usr/bin/env python3
"""
FINAL VALIDATION TEST - Complete System Check
Ensures everything is perfect for judges demo
"""

import requests
import json
import time
import sys
from pathlib import Path

def print_status(message, status="info"):
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "🔍"}
    print(f"{icons.get(status, '🔍')} {message}")

def test_complete_system():
    print("🏆 FINAL VALIDATION TEST - HACKATHON DEMO")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 8
    
    # Test 1: Backend Health
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print_status("Backend health check", "success")
            tests_passed += 1
        else:
            print_status(f"Backend health failed: {response.status_code}", "error")
    except:
        print_status("Backend not responding - check BACKEND-DEMO window", "error")
    
    # Test 2: Frontend Accessibility
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print_status("Frontend web app accessible", "success")
            tests_passed += 1
        else:
            print_status("Frontend not accessible", "error")
    except:
        print_status("Frontend not responding - check FRONTEND-DEMO window", "error")
    
    # Test 3: API Documentation
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print_status("API documentation accessible", "success")
            tests_passed += 1
        else:
            print_status("API docs not accessible", "error")
    except:
        print_status("API docs not responding", "error")
    
    # Test 4: File Creation (Payroll Demo)
    try:
        payroll_data = {
            "title": "validation-payroll.xlsx",
            "content": "Employee_ID,Name,Salary,Department\nEMP001,John Smith,8500,Engineering\nEMP002,Sarah Johnson,7200,Marketing",
            "path": "documents"
        }
        response = requests.post("http://localhost:8000/api/create-file", json=payroll_data, timeout=10)
        if response.status_code == 200:
            print_status("Payroll file creation working", "success")
            tests_passed += 1
        else:
            print_status(f"File creation failed: {response.status_code}", "error")
    except Exception as e:
        print_status(f"File creation error: {e}", "error")
    
    # Test 5: Spreadsheet Analysis
    try:
        analysis_data = {
            "path": "sample-budget.csv",
            "op": "sum",
            "column": "Total_Monthly"
        }
        response = requests.post("http://localhost:8000/api/analyze-sheet", json=analysis_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print_status(f"Spreadsheet analysis working - Total: ${result['result']:,.0f}", "success")
            tests_passed += 1
        else:
            print_status(f"Analysis failed: {response.status_code}", "error")
    except Exception as e:
        print_status(f"Analysis error: {e}", "error")
    
    # Test 6: Spreadsheet Update
    try:
        update_data = {
            "path": "sample-budget.csv",
            "operation": "salary_increase",
            "percentage": 5.0
        }
        response = requests.post("http://localhost:8000/api/update-sheet", json=update_data, timeout=10)
        if response.status_code == 200:
            print_status("Spreadsheet update working", "success")
            tests_passed += 1
        else:
            print_status(f"Update failed: {response.status_code}", "error")
    except Exception as e:
        print_status(f"Update error: {e}", "error")
    
    # Test 7: Email Automation
    try:
        email_data = {
            "name": "Demo Rule",
            "condition": "subject contains invoice",
            "action": "move",
            "target": "invoices"
        }
        response = requests.post("http://localhost:8000/api/email-rule", json=email_data, timeout=10)
        if response.status_code == 200:
            print_status("Email automation working", "success")
            tests_passed += 1
        else:
            print_status(f"Email automation failed: {response.status_code}", "error")
    except Exception as e:
        print_status(f"Email automation error: {e}", "error")
    
    # Test 8: Report Generation
    try:
        report_data = {
            "report_type": "financial",
            "data_sources": ["sample-budget.csv"],
            "period": "monthly"
        }
        response = requests.post("http://localhost:8000/api/generate-report", json=report_data, timeout=10)
        if response.status_code == 200:
            print_status("Report generation working", "success")
            tests_passed += 1
        else:
            print_status(f"Report generation failed: {response.status_code}", "error")
    except Exception as e:
        print_status(f"Report generation error: {e}", "error")
    
    # Results Summary
    print("\n" + "=" * 50)
    print("🎯 FINAL VALIDATION RESULTS")
    print("=" * 50)
    
    success_rate = (tests_passed / total_tests) * 100
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if tests_passed == total_tests:
        print_status("🏆 PERFECT! SYSTEM IS 100% READY FOR JUDGES!", "success")
        print("\n🎬 DEMO CONFIDENCE LEVEL: MAXIMUM")
        print("🎯 ALL SYSTEMS GO - YOU'RE READY TO WIN!")
        
    elif tests_passed >= 6:
        print_status("🎉 EXCELLENT! System is demo-ready with minor issues", "success")
        print("🎯 DEMO CONFIDENCE LEVEL: HIGH")
        print("💡 Focus on working features during demo")
        
    elif tests_passed >= 4:
        print_status("⚠️ GOOD! Core features working, some issues detected", "warning")
        print("🎯 DEMO CONFIDENCE LEVEL: MODERATE")
        print("💡 Use backup demo strategies")
        
    else:
        print_status("❌ CRITICAL ISSUES! System needs attention", "error")
        print("🎯 DEMO CONFIDENCE LEVEL: LOW")
        print("💡 Run JUDGES-DEMO-COMPLETE.bat again")
    
    print(f"\n📋 DEMO URLS:")
    print(f"🌐 Main App: http://localhost:5173")
    print(f"📡 Backend: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    
    print(f"\n🎤 DEMO COMMANDS:")
    print(f"• 'Create payroll file' → Excel creation")
    print(f"• 'Calculate total salary' → Analysis")
    print(f"• 'Update salary increase' → Modifications")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = test_complete_system()
    
    if success:
        print(f"\n🏆 SYSTEM VALIDATION COMPLETE - GO WIN THAT HACKATHON! 🏆")
    else:
        print(f"\n🔧 Some issues detected - but you still have a strong demo!")
        print(f"💡 Focus on the working features and use backup strategies")
    
    sys.exit(0 if success else 1)
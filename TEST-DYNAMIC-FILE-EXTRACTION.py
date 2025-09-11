#!/usr/bin/env python3
"""
TEST DYNAMIC FILE EXTRACTION - Verify the enhanced file extraction from natural language
"""

import requests
import json
import sys

def test_dynamic_commands():
    print("🧪 TESTING DYNAMIC FILE EXTRACTION")
    print("=" * 50)
    
    # Test various natural language commands
    test_commands = [
        # Direct file references
        ("Analyze global-sales.csv", "global-sales.csv"),
        ("Read fortune500-payroll.csv", "fortune500-payroll.csv"),
        ("Open ai-projects.csv", "ai-projects.csv"),
        
        # Natural language without extensions
        ("Do an insightful analysis on the global-sales file", "global-sales.csv"),
        ("Analyze the fortune500 payroll data", "fortune500-payroll.csv"),
        ("Show me the AI projects information", "ai-projects.csv"),
        ("Calculate totals from the sample budget", "sample-budget.csv"),
        
        # Keyword-based matching
        ("Show me global sales performance", "global-sales.csv"),
        ("Analyze employee compensation data", "fortune500-payroll.csv"),
        ("Review the AI project portfolio", "ai-projects.csv"),
        ("Calculate budget totals", "sample-budget.csv"),
        
        # Complex natural language
        ("I want to see revenue breakdown by region", "global-sales.csv"),
        ("Show executive compensation analysis", "fortune500-payroll.csv"),
        ("Display artificial intelligence project ROI", "ai-projects.csv"),
    ]
    
    success_count = 0
    
    for i, (command, expected_file) in enumerate(test_commands, 1):
        print(f"\n🔍 Test {i}: {command}")
        print(f"Expected file: {expected_file}")
        print("-" * 60)
        
        try:
            response = requests.post(
                "http://localhost:8000/api/smart-spreadsheet",
                json={"command": command},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                file_analyzed = data.get('file_analyzed', '')
                
                # Extract just the filename from the full path
                actual_file = file_analyzed.split('\\')[-1] if '\\' in file_analyzed else file_analyzed.split('/')[-1]
                
                if expected_file.lower() in actual_file.lower():
                    print(f"✅ SUCCESS! Correctly identified: {actual_file}")
                    success_count += 1
                    
                    # Show some insights
                    if 'insights' in data:
                        print("💡 Sample insights:")
                        for insight in data['insights'][:2]:
                            print(f"  • {insight}")
                else:
                    print(f"❌ WRONG FILE! Expected: {expected_file}, Got: {actual_file}")
                
            else:
                error_data = response.json()
                print(f"❌ ERROR ({response.status_code}): {error_data}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    print(f"\n📊 RESULTS: {success_count}/{len(test_commands)} tests passed")
    return success_count == len(test_commands)

def main():
    print("🚀 TESTING ENHANCED DYNAMIC FILE EXTRACTION")
    print("=" * 60)
    print("This test verifies that the system can intelligently extract")
    print("file names from natural language commands without hardcoding.")
    print()
    
    success = test_dynamic_commands()
    
    if success:
        print("\n🎉 ALL DYNAMIC EXTRACTION TESTS PASSED!")
        print("🎯 The system now:")
        print("  • Extracts file names from natural language")
        print("  • Handles various command formats")
        print("  • Maps keywords to appropriate files")
        print("  • Works with complex natural language")
        print("\n🏆 READY FOR TRULY DYNAMIC DEMO!")
    else:
        print("\n⚠️ Some tests failed")
        print("🔧 The file extraction logic needs refinement")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
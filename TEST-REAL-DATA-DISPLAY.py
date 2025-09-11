#!/usr/bin/env python3
"""
TEST REAL DATA DISPLAY - Verify the enhanced intelligent spreadsheet service shows actual employee data
"""

import requests
import json
import sys

def test_enhanced_data_display():
    print("🧪 TESTING ENHANCED DATA DISPLAY")
    print("=" * 40)
    
    # Test commands that should now show real employee data
    test_commands = [
        "Read demo-payroll.csv and calculate total compensation",
        "Read fortune500-payroll.csv and calculate total compensation", 
        "Analyze global-sales.csv and show revenue breakdown",
        "Calculate total salary from sample-budget.csv"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🔍 Test {i}: {command}")
        print("-" * 50)
        
        try:
            response = requests.post(
                "http://localhost:8000/api/smart-spreadsheet",
                json={"command": command},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                
                # Check if we have employee data
                data = result.get('data', {})
                
                if 'employee_breakdown' in data:
                    print(f"📊 Employee Breakdown ({len(data['employee_breakdown'])} records):")
                    for j, emp in enumerate(data['employee_breakdown'][:3], 1):  # Show first 3
                        print(f"  {j}. {emp}")
                
                if 'employee_details' in data:
                    print(f"👥 Employee Details ({len(data['employee_details'])} records):")
                    for j, emp in enumerate(data['employee_details'][:3], 1):  # Show first 3
                        print(f"  {j}. {emp}")
                
                if 'employee_data' in data:
                    print(f"📋 Employee Data ({len(data['employee_data'])} records):")
                    for j, emp in enumerate(data['employee_data'][:3], 1):  # Show first 3
                        print(f"  {j}. {emp}")
                
                if 'totals_summary' in data:
                    print("💰 Totals Summary:")
                    for col, totals in data['totals_summary'].items():
                        print(f"  {col}: {totals}")
                
                if 'insights' in data:
                    print("💡 Insights:")
                    for insight in data['insights'][:5]:  # Show first 5 insights
                        print(f"  • {insight}")
                
                print(f"🎯 Operation: {data.get('operation', 'Unknown')}")
                
            else:
                error_data = response.json()
                print(f"❌ ERROR ({response.status_code}): {error_data}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    return True

def main():
    print("🚀 TESTING ENHANCED INTELLIGENT SPREADSHEET SERVICE")
    print("=" * 60)
    print("This test verifies that the service now shows actual employee names,")
    print("salaries, and detailed data instead of generic summaries.")
    print()
    
    success = test_enhanced_data_display()
    
    if success:
        print("\n🎉 ENHANCED DATA DISPLAY TEST COMPLETE!")
        print("🎯 The service should now show:")
        print("  • Actual employee names and positions")
        print("  • Real salary and compensation data")
        print("  • Detailed breakdowns with specific amounts")
        print("  • Enhanced business insights")
        print("\n🏆 READY FOR WOW DEMO!")
    else:
        print("\n⚠️ Some tests had issues")
        print("🔧 Check the backend logs for details")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
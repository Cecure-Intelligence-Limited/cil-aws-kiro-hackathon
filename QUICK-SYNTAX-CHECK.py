#!/usr/bin/env python3
"""
QUICK SYNTAX CHECK - Verify backend has no syntax errors
"""

import ast
import sys
from pathlib import Path

def check_syntax(file_path):
    """Check if Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    print("🔍 QUICK SYNTAX CHECK")
    print("=" * 30)
    
    # Check main.py
    main_py = Path("backend/main.py")
    if main_py.exists():
        is_valid, error = check_syntax(main_py)
        if is_valid:
            print("✅ backend/main.py - Syntax OK")
        else:
            print(f"❌ backend/main.py - {error}")
            return False
    else:
        print("❌ backend/main.py not found")
        return False
    
    # Check intelligent spreadsheet service
    intel_service = Path("backend/services/intelligent_spreadsheet_service.py")
    if intel_service.exists():
        is_valid, error = check_syntax(intel_service)
        if is_valid:
            print("✅ intelligent_spreadsheet_service.py - Syntax OK")
        else:
            print(f"❌ intelligent_spreadsheet_service.py - {error}")
            return False
    
    print("\n🎉 ALL SYNTAX CHECKS PASSED!")
    print("🚀 Backend is ready to start!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
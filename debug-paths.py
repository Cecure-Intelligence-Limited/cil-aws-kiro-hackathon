#!/usr/bin/env python3
"""
Debug script to check file paths
"""

from pathlib import Path
import os

def check_paths():
    print("🔍 Debugging file paths...")
    print(f"Current working directory: {Path.cwd()}")
    print()
    
    # Test paths to check
    test_paths = [
        "documents/sample-budget.csv",
        "backend/documents/sample-budget.csv", 
        "sample-budget.csv",
        Path("documents") / "sample-budget.csv",
        Path("backend/documents") / "sample-budget.csv",
        Path.cwd() / "documents" / "sample-budget.csv",
        Path.cwd() / "backend" / "documents" / "sample-budget.csv",
    ]
    
    print("📁 Checking file existence:")
    for path in test_paths:
        path_obj = Path(path)
        exists = path_obj.exists()
        print(f"  {'✅' if exists else '❌'} {path} -> {path_obj.resolve() if exists else 'NOT FOUND'}")
    
    print()
    print("📂 Directory contents:")
    
    # Check documents directory
    docs_path = Path("documents")
    if docs_path.exists():
        print(f"  documents/ contents:")
        for item in docs_path.iterdir():
            print(f"    - {item.name}")
    else:
        print("  documents/ does not exist")
    
    # Check backend/documents directory  
    backend_docs_path = Path("backend/documents")
    if backend_docs_path.exists():
        print(f"  backend/documents/ contents:")
        for item in backend_docs_path.iterdir():
            print(f"    - {item.name}")
    else:
        print("  backend/documents/ does not exist")

if __name__ == "__main__":
    check_paths()
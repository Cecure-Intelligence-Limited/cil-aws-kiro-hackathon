#!/usr/bin/env python3
"""
Verify repository cleanup and structure for competition
"""

import os
from pathlib import Path

def check_repository_structure():
    """Verify the repository has the correct professional structure"""
    print("🔍 Verifying Repository Structure")
    print("=" * 40)
    
    # Required directories
    required_dirs = [
        "src",
        "backend", 
        "src-tauri",
        "local-test",
        ".github"
    ]
    
    # Required files
    required_files = [
        "README.md",
        "package.json",
        "tsconfig.json",
        "vite.config.ts",
        "tailwind.config.js",
        ".env.template",
        "CLOUD-TESTING.md",
        "COMPETITION-READY.md"
    ]
    
    # Files that should be removed
    unwanted_files = [
        "CHECK-BUILD-TOOLS.bat",
        "FIX-AND-DEMO.bat", 
        "RUN-DEMO.bat",
        "QUICK-DEMO.bat",
        "BACKEND-DEMO.html",
        "test.html",
        "test-connection.html",
        "TEST_EVERYTHING.md",
        "QUICK_START.md",
        "DEMO.md",
        "RUNBOOK.md"
    ]
    
    # Directories that should be removed
    unwanted_dirs = [
        "local-setup",
        ".kiro",
        "node_modules",
        "__pycache__",
        "dist"
    ]
    
    issues = []
    
    # Check required directories
    print("\n📁 Checking Required Directories:")
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - MISSING")
            issues.append(f"Missing directory: {dir_name}")
    
    # Check required files
    print("\n📄 Checking Required Files:")
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - MISSING")
            issues.append(f"Missing file: {file_name}")
    
    # Check unwanted files are removed
    print("\n🗑️  Checking Unwanted Files Removed:")
    for file_name in unwanted_files:
        if Path(file_name).exists():
            print(f"❌ {file_name} - SHOULD BE REMOVED")
            issues.append(f"Unwanted file still exists: {file_name}")
        else:
            print(f"✅ {file_name} - Removed")
    
    # Check unwanted directories are removed
    print("\n📂 Checking Unwanted Directories Removed:")
    for dir_name in unwanted_dirs:
        if Path(dir_name).exists():
            print(f"❌ {dir_name}/ - SHOULD BE REMOVED")
            issues.append(f"Unwanted directory still exists: {dir_name}")
        else:
            print(f"✅ {dir_name}/ - Removed")
    
    return issues

def check_local_test_structure():
    """Verify local-test directory has all required files"""
    print("\n🧪 Checking local-test/ Structure:")
    
    local_test_files = [
        "README.md",
        "setup-and-test.bat",
        "setup-and-test.sh", 
        "run-all-tests.bat",
        "run-all-tests.sh",
        "check-prerequisites.bat",
        "check-prerequisites.sh",
        "create-demo-data.py",
        "test-backend.py",
        "test-integration.py",
        "test-performance.py",
        "test-security.py"
    ]
    
    issues = []
    
    for file_name in local_test_files:
        file_path = Path("local-test") / file_name
        if file_path.exists():
            print(f"✅ local-test/{file_name}")
        else:
            print(f"❌ local-test/{file_name} - MISSING")
            issues.append(f"Missing local-test file: {file_name}")
    
    return issues

def check_file_sizes():
    """Check for any unusually large files that might need cleanup"""
    print("\n📊 Checking File Sizes:")
    
    large_files = []
    
    for file_path in Path(".").rglob("*"):
        if file_path.is_file():
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > 10:  # Files larger than 10MB
                    large_files.append((str(file_path), size_mb))
            except:
                pass
    
    if large_files:
        print("⚠️  Large files found (>10MB):")
        for file_path, size_mb in large_files:
            print(f"   📄 {file_path}: {size_mb:.1f}MB")
    else:
        print("✅ No unusually large files found")
    
    return large_files

def main():
    """Run complete repository verification"""
    print("🏆 Aura Repository Structure Verification")
    print("=" * 50)
    
    # Check repository structure
    structure_issues = check_repository_structure()
    
    # Check local-test structure
    local_test_issues = check_local_test_structure()
    
    # Check file sizes
    large_files = check_file_sizes()
    
    # Summary
    all_issues = structure_issues + local_test_issues
    
    print("\n" + "=" * 50)
    print("📋 Verification Summary")
    print("=" * 50)
    
    if not all_issues:
        print("🎉 Repository structure is PERFECT!")
        print("✅ All required files and directories present")
        print("✅ All unwanted files removed")
        print("✅ Professional structure ready for competition")
        
        if large_files:
            print(f"\n⚠️  Note: {len(large_files)} large files found (review if needed)")
        
        print("\n🚀 Ready for competition submission!")
        return True
    else:
        print(f"❌ Found {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"   • {issue}")
        
        print("\n🔧 Run cleanup-repo.bat to fix these issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
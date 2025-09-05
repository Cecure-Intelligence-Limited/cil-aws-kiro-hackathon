@echo off
echo ========================================
echo Cleaning Up Repository for Competition
echo ========================================
echo.

echo Removing temporary and duplicate files...

:: Remove all temporary demo/test scripts from root
if exist "CHECK-BUILD-TOOLS.bat" del "CHECK-BUILD-TOOLS.bat"
if exist "INSTALL-BUILD-TOOLS.bat" del "INSTALL-BUILD-TOOLS.bat"
if exist "FIX-AND-DEMO.bat" del "FIX-AND-DEMO.bat"
if exist "RUN-DEMO.bat" del "RUN-DEMO.bat"
if exist "QUICK-DEMO.bat" del "QUICK-DEMO.bat"
if exist "DEMO-INSTRUCTIONS.md" del "DEMO-INSTRUCTIONS.md"
if exist "BACKEND-DEMO.html" del "BACKEND-DEMO.html"
if exist "WEB-DEMO.bat" del "WEB-DEMO.bat"
if exist "LAUNCH-FRONTEND.bat" del "LAUNCH-FRONTEND.bat"
if exist "CONTINUE-SETUP.bat" del "CONTINUE-SETUP.bat"
if exist "START-DEMO.bat" del "START-DEMO.bat"
if exist "KILL-AND-RESTART.bat" del "KILL-AND-RESTART.bat"
if exist "IMPROVE-VOICE-WEB.bat" del "IMPROVE-VOICE-WEB.bat"
if exist "INSTALL-VISUAL-STUDIO.md" del "INSTALL-VISUAL-STUDIO.md"

:: Remove duplicate test files (now in local-test)
if exist "test.html" del "test.html"
if exist "test-connection.html" del "test-connection.html"
if exist "TEST_EVERYTHING.md" del "TEST_EVERYTHING.md"

:: Remove old local-setup folder (replaced by local-test)
if exist "local-setup" (
    echo Removing old local-setup directory...
    rmdir /s /q "local-setup"
)

:: Remove duplicate documentation files
if exist "QUICK_START.md" del "QUICK_START.md"
if exist "DEMO.md" del "DEMO.md"
if exist "RUNBOOK.md" del "RUNBOOK.md"

:: Remove old scripts folder content that's duplicated
if exist "scripts\test-everything.py" del "scripts\test-everything.py"
if exist "scripts\test-complete-system.py" del "scripts\test-complete-system.py"
if exist "scripts\run-all-tests.py" del "scripts\run-all-tests.py"
if exist "scripts\create-test-data.py" del "scripts\create-test-data.py"

:: Remove temporary backend files
if exist "backend\simple_main.py" del "backend\simple_main.py"

:: Remove Kiro-specific files (not needed for competition)
if exist ".kiro" (
    echo Removing Kiro IDE specific files...
    rmdir /s /q ".kiro"
)

:: Clean up any log files
if exist "*.log" del "*.log"
if exist "backend\*.log" del "backend\*.log"

:: Remove node_modules (will be reinstalled)
if exist "node_modules" (
    echo Removing node_modules directory...
    rmdir /s /q "node_modules"
)

:: Remove Python cache
if exist "backend\__pycache__" rmdir /s /q "backend\__pycache__"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "**\__pycache__" (
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
)

:: Remove build artifacts
if exist "dist" rmdir /s /q "dist"
if exist "src-tauri\target" rmdir /s /q "src-tauri\target"

:: Remove temporary files
if exist "*.tmp" del "*.tmp"
if exist "*.temp" del "*.temp"

:: Remove OS-specific files
if exist ".DS_Store" del ".DS_Store"
if exist "Thumbs.db" del "Thumbs.db"
if exist "desktop.ini" del "desktop.ini"

:: Clean up package-lock if needed (optional)
echo.
echo Do you want to remove package-lock.json? (This will force a fresh npm install)
set /p "choice=Remove package-lock.json? (y/N): "
if /i "%choice%"=="y" (
    if exist "package-lock.json" del "package-lock.json"
    echo ✅ Removed package-lock.json
)

echo.
echo ========================================
echo Repository Cleanup Complete!
echo ========================================
echo.
echo 📁 Professional structure now ready:
echo   ├── local-test/              - Complete testing suite
echo   ├── src/                     - Frontend React application  
echo   ├── backend/                 - Python FastAPI server
echo   ├── src-tauri/               - Desktop app configuration
echo   ├── .github/                 - CI/CD workflows
echo   ├── README.md                - Main documentation
echo   ├── CLOUD-TESTING.md         - Cloud testing guide
echo   ├── COMPETITION-READY.md     - Competition summary
echo   ├── SECURITY.md              - Security documentation
echo   ├── PRIVACY.md               - Privacy policy
echo   ├── CONTRIBUTING.md          - Contribution guidelines
echo   └── CHANGELOG.md             - Version history
echo.
echo 🧹 Removed files:
echo   ❌ Temporary demo scripts
echo   ❌ Duplicate test files  
echo   ❌ Old local-setup folder
echo   ❌ Build artifacts
echo   ❌ Cache directories
echo   ❌ IDE-specific files
echo.
echo 🎉 Ready for competition submission!
echo.
echo Next steps:
echo   1. Run: local-test\setup-and-test.bat (to verify everything works)
echo   2. Git add, commit, and push to repository
echo   3. Create release tag for competition
echo.
pause
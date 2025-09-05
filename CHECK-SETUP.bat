@echo off
echo ========================================
echo Aura Setup Check
echo ========================================
echo.

:: Check directory
if not exist package.json (
    echo ERROR: Not in project root directory
    echo Current directory: %CD%
    echo Looking for: package.json
    exit /b 1
)
echo ✓ In correct directory

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Node.js not found
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo ✓ Node.js: %%i
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo ✓ Python: %%i
)

:: Check Rust (optional for demo)
rustc --version >nul 2>&1
if errorlevel 1 (
    echo ⚠ Rust not found (needed for building)
) else (
    for /f "tokens=*" %%i in ('rustc --version') do echo ✓ Rust: %%i
)

echo.
echo Project structure:
if exist src echo ✓ Frontend source
if exist backend echo ✓ Backend
if exist src-tauri echo ✓ Tauri config
if exist package.json echo ✓ Package.json
if exist .env.template echo ✓ Environment template

echo.
echo ========================================
echo Setup Status: READY
echo ========================================
echo.
echo Next step: Run RUN-DEMO.bat
echo.
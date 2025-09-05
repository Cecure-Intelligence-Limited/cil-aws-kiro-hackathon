@echo off
echo ========================================
echo Aura Prerequisites Check
echo ========================================
echo.

set "ERRORS=0"

:: Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found
    echo    Please install Node.js 18+ from https://nodejs.org/
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo ✅ Node.js: %%i
)

:: Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    echo    Please install Python 3.9+ from https://python.org/
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo ✅ Python: %%i
)

:: Check Rust (optional for web demo)
echo Checking Rust...
rustc --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Rust not found (required for native desktop app)
    echo    Install from https://rustup.rs/ for full experience
) else (
    for /f "tokens=*" %%i in ('rustc --version') do echo ✅ Rust: %%i
)

:: Check Git
echo Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git not found (recommended for development)
) else (
    for /f "tokens=*" %%i in ('git --version') do echo ✅ Git: %%i
)

echo.
if %ERRORS% equ 0 (
    echo ========================================
    echo Prerequisites Status: READY ✅
    echo ========================================
    exit /b 0
) else (
    echo ========================================
    echo Prerequisites Status: MISSING REQUIREMENTS ❌
    echo ========================================
    echo.
    echo Please install the missing prerequisites and try again.
    exit /b 1
)
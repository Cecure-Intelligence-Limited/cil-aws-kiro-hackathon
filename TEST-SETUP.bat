@echo off
echo ========================================
echo Aura Desktop Assistant - Setup Test
echo ========================================
echo.

:: Check if we're in the right directory
if not exist package.json (
    echo ERROR: Please run this from the project root directory
    echo (where package.json is located)
    pause
    exit /b 1
)

echo Checking prerequisites...

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✓ Node.js found
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.9+ from https://python.org/
    pause
    exit /b 1
) else (
    echo ✓ Python found
)

:: Check Rust
rustc --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Rust not found
    echo Please install Rust from https://rustup.rs/
    pause
    exit /b 1
) else (
    echo ✓ Rust found
)

echo.
echo All prerequisites found!
echo.
echo Project structure check:
if exist src echo ✓ Frontend source found
if exist backend echo ✓ Backend found
if exist src-tauri echo ✓ Tauri config found
if exist package.json echo ✓ Package.json found
if exist .env.template echo ✓ Environment template found

echo.
echo ========================================
echo Ready to run demo!
echo ========================================
echo.
echo Run: QUICK-DEMO.bat
echo.
pause
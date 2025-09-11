@echo off
echo ========================================
echo ULTIMATE AURA DEMO STARTUP
echo (Handles all permission issues)
echo ========================================

cd /d "%~dp0"

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo 🔧 FIXING DEPENDENCY ISSUES...
echo.

echo Method 1: Using existing Anaconda packages...
python -c "import pandas, numpy, fastapi; print('✅ Core packages already available!')" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Great! Your Anaconda environment already has the core packages
    goto :start_server
)

echo Method 2: Installing with conda (recommended for Anaconda)...
conda install -y pandas numpy fastapi uvicorn pydantic structlog 2>nul
if %errorlevel% equ 0 (
    echo ✅ Conda installation successful
    goto :install_extras
)

echo Method 3: Installing with pip --user (bypass permissions)...
pip install --user --no-deps pandas numpy fastapi uvicorn pydantic structlog python-multipart aiofiles requests
if %errorlevel% neq 0 (
    echo ⚠️ Some packages may not have installed correctly
)

:install_extras
echo.
echo Installing additional automation packages...
pip install --user fuzzywuzzy python-levenshtein openpyxl xlrd odfpy pydantic-settings 2>nul

echo Installing optional visualization packages...
pip install --user matplotlib seaborn 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Chart generation may not be available (reports will still work)
)

:start_server
echo.
echo Creating necessary directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\reports" mkdir "backend\data\reports"

echo.
echo 🚀 STARTING FULL FEATURE DEMO SERVER...
echo ========================================
echo 🎯 HACKATHON DEMO READY!
echo ========================================
echo Server: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo 🎬 DEMO FEATURES:
echo • OCR Data Extraction from invoices/receipts
echo • Email Management with smart sorting
echo • Calendar Scheduling across time zones
echo • Report Generation with charts
echo • Document Workflow Processing
echo • Spreadsheet Analysis ^& In-Place Updates
echo • File Operations with voice commands
echo.
echo 📋 After server starts, run: python test-full-demo.py
echo.
echo Press Ctrl+C to stop the server
echo ========================================

cd backend
python main.py

pause
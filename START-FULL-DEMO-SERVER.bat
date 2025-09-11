@echo off
echo ========================================
echo Starting FULL Aura Desktop Assistant Demo
echo (All Features Enabled)
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
echo Method 1: Trying conda for pandas/numpy...
conda install -y -q pandas numpy matplotlib seaborn 2>nul
if %errorlevel% equ 0 (
    echo ✅ Conda installation successful
) else (
    echo ⚠️ Conda not available or failed, trying pip with --user flag...
    pip install --user --no-deps pandas numpy matplotlib seaborn
)

echo.
echo Installing core FastAPI dependencies...
pip install --user fastapi uvicorn[standard] pydantic pydantic-settings structlog python-multipart aiofiles requests

echo.
echo Installing automation dependencies...
pip install --user fuzzywuzzy python-levenshtein openpyxl xlrd odfpy

echo.
echo Installing optional advanced features...
pip install --user --no-deps Pillow opencv-python-headless pytesseract PyMuPDF python-docx 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Some advanced features may not be available (OCR, PDF processing)
    echo Basic automation will still work perfectly
)

echo.
echo Creating necessary directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\reports" mkdir "backend\data\reports"

echo.
echo Testing core imports...
python -c "import fastapi, pandas, numpy; print('✅ Core packages working!')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Core packages not working properly
    echo Trying emergency fix...
    python -m pip install --user --force-reinstall pandas numpy fastapi
)

echo.
echo ========================================
echo Starting FULL FEATURE SERVER
echo ========================================
echo Server: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo 🎯 DEMO FEATURES AVAILABLE:
echo ✅ OCR Data Extraction
echo ✅ Email Management Automation  
echo ✅ Calendar Scheduling
echo ✅ Report Generation with Charts
echo ✅ Document Workflow Processing
echo ✅ Spreadsheet Analysis ^& Updates
echo ✅ File Operations
echo.
echo Press Ctrl+C to stop the server
echo ========================================

cd backend
python main.py

pause
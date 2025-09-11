@echo off
echo 🏆 HACKATHON READY STARTUP - FINAL VERSION
echo ==========================================
echo Fixing all issues and starting demo-ready system
echo ==========================================

cd /d "%~dp0"

echo.
echo 🔧 STEP 1: Fixing file permissions and locks...
call FIX-FILE-PERMISSIONS.bat

echo.
echo 🔧 STEP 2: Killing any existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo 🔧 STEP 3: Installing/updating dependencies...
pip install --user --upgrade fastapi uvicorn pandas numpy pydantic structlog python-multipart aiofiles requests fuzzywuzzy python-levenshtein openpyxl

echo.
echo 🔧 STEP 4: Creating required directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\reports" mkdir "backend\data\reports"
if not exist "backend\documents" mkdir "backend\documents"

echo.
echo 🚀 STEP 5: Starting backend server...
echo ==========================================
echo 🎯 HACKATHON DEMO READY!
echo ==========================================
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo 🎬 DEMO FEATURES READY:
echo • ✅ OCR Data Extraction from documents
echo • ✅ Email Management with smart sorting  
echo • ✅ Calendar Scheduling across time zones
echo • ✅ Report Generation with charts
echo • ✅ Document Workflow Processing
echo • ✅ Spreadsheet Analysis ^& Updates (FIXED!)
echo • ✅ File Operations automation
echo.
echo 📋 After server starts, run: python FINAL-HACKATHON-TEST.py
echo.
echo Press Ctrl+C to stop the server
echo ==========================================

cd backend
python main.py

pause
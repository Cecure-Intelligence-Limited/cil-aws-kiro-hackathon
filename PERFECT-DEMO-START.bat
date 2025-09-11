@echo off
echo 🏆 PERFECT HACKATHON DEMO - SIMPLE & RELIABLE
echo ============================================
echo Starting your winning demo system now...
echo ============================================

cd /d "%~dp0"

echo.
echo 🔧 Step 1: Clean start...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
timeout /t 2 /nobreak > nul

echo.
echo 🔧 Step 2: Install packages...
pip install --user --quiet fastapi uvicorn pandas numpy pydantic structlog python-multipart aiofiles requests fuzzywuzzy python-levenshtein openpyxl 2>nul

echo.
echo 🔧 Step 3: Create directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\reports" mkdir "backend\data\reports"
if not exist "backend\documents" mkdir "backend\documents"

echo.
echo 🔧 Step 4: Starting backend...
start "BACKEND" cmd /k "cd backend && echo 🚀 BACKEND STARTING... && python main.py"

echo.
echo ⏳ Waiting for backend...
timeout /t 6 /nobreak > nul

echo.
echo 🔧 Step 5: Starting frontend...
start "FRONTEND" cmd /k "echo 🌐 FRONTEND STARTING... && npm run dev"

echo.
echo ⏳ Waiting for frontend...
timeout /t 8 /nobreak > nul

echo.
echo ✅ DEMO SYSTEM READY!
echo =====================
echo.
echo 🌐 **Web App**: http://localhost:5173
echo 📡 **Backend**: http://localhost:8000
echo 📚 **API Docs**: http://localhost:8000/docs
echo.
echo 🎤 **DEMO COMMANDS**:
echo • "Create payroll file"
echo • "Calculate total salary"
echo • "Update spreadsheet"
echo.
echo 🎯 Opening web app...
timeout /t 2 /nobreak > nul
start http://localhost:5173

echo.
echo 🏆 **HACKATHON DEMO IS LIVE!**
echo.
echo Keep the BACKEND and FRONTEND windows open
echo Press any key to test the system...
pause > nul

echo.
echo 🧪 Testing system...
python FINAL-VALIDATION-TEST.py

echo.
echo 🎉 **READY FOR JUDGES!**
pause
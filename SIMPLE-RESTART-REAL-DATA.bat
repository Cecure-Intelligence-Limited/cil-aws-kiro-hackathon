@echo off
echo 🔄 SIMPLE RESTART WITH REAL DATA DISPLAY
echo ========================================
echo Starting enhanced backend with actual employee data display
echo ========================================

cd /d "%~dp0"

echo.
echo 🛑 Step 1: Stopping existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
timeout /t 3 /nobreak > nul

echo.
echo 🚀 Step 2: Starting enhanced backend...
start "ENHANCED-BACKEND" cmd /k "cd backend && echo 🚀 ENHANCED BACKEND WITH REAL DATA STARTING... && python main.py"

echo.
echo ⏳ Waiting for backend to initialize...
timeout /t 8 /nobreak > nul

echo.
echo 🌐 Step 3: Starting frontend...
start "FRONTEND" cmd /k "echo 🌐 FRONTEND STARTING... && npm run dev"

echo.
echo ⏳ Waiting for frontend to initialize...
timeout /t 10 /nobreak > nul

echo.
echo 🎉 ENHANCED SYSTEM READY!
echo =========================
echo.
echo 🎬 **ENHANCED WOW COMMANDS FOR JUDGES**:
echo.
echo 1. "Read fortune500-payroll.csv and calculate total compensation"
echo    → NOW SHOWS: Sarah Chen (CEO) $1,145,000, Michael Rodriguez (CTO) $733,000
echo.
echo 2. "Analyze global-sales.csv and show revenue breakdown"
echo    → NOW SHOWS: John Mitchell $12.3M sales, Hiroshi Tanaka $13.8M sales
echo.
echo 3. "Calculate total salary from sample-budget.csv"
echo    → NOW SHOWS: Detailed budget breakdown with actual amounts
echo.
echo 🌐 **DEMO URLS**:
echo   Web App: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
echo 🎯 **ENHANCED FEATURES**:
echo ✅ Shows real employee names and positions
echo ✅ Displays actual salaries and compensation
echo ✅ Provides detailed business breakdowns
echo ✅ Enhanced insights with specific amounts
echo.
echo 🎉 Opening demo application...
timeout /t 3 /nobreak > nul
start http://localhost:5173

echo.
echo 🏆 **READY FOR HACKATHON DEMO!**
echo.
echo Press any key to continue...
pause > nul
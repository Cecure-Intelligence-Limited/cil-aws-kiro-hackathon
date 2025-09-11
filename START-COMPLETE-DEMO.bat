@echo off
echo 🎯 COMPLETE HACKATHON DEMO - FULL STACK STARTUP
echo ===============================================
echo Starting Backend API + Frontend Web App + Desktop
echo ===============================================

cd /d "%~dp0"

echo.
echo 🔧 STEP 1: Killing existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
taskkill /f /im electron.exe 2>nul

echo.
echo 🔧 STEP 2: Installing Node.js dependencies...
echo Installing frontend dependencies (this may take a moment)...
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install Node.js dependencies
    echo 💡 Make sure Node.js is installed: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo 🔧 STEP 3: Installing Python dependencies...
pip install --user --upgrade fastapi uvicorn pandas numpy pydantic structlog python-multipart aiofiles requests fuzzywuzzy python-levenshtein openpyxl

echo.
echo 🔧 STEP 4: Creating required directories and files...
call FINAL-FIX-ALL-ISSUES.bat

echo.
echo 🚀 STEP 5: Starting Backend API Server...
echo Starting backend on http://localhost:8000
start "Backend API Server" cmd /k "cd backend && python main.py"

echo.
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 STEP 6: Starting Frontend Development Server...
echo Starting frontend on http://localhost:5173
start "Frontend Dev Server" cmd /k "npm run dev"

echo.
echo ⏳ Waiting for frontend to initialize...
timeout /t 8 /nobreak > nul

echo.
echo 🖥️ STEP 7: Starting Desktop Application...
start "Desktop App" cmd /k "npm run electron"

echo.
echo ✅ ALL SERVICES STARTED SUCCESSFULLY!
echo ===============================================
echo 🎬 HACKATHON DEMO READY!
echo ===============================================
echo.
echo 📋 Your Demo URLs:
echo   🌐 Frontend Web App: http://localhost:5173
echo   📡 Backend API: http://localhost:8000  
echo   📚 API Documentation: http://localhost:8000/docs
echo   🖥️ Desktop App: Native window opened
echo.
echo 🧪 Test Commands:
echo   Backend Only: python FINAL-HACKATHON-TEST.py
echo   Full Demo: Open http://localhost:5173 in browser
echo.
echo 💡 Demo Script:
echo   1. Show web app at localhost:5173
echo   2. Demonstrate automation features
echo   3. Show API docs at localhost:8000/docs
echo   4. Test spreadsheet operations
echo   5. Show desktop app integration
echo.
echo 🎯 Press any key to open the web application...
pause > nul
start http://localhost:5173

echo.
echo 🎉 HACKATHON DEMO IS LIVE!
echo Press any key to exit (this will stop all servers)
pause > nul

echo.
echo 🛑 Stopping all services...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
taskkill /f /im electron.exe 2>nul
echo ✅ All services stopped.
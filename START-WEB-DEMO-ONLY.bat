@echo off
echo 🌐 WEB-ONLY HACKATHON DEMO - NO ELECTRON NEEDED
echo ===============================================
echo Starting Backend API + Frontend Web App ONLY
echo (Skipping problematic Electron desktop app)
echo ===============================================

cd /d "%~dp0"

echo.
echo 🔧 STEP 1: Killing existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo 🔧 STEP 2: Installing Node.js dependencies (lightweight)...
call npm install --production=false
if %errorlevel% neq 0 (
    echo ⚠️ Full npm install failed, trying basic install...
    call npm install react react-dom vite @vitejs/plugin-react
)

echo.
echo 🔧 STEP 3: Installing Python dependencies...
pip install --user --upgrade fastapi uvicorn pandas numpy pydantic structlog python-multipart aiofiles requests fuzzywuzzy python-levenshtein openpyxl

echo.
echo 🔧 STEP 4: Creating required directories and files...
call FINAL-FIX-ALL-ISSUES.bat

echo.
echo 🚀 STEP 5: Starting Backend API Server...
echo Backend starting on http://localhost:8000
start "Backend API Server" cmd /k "cd backend && python main.py"

echo.
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 STEP 6: Starting Frontend Web Server...
echo Frontend starting on http://localhost:5173
start "Frontend Web Server" cmd /k "npm run dev"

echo.
echo ⏳ Waiting for frontend to initialize...
timeout /t 8 /nobreak > nul

echo.
echo ✅ WEB DEMO READY!
echo ===============================================
echo 🎬 HACKATHON DEMO URLS
echo ===============================================
echo.
echo 🌐 MAIN WEB APP: http://localhost:5173
echo   ↳ Full interactive web interface
echo   ↳ Voice commands, automation features
echo   ↳ Perfect for live demo presentation
echo.
echo 📡 BACKEND API: http://localhost:8000
echo   ↳ JSON API responses
echo   ↳ Shows technical capabilities
echo.
echo 📚 API DOCUMENTATION: http://localhost:8000/docs
echo   ↳ Interactive API testing
echo   ↳ Great for technical judges
echo.
echo 🧪 Test Commands:
echo   Backend Test: python FINAL-HACKATHON-TEST.py
echo   Web Interface: Open http://localhost:5173
echo.
echo 🎯 DEMO SCRIPT:
echo   1. Open http://localhost:5173 (main demo)
echo   2. Show voice commands and automation
echo   3. Demonstrate spreadsheet operations
echo   4. Show http://localhost:8000/docs (technical)
echo   5. Run backend tests for validation
echo.
echo 🎉 Press any key to open the web application...
pause > nul
start http://localhost:5173

echo.
echo 🌟 WEB DEMO IS LIVE! Perfect for hackathon presentation!
echo 💡 No desktop app needed - web interface has all features
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo 🛑 Stopping servers...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
echo ✅ All servers stopped.
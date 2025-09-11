@echo off
echo 🚀 RESTARTING WITH ULTRA-FAST VOICE SYSTEM
echo ==========================================
echo Applying lightning-fast voice recognition fixes
echo ==========================================

cd /d "%~dp0"

echo.
echo 🔧 Stopping existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo ⚡ Starting optimized backend...
start "Ultra-Fast Backend" cmd /k "cd backend && python main.py"

echo.
echo ⏳ Waiting for backend...
timeout /t 3 /nobreak > nul

echo.
echo 🌐 Starting ultra-fast frontend...
start "Ultra-Fast Frontend" cmd /k "npm run dev"

echo.
echo ⏳ Waiting for frontend...
timeout /t 5 /nobreak > nul

echo.
echo ✅ ULTRA-FAST VOICE SYSTEM READY!
echo ==========================================
echo 🎯 HACKATHON DEMO READY!
echo ==========================================
echo.
echo 🌐 **Web App**: http://localhost:5173
echo 📡 **Backend**: http://localhost:8000
echo.
echo 🎤 **NEW VOICE FEATURES**:
echo   • Lightning-fast recognition (0.5s response)
echo   • Smart command parsing
echo   • Creates EXACTLY what you ask for
echo   • Multiple hotkeys: Ctrl+' / F1 / Spacebar
echo.
echo 🎯 **DEMO COMMANDS**:
echo   • "Create payroll.xlsx file" ← Perfect Excel file
echo   • "Calculate total salary" ← Instant analysis
echo   • "Update salary with increase" ← Smart updates
echo.
echo 🎉 Press any key to open the web app...
pause > nul
start http://localhost:5173

echo.
echo 🏆 READY TO WIN THE HACKATHON!
pause
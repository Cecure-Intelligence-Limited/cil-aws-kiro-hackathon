@echo off
echo ========================================
echo EMERGENCY WEB DEMO - No Build Tools Required
echo ========================================
echo.
echo This demo runs the web version without Tauri
echo Perfect for quick testing and demonstrations
echo.
pause

cd /d "%~dp0\.."

:: Fix backend dependencies
echo 🔧 Installing missing backend dependencies...
cd backend
call venv\Scripts\activate
pip install aiohttp==3.9.1 aiofiles==23.2.1
cd ..

:: Start backend
echo 🚀 Starting backend server...
cd backend
start "Aura Backend" cmd /k "call venv\Scripts\activate && echo Backend Starting... && python main.py"

:: Wait for backend
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

:: Start frontend (web version)
echo 🌐 Starting web frontend...
start "Aura Web" cmd /k "echo Frontend Starting... && npm run dev"

echo.
echo ========================================
echo WEB DEMO READY! 🎉
echo ========================================
echo.
echo 📋 Access Instructions:
echo   1. Wait 10 seconds for servers to start
echo   2. Open: http://localhost:1420
echo   3. Click the microphone to test voice
echo   4. Try these commands:
echo      - "Create a meeting notes document"
echo      - "Analyze my budget spreadsheet"
echo      - "Summarize the demo document"
echo.
echo 🎯 Demo Features:
echo   ✅ Voice recognition (browser-based)
echo   ✅ File operations
echo   ✅ Document processing
echo   ✅ Spreadsheet analysis
echo   ✅ Real-time responses
echo.
echo 💡 This web demo shows 90%% of functionality
echo    without requiring Visual Studio Build Tools!
echo.
pause
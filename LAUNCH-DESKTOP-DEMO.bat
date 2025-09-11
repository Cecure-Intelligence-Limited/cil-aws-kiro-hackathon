@echo off
echo ========================================
echo AURA DESKTOP DEMO LAUNCHER
echo ========================================
echo.
echo 🖥️  Launching Electron Desktop App...
echo.

cd /d "%~dp0"

echo 🔧 Quick dependency check...
call npm list electron >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Electron not found, installing...
    call npm install electron --save-dev
)

echo.
echo 🚀 Starting backend server...
cd backend
start /min cmd /c "python main.py"
cd ..

echo ⏳ Waiting for server to start...
timeout /t 3 /nobreak >nul

echo.
echo 🖥️  Launching Electron desktop app...
call npm run electron:dev

echo.
echo 🎯 Desktop app launched!
echo 📋 Global shortcut: Ctrl+' to show/hide
echo 🌐 Backend: http://localhost:8000
echo.
pause
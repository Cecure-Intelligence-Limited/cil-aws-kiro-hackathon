@echo off
echo ========================================
echo 🧹 CLEAN DESKTOP APP STARTUP
echo ========================================
echo.

cd /d "%~dp0"

echo 🛑 Stopping any running processes...
taskkill /IM node.exe /F >nul 2>&1
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM electron.exe /F >nul 2>&1

echo ⏳ Waiting for ports to clear...
timeout /t 2 /nobreak >nul

echo 🔧 Setting up backend...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1

echo 🚀 Starting fresh backend server...
start "Aura Backend" cmd /k "call venv\Scripts\activate && python main.py"
cd ..

echo ⏳ Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo 🎨 Launching desktop application...
echo.
echo ========================================
echo 🎯 AURA DESKTOP ASSISTANT READY!
echo ========================================
echo.
echo Press Ctrl+' to activate voice mode
echo.

set NODE_ENV=development
npm run desktop:demo

pause
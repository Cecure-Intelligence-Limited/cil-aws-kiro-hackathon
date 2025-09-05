@echo off
echo ========================================
echo 🚀 AURA DESKTOP ASSISTANT - QUICK DEMO
echo ========================================
echo.
echo Starting the complete desktop application...
echo.

cd /d "%~dp0"

:: Kill any existing processes
echo 🧹 Cleaning up existing processes...
taskkill /F /IM node.exe 2>nul >nul
taskkill /F /IM python.exe 2>nul >nul
timeout /t 2 /nobreak >nul

:: Setup environment quickly
if not exist .env copy .env.template .env >nul
if not exist documents mkdir documents
if not exist data mkdir data

:: Start backend
echo 🔧 Starting backend server...
cd backend
start "Aura Backend" cmd /k "call venv\Scripts\activate && python main.py"
cd ..

:: Wait for backend
echo ⏳ Waiting for backend...
timeout /t 3 /nobreak >nul

:: Start frontend
echo 🎨 Starting desktop application...
echo.
echo ========================================
echo 🎯 DESKTOP APP READY!
echo ========================================
echo.
echo The Aura Desktop Assistant will open shortly.
echo Press Ctrl+' to activate voice mode.
echo.
echo Test commands:
echo   • "Create a meeting notes document"
echo   • "Analyze my budget spreadsheet"
echo.

set NODE_ENV=development
npm run desktop:demo

echo.
echo 🎉 Demo complete!
pause
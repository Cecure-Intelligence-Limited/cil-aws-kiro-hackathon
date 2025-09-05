@echo off
echo 🚀 Aura Setup - After Node.js Installation
echo ==========================================

echo.
echo Step 1: Verifying Node.js installation...
node --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Node.js found: 
    node --version
    npm --version
) else (
    echo ❌ Node.js still not found!
    echo.
    echo Please:
    echo 1. Install Node.js from https://nodejs.org/
    echo 2. Make sure "Add to PATH" is checked during installation
    echo 3. Restart your terminal completely
    echo 4. Run this script again
    pause
    exit /b 1
)

echo.
echo Step 2: Installing project dependencies...
call npm install
if %errorlevel% == 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 3: Setting up Python backend...
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate
pip install fastapi uvicorn
cd ..

echo.
echo 🎉 Setup complete!
echo.
echo To start Aura:
echo 1. Run: scripts\start-both.bat
echo 2. Or manually start both servers in separate terminals
echo.
echo Frontend: npm run dev
echo Backend: cd backend && venv\Scripts\activate && python simple_main.py
echo.
pause
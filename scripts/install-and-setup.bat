@echo off
echo 🚀 Complete Aura Setup Script
echo ============================

echo.
echo Step 1: Checking Node.js...
node --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Node.js is installed
    node --version
) else (
    echo ❌ Node.js not found
    echo.
    echo Please install Node.js first:
    echo 1. Go to https://nodejs.org/
    echo 2. Download and install the LTS version
    echo 3. Restart your command prompt
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
    echo Try running: npm install --verbose
    pause
    exit /b 1
)

echo.
echo Step 3: Setting up Python backend...
cd backend
if not exist venv (
    python -m venv venv
    echo ✅ Created Python virtual environment
)

call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% == 0 (
    echo ✅ Python dependencies installed
) else (
    echo ❌ Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo Step 4: Checking configuration...
if exist .env (
    echo ✅ .env file exists
) else (
    echo ⚠️  Creating .env file from template...
    copy .env.template .env
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file if needed: notepad .env
echo 2. Start Aura: scripts\start-aura.bat
echo.
pause
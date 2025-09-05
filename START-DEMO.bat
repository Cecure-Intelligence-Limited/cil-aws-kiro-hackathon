@echo off
echo ========================================
echo Aura Desktop Assistant - Demo Launcher
echo ========================================
echo.

echo Current directory: %CD%
echo.

echo Setting up environment...

:: Setup environment file
if not exist ".env" (
    if exist ".env.template" (
        copy ".env.template" ".env" >nul 2>&1
        echo ✓ Created .env file
    )
) else (
    echo ✓ .env file exists
)

:: Create demo directories
if not exist "documents" mkdir "documents" >nul 2>&1
if not exist "data" mkdir "data" >nul 2>&1
echo ✓ Demo directories ready

echo.
echo Installing frontend dependencies...
npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    echo Make sure you're in the project root directory
    pause
    exit /b 1
)
echo ✓ Frontend dependencies installed

echo.
echo Setting up backend...
cd backend
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create Python virtual environment
        echo Make sure Python 3.9+ is installed
        pause
        exit /b 1
    )
)

echo Installing backend dependencies...
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)
echo ✓ Backend dependencies installed

echo.
echo Creating demo data...
cd ..
python local-setup\create-demo-data.py >nul 2>&1
echo ✓ Demo data created

echo.
echo ========================================
echo STARTING AURA DEMO
echo ========================================

:: Start backend
echo Starting backend server...
cd backend
start "Aura Backend Server" cmd /k "call venv\Scripts\activate && echo Aura Backend Starting... && python main.py"

:: Wait for backend
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

:: Start frontend
cd ..
echo.
echo ========================================
echo LAUNCHING AURA!
echo ========================================
echo.
echo DEMO INSTRUCTIONS:
echo 1. Wait for the Tauri app to open
echo 2. Press Ctrl+' to activate Aura overlay
echo 3. Try these voice commands:
echo    - "Create a meeting notes document"
echo    - "Analyze my sample budget spreadsheet"
echo    - "Summarize the demo document"
echo.
echo Starting Aura frontend...
echo.

npm run tauri:dev

echo.
echo Demo complete! Check the documents folder for created files.
pause
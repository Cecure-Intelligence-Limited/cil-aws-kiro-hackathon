@echo off
echo ========================================
echo Aura Desktop Assistant - Complete Demo
echo ========================================
echo.
echo This is the FULL END-TO-END desktop demo
echo that judges can test after GitHub deployment!
echo.
pause

cd /d "%~dp0\.."

:: Check prerequisites
echo 📋 Checking Prerequisites...
call local-test\check-prerequisites.bat
if errorlevel 1 (
    echo ❌ Prerequisites check failed
    pause
    exit /b 1
)

:: Setup environment
echo 🌍 Setting up environment...
if not exist .env (
    copy .env.template .env >nul
    echo ✅ Created .env configuration
)

:: Create directories
if not exist documents mkdir documents
if not exist data mkdir data

:: Install all dependencies
echo 📦 Installing dependencies...
npm install
if errorlevel 1 (
    echo ❌ Frontend installation failed
    pause
    exit /b 1
)

:: Setup backend
echo 🔧 Setting up backend...
cd backend
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

call venv\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Backend installation failed
    pause
    exit /b 1
)

:: Create demo data
echo 📊 Creating demo data...
cd ..
python local-test\create-demo-data.py

:: Start backend server
echo 🚀 Starting backend server...
cd backend
start "Aura Backend" cmd /k "call venv\Scripts\activate && python main.py"

:: Wait for backend
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Test backend connection
cd ..
python local-test\test-backend.py
if errorlevel 1 (
    echo ⚠️  Backend connection test failed, but continuing
)

:: Launch Electron desktop app
echo 🎨 Launching Aura Desktop Assistant...
echo.
echo ========================================
echo DESKTOP DEMO READY!
echo ========================================
echo.
echo 📋 Test Instructions for Judges:
echo   1. Desktop app will open automatically
echo   2. Press Ctrl+' to show/hide Aura overlay
echo   3. Try these voice commands:
echo      - "Create a meeting notes document"
echo      - "Analyze my sample budget spreadsheet"  
echo      - "Summarize the demo document"
echo      - "Help me organize my files"
echo.
echo 🎯 Success Criteria:
echo   - Voice commands process in under 2 seconds
echo   - Files created with exact content
echo   - Desktop app is responsive and professional
echo   - All features work without internet dependency
echo.

npm run desktop:demo

echo.
echo 🎉 Desktop demo session complete!
echo Check the documents folder for created files.
echo.
pause
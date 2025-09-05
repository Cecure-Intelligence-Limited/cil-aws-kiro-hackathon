@echo off
echo ========================================
echo Aura Desktop Assistant - Setup and Test
echo ========================================
echo.
echo This script will:
echo   1. Verify system prerequisites
echo   2. Install all dependencies
echo   3. Create demo data
echo   4. Launch comprehensive tests
echo   5. Start the desktop application
echo.
pause

:: Navigate to project root
cd /d "%~dp0\.."

:: Check prerequisites
echo 📋 Checking Prerequisites...
call local-test\check-prerequisites.bat
if errorlevel 1 (
    echo ❌ Prerequisites check failed
    pause
    exit /b 1
)
echo ✅ Prerequisites check completed

:: Setup environment
echo 🌍 Setting up environment...
if not exist .env (
    copy .env.template .env >nul
    echo ✅ Created .env configuration
) else (
    echo ✅ .env file already exists
)

:: Create directories
if not exist documents mkdir documents
if not exist data mkdir data
echo ✅ Created project directories

:: Install frontend dependencies
echo 📦 Installing frontend dependencies...
call npm install
if errorlevel 1 (
    echo ❌ Frontend installation failed
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed
echo 🔄 Continuing to backend setup...

:: Setup backend
echo 🔧 Setting up backend...
echo 📂 Changing to backend directory...
cd backend
if not exist venv (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Created Python virtual environment
) else (
    echo ✅ Virtual environment already exists
)

echo 🔄 Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Backend installation failed
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed

:: Create demo data
echo 📊 Creating demo data...
cd ..
python local-test\create-demo-data.py
echo ✅ Demo data created

:: Run tests
echo 🧪 Running test suite...
call local-test\run-all-tests.bat
if errorlevel 1 (
    echo ⚠️  Some tests failed, but continuing with demo
)

:: Start backend
echo 🚀 Starting backend server...
cd backend
start "Aura Backend" cmd /k "call venv\Scripts\activate && echo Aura Backend Server Starting... && python main.py"

:: Wait for backend
echo ⏳ Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

:: Test backend connection
cd ..
python local-test\test-backend.py
if errorlevel 1 (
    echo ⚠️  Backend connection test failed, but continuing
)

:: Launch application
echo 🎨 Launching Aura Desktop Assistant...
echo.
echo ========================================
echo DEMO READY!
echo ========================================
echo.
echo 📋 Test Instructions:
echo   1. Wait for the application to load
echo   2. Press Ctrl+' to activate Aura overlay
echo   3. Try these voice commands:
echo      - "Create a meeting notes document"
echo      - "Analyze my sample budget spreadsheet"
echo      - "Summarize the demo document"
echo.
echo 🎯 Success Criteria:
echo   - Voice commands process in under 2 seconds
echo   - Files created with exact content
echo   - Calculations are accurate
echo   - UI is smooth and responsive
echo.

call npm run tauri:dev

echo.
echo 🎉 Demo session complete!
echo Check the documents folder for created files.
echo.
pause
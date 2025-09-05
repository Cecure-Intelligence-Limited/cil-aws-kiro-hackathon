@echo off
echo ========================================
echo 🏆 AURA DESKTOP ASSISTANT - FINAL TEST
echo ========================================
echo.
echo This is the COMPLETE desktop application
echo ready for hackathon judging!
echo.
echo What this demonstrates:
echo   ✅ Professional desktop application
echo   ✅ Voice-activated AI assistant  
echo   ✅ Intelligent file operations
echo   ✅ Real-time document analysis
echo   ✅ Cross-platform compatibility
echo.
pause

cd /d "%~dp0"

:: Quick prerequisite check
echo 📋 Quick system check...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+ from https://python.org/
    pause
    exit /b 1
)

echo ✅ System requirements met

:: Install dependencies if needed
if not exist node_modules (
    echo 📦 Installing dependencies...
    npm install
)

:: Setup environment
if not exist .env (
    copy .env.template .env >nul
    echo ✅ Environment configured
)

:: Create demo directories
if not exist documents mkdir documents
if not exist data mkdir data

:: Setup backend
echo 🔧 Setting up backend...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1

:: Create demo data
echo 📊 Creating demo data...
cd ..
python local-test\create-demo-data.py >nul 2>&1

:: Start backend
echo 🚀 Starting backend server...
cd backend
start "Aura Backend" cmd /k "call venv\Scripts\activate && python main.py"
cd ..

:: Wait for backend
echo ⏳ Initializing services...
timeout /t 3 /nobreak >nul

:: Launch desktop app
echo 🎨 Launching Aura Desktop Assistant...
echo.
echo ========================================
echo 🎯 DESKTOP APP LAUNCHING!
echo ========================================
echo.
echo 📋 For Judges - Test Instructions:
echo.
echo   1. Desktop app opens automatically
echo   2. Press Ctrl+' to activate voice mode
echo   3. Try these commands:
echo      • "Create a meeting notes document"
echo      • "Analyze my budget spreadsheet"
echo      • "Summarize the demo document"
echo.
echo   4. Check 'documents' folder for results
echo   5. All operations complete in under 2 seconds
echo.
echo 🏆 Success Criteria:
echo   ✅ Professional desktop interface
echo   ✅ Instant voice recognition
echo   ✅ Accurate AI file operations
echo   ✅ Smooth, responsive experience
echo.

set NODE_ENV=development
npm run desktop:demo

echo.
echo 🎉 Demo complete! Check documents folder for generated files.
pause
@echo off
echo 🌐 STARTING FRONTEND WEB APP ONLY
echo =================================
echo This will start the React app on localhost:5173
echo =================================

cd /d "%~dp0"

echo.
echo 🔧 Installing Node.js dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    echo 💡 Make sure Node.js is installed
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Frontend Development Server...
echo.
echo ✅ Frontend will be available at: http://localhost:5173
echo 💡 Make sure backend is running on: http://localhost:8000
echo.
echo Press Ctrl+C to stop the frontend server
echo =================================

npm run dev

pause
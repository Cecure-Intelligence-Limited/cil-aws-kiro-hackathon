@echo off
echo ========================================
echo Starting Aura Desktop Assistant Server
echo (Skipping dependency installation)
echo ========================================

cd /d "%~dp0"

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Creating necessary directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\reports" mkdir "backend\data\reports"

echo.
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.
echo Note: If you see import errors, run START-AUTOMATION-SERVER.bat first
echo.

cd backend
python main.py

pause
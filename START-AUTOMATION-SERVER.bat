@echo off
echo ========================================
echo Starting Aura Desktop Assistant with Automation
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
echo Installing core Python dependencies...
pip install --upgrade pip
pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install core dependencies
    pause
    exit /b 1
)

echo.
echo Installing automation dependencies (optional)...
pip install -r backend/requirements-automation.txt
if %errorlevel% neq 0 (
    echo WARNING: Some automation dependencies failed to install
    echo The server will still work with basic functionality
)

echo.
echo Creating necessary directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\reports" mkdir "backend\data\reports"

echo.
echo Starting FastAPI server with automation capabilities...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py

pause
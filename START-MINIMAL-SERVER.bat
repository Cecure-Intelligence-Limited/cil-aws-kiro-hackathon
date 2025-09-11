@echo off
echo ========================================
echo Starting Aura Desktop Assistant (Minimal)
echo ========================================

cd /d "%~dp0"

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing minimal dependencies only...
pip install --user fastapi uvicorn[standard] pydantic structlog python-multipart aiofiles requests
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may not have installed correctly
    echo The server will still attempt to start
)

echo.
echo Creating necessary directories...
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\reports" mkdir "backend\data\reports"

echo.
echo Starting FastAPI server with minimal configuration...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py

pause
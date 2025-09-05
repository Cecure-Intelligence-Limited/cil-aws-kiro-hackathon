@echo off
echo ========================================
echo Starting Aura Desktop Assistant with Automation
echo ========================================

cd /d "%~dp0"

echo Installing Python dependencies...
pip install -r backend/requirements.txt
pip install -r backend/requirements-automation.txt

echo.
echo Starting FastAPI server with automation capabilities...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

cd backend
python main.py

pause
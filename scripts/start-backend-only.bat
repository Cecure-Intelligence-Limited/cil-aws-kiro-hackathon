@echo off
echo 🔧 Starting Aura Backend Server
echo ===============================

cd backend

echo Setting up Python environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing basic dependencies...
pip install fastapi uvicorn pandas python-dotenv structlog

echo Starting backend server...
echo.
echo ✅ Backend will start on http://localhost:8000
echo ✅ API docs available at http://localhost:8000/docs
echo.
python main.py
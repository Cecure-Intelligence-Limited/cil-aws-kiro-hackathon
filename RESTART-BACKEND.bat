@echo off
echo 🔄 Restarting Backend Server...

echo Stopping any existing backend processes...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak > nul

echo Starting backend server...
cd backend
start "Backend API" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 🧪 Testing endpoints...
cd ..
python test-endpoints.py

echo ✅ Backend restarted and tested!
pause
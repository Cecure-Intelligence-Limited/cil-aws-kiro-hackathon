@echo off
echo 🚀 Starting Simple Aura Backend
echo ===============================

cd backend
call venv\Scripts\activate

echo Starting simple backend server...
echo.
echo ✅ Backend will start on http://localhost:8000
echo ✅ API docs available at http://localhost:8000/docs
echo ✅ Using simple version (no complex dependencies)
echo.

python simple_main.py
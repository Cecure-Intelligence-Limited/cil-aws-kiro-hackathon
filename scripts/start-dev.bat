@echo off
echo Starting Aura Desktop Assistant Development Environment...

echo.
echo [1/3] Starting Backend Server...
start "Aura Backend" cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python main.py"

echo.
echo [2/3] Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo [3/3] Starting Tauri Development...
npm run tauri:dev

echo.
echo Development environment started!
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:1420
echo - Global Shortcut: Ctrl+' or Ctrl+Shift+A
echo.
pause
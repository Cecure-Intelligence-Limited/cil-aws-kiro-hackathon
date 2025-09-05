@echo off
echo 🚀 Starting Aura Frontend and Backend
echo ====================================

echo Starting backend in new window...
start "Aura Backend" cmd /k "cd backend && venv\Scripts\activate && python simple_main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend in new window...
start "Aura Frontend" cmd /k "npm run dev"

echo.
echo 🎉 Both servers are starting!
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:1420
echo.
echo Wait for both windows to show "ready" then test your app!
pause
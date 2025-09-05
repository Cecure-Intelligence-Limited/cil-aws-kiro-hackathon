@echo off
echo 🚀 Starting Aura Desktop Assistant
echo =================================

echo.
echo Starting backend server...
start "Aura Backend" cmd /k "cd backend && venv\Scripts\activate && python main.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Testing backend connection...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Backend is running
) else (
    echo ⚠️  Backend may still be starting...
)

echo.
echo Starting Tauri desktop app...
start "Aura Frontend" cmd /k "npm run tauri:dev"

echo.
echo 🎉 Aura is starting!
echo.
echo Instructions:
echo 1. Wait for the desktop app window to appear
echo 2. Press Ctrl+' (Ctrl + single quote) to activate
echo 3. Try saying: "Create a file called test.txt"
echo 4. Or type: "Create a new document"
echo.
echo Troubleshooting:
echo - If Ctrl+' doesn't work, try Ctrl+Shift+A
echo - Check that both terminal windows are running
echo - Visit http://localhost:8000/docs for API documentation
echo.
pause
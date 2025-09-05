@echo off
echo 🌐 Testing Aura Web Version
echo ===========================

echo.
echo Step 1: Starting backend...
cd backend
call venv\Scripts\activate
start "Aura Backend" cmd /k "python main.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 2: Testing backend health...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Backend is running
) else (
    echo ⚠️  Backend may still be starting...
)

cd ..

echo.
echo Step 3: Starting frontend...
start "Aura Frontend" cmd /k "npm run dev"

echo.
echo 🎉 Aura web version is starting!
echo.
echo Instructions:
echo 1. Wait for both terminal windows to show "ready"
echo 2. Open http://localhost:1420 in your browser
echo 3. Try typing: "Create a file called test.txt"
echo.
echo Note: This is the web version. Desktop features require Tauri.
echo.
pause
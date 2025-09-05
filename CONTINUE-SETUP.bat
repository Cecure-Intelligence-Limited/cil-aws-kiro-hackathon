@echo off
echo ========================================
echo Continuing Aura Setup...
echo ========================================
echo.

echo Setting up backend...
cd backend
call venv\Scripts\activate
echo Installing backend dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Backend setup failed
    pause
    exit /b 1
)
echo ✓ Backend ready

echo.
echo Creating demo data...
cd ..
python local-setup\create-demo-data.py
echo ✓ Demo data created

echo.
echo ========================================
echo STARTING AURA DEMO
echo ========================================

echo Starting backend server...
cd backend
start "Aura Backend" cmd /k "call venv\Scripts\activate && echo Aura Backend Starting... && python main.py"

echo Waiting for backend...
timeout /t 8 /nobreak >nul

cd ..
echo.
echo ========================================
echo LAUNCHING AURA!
echo ========================================
echo.
echo DEMO INSTRUCTIONS:
echo 1. Wait for Tauri app to open
echo 2. Press Ctrl+' to activate overlay
echo 3. Try: "Create a meeting notes document"
echo 4. Try: "Analyze my sample budget spreadsheet"
echo.

npm run tauri:dev

echo.
echo Demo complete!
pause
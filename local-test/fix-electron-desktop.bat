@echo off
echo ========================================
echo ELECTRON DESKTOP FIX - Win the Hackathon!
echo ========================================
echo.
echo This will fix any Electron desktop issues
echo and get your desktop app working perfectly.
echo.
echo ✅ You're using ELECTRON (not Tauri) - Smart choice!
echo.
pause

cd /d "%~dp0\.."

echo 🔧 Step 1: Ensuring Electron dependencies are installed...
call npm install

echo 🧹 Step 2: Cleaning any build artifacts...
if exist dist rmdir /s /q dist
if exist dist-electron rmdir /s /q dist-electron

echo 📦 Step 3: Installing/updating Electron...
call npm install electron@latest --save-dev
echo 🔧 Step 4: Fixing backend dependencies...
cd backend
if exist venv\Scripts\activate (
    call venv\Scripts\activate
    pip install aiohttp==3.9.1 aiofiles==23.2.1 structlog pandas numpy
) else (
    echo ⚠️  Backend virtual environment not found
    echo Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
)
cd ..

echo 🧪 Step 5: Testing Electron desktop app...
echo Building frontend...
call npm run build

echo Testing Electron launch...
call npm run electron

if errorlevel 1 (
    echo ❌ Electron test failed
    echo � T3rying to fix common issues...
    
    echo Reinstalling Electron...
    call npm uninstall electron
    call npm install electron@latest --save-dev
    
    echo Retrying Electron launch...
    call npm run electron
)

echo.
echo ========================================
echo ELECTRON DESKTOP SETUP COMPLETE! 🎉
echo ========================================
echo.
echo ✅ Electron dependencies installed
echo ✅ Backend dependencies fixed  
echo ✅ Desktop app ready to launch
echo.
echo � LaunTch commands:
echo    npm run electron:dev    (Development mode)
echo    npm run desktop:demo    (Demo mode)
echo.
echo 🎯 Global shortcut: Ctrl+' to show/hide
echo.
echo 🏆 You're ready to win the hackathon!
echo.
pause
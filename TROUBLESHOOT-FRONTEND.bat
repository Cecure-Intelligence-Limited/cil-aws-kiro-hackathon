@echo off
echo 🔍 FRONTEND TROUBLESHOOTING SCRIPT
echo ==================================
echo Diagnosing why localhost:5173 isn't working
echo ==================================

cd /d "%~dp0"

echo.
echo 🔧 STEP 1: Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo 💡 Download and install Node.js from: https://nodejs.org/
    echo 💡 Recommended version: 18.x or higher
    pause
    exit /b 1
) else (
    echo ✅ Node.js is installed
)

echo.
echo 🔧 STEP 2: Checking npm installation...
npm --version
if %errorlevel% neq 0 (
    echo ❌ npm is not available
    pause
    exit /b 1
) else (
    echo ✅ npm is available
)

echo.
echo 🔧 STEP 3: Checking package.json...
if not exist "package.json" (
    echo ❌ package.json not found
    pause
    exit /b 1
) else (
    echo ✅ package.json exists
)

echo.
echo 🔧 STEP 4: Checking if port 5173 is in use...
netstat -an | findstr :5173
if %errorlevel% equ 0 (
    echo ⚠️ Port 5173 is already in use
    echo 🔧 Killing processes on port 5173...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /f /pid %%a 2>nul
) else (
    echo ✅ Port 5173 is available
)

echo.
echo 🔧 STEP 5: Cleaning and installing dependencies...
if exist "node_modules" (
    echo Removing old node_modules...
    rmdir /s /q node_modules
)

if exist "package-lock.json" (
    echo Removing package-lock.json...
    del package-lock.json
)

echo Installing fresh dependencies...
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    echo 💡 Try running as administrator
    pause
    exit /b 1
) else (
    echo ✅ Dependencies installed successfully
)

echo.
echo 🔧 STEP 6: Testing Vite development server...
echo Starting frontend server (this will open in a new window)...
echo ✅ If successful, frontend will be at: http://localhost:5173
echo.
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ⏳ Waiting for server to start...
timeout /t 10 /nobreak > nul

echo.
echo 🧪 STEP 7: Testing if frontend is accessible...
curl -s http://localhost:5173 > nul
if %errorlevel% equ 0 (
    echo ✅ Frontend is running and accessible!
    start http://localhost:5173
) else (
    echo ⚠️ Frontend may still be starting up...
    echo 💡 Check the Frontend Server window for any errors
    echo 💡 Try opening http://localhost:5173 manually in your browser
)

echo.
echo ===============================================
echo 🎯 TROUBLESHOOTING COMPLETE
echo ===============================================
echo.
echo 📋 If frontend still doesn't work:
echo   1. Check the "Frontend Server" window for errors
echo   2. Try running: npm run dev manually
echo   3. Ensure no antivirus is blocking port 5173
echo   4. Try a different port by editing vite.config.ts
echo.
echo 🌐 Expected URLs:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo.
pause
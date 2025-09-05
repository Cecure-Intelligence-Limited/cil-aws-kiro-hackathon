@echo off
echo 🔍 Checking Node.js Installation
echo ===============================

echo.
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Node.js found: 
    node --version
) else (
    echo ❌ Node.js not found or not in PATH
    echo.
    echo Please install Node.js from https://nodejs.org/
    echo Make sure to check "Add to PATH" during installation
    goto :error
)

echo.
echo Checking npm...
npm --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ npm found: 
    npm --version
) else (
    echo ❌ npm not found
    goto :error
)

echo.
echo Checking if we're in the right directory...
if exist package.json (
    echo ✅ package.json found - you're in the right directory
) else (
    echo ❌ package.json not found - wrong directory?
    echo Current directory: %CD%
    goto :error
)

echo.
echo Checking node_modules...
if exist node_modules (
    echo ✅ node_modules found - dependencies installed
) else (
    echo ⚠️  node_modules not found - need to run: npm install
)

echo.
echo 🎉 Node.js setup looks good!
echo You can now run: npm run dev
goto :end

:error
echo.
echo ❌ There are issues with your Node.js setup.
echo.
echo To fix:
echo 1. Install Node.js from https://nodejs.org/
echo 2. Restart your terminal
echo 3. Run this script again

:end
pause
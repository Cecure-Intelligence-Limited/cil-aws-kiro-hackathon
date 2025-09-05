@echo off
echo 🧪 Testing Node.js Installation
echo ==============================

echo.
echo Testing Node.js...
node --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Node.js is working!
    node --version
) else (
    echo ❌ Node.js not found
    echo Please install from https://nodejs.org/
    goto :end
)

echo.
echo Testing npm...
npm --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ npm is working!
    npm --version
) else (
    echo ❌ npm not found
    goto :end
)

echo.
echo Testing project setup...
if exist package.json (
    echo ✅ Found package.json
    
    if exist node_modules (
        echo ✅ Dependencies already installed
    ) else (
        echo ⚠️  Installing dependencies...
        call npm install
        if %errorlevel% == 0 (
            echo ✅ Dependencies installed successfully!
        ) else (
            echo ❌ Failed to install dependencies
        )
    )
) else (
    echo ❌ package.json not found - are you in the right directory?
)

echo.
echo 🎉 Ready to start Aura!
echo Run: npm run dev

:end
pause
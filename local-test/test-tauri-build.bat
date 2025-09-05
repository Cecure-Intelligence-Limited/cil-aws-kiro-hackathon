@echo off
echo ========================================
echo TESTING TAURI BUILD
echo ========================================
echo.

cd /d "%~dp0\.."

echo 🧹 Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist src-tauri\target rmdir /s /q src-tauri\target

echo 📦 Installing dependencies...
call npm install

echo 🔧 Testing TypeScript compilation...
call npx tsc --noEmit
if errorlevel 1 (
    echo ❌ TypeScript compilation failed
    pause
    exit /b 1
)
echo ✅ TypeScript compilation successful

echo 🏗️ Testing Vite build...
call npm run build
if errorlevel 1 (
    echo ❌ Vite build failed
    pause
    exit /b 1
)
echo ✅ Vite build successful

echo 🦀 Testing Tauri development build...
call npm run tauri dev --help >nul 2>&1
if errorlevel 1 (
    echo ❌ Tauri CLI not working
    call npm install -g @tauri-apps/cli
)

echo 🚀 Starting Tauri development mode...
echo.
echo ========================================
echo TAURI DEV MODE STARTING! 🎉
echo ========================================
echo.
echo This will open your native desktop app!
echo Press Ctrl+C to stop when you're done testing.
echo.
pause

call npm run tauri dev
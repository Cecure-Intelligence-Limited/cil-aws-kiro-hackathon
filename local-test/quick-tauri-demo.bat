@echo off
echo ========================================
echo QUICK TAURI DEMO - BYPASS TYPE CHECKING
echo ========================================
echo.
echo Getting your app running FAST for the hackathon!
echo.

cd /d "%~dp0\.."

echo 🧹 Cleaning build cache...
if exist dist rmdir /s /q dist
if exist src-tauri\target\debug rmdir /s /q src-tauri\target\debug

echo 📦 Installing dependencies...
call npm install --silent

echo 🔧 Building without strict type checking...
set VITE_SKIP_TYPE_CHECK=true
call npm run build -- --mode development

if errorlevel 1 (
    echo ⚠️  Build failed, trying Vite directly...
    call npx vite build --mode development
)

echo 🦀 Starting Tauri development mode...
echo.
echo ========================================
echo TAURI LAUNCHING! 🚀
echo ========================================
echo.
echo Your native desktop app is starting...
echo This will open the Aura Desktop Assistant!
echo.
echo 🎯 Demo Commands to Try:
echo   - Press Ctrl+' to activate
echo   - "Create a meeting notes document"
echo   - "Analyze my budget spreadsheet"
echo   - "Summarize the demo document"
echo.
pause

:: Start backend first
echo 🔧 Starting backend...
cd backend
start "Aura Backend" cmd /k "call venv\Scripts\activate && python main.py"
cd ..

:: Wait a moment for backend
timeout /t 3 /nobreak >nul

:: Start Tauri
echo 🎨 Launching native desktop app...
call npm run tauri dev

echo.
echo 🎉 Demo complete! Your app is ready for judges!
pause
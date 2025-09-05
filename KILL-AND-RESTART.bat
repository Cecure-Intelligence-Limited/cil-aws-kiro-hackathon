@echo off
echo ========================================
echo Killing Previous Processes and Restarting
echo ========================================
echo.

echo Killing any existing Vite/Node processes...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im npm.exe >nul 2>&1

echo Waiting for ports to free up...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo LAUNCHING AURA DEMO
echo ========================================
echo.
echo DEMO INSTRUCTIONS:
echo 1. Wait for Tauri app to open
echo 2. Press Ctrl+' to activate overlay
echo 3. Try these voice commands:
echo    - "Create a meeting notes document"
echo    - "Analyze my sample budget spreadsheet"
echo    - "Summarize the demo document"
echo.
echo Starting Aura frontend...

npm run tauri:dev
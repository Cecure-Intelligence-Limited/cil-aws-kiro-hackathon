@echo off
echo 🔧 Installing Dependencies Manually
echo ==================================

echo Installing core React dependencies...
call npm install react@^18.2.0 react-dom@^18.2.0
if %errorlevel% neq 0 goto :error

echo Installing XState...
call npm install xstate@^5.8.0 @xstate/react@^4.1.0
if %errorlevel% neq 0 goto :error

echo Installing Tauri API...
call npm install @tauri-apps/api@^1.5.3
if %errorlevel% neq 0 goto :error

echo Installing build tools...
call npm install --save-dev @vitejs/plugin-react@^4.2.1 vite@^5.1.6 typescript@^5.2.2
if %errorlevel% neq 0 goto :error

echo Installing Tauri CLI...
call npm install --save-dev @tauri-apps/cli@^1.5.10
if %errorlevel% neq 0 goto :error

echo Installing additional tools...
call npm install --save-dev tailwindcss@^3.4.1 autoprefixer@^10.4.18 postcss@^8.4.35
if %errorlevel% neq 0 goto :error

echo ✅ All dependencies installed successfully!
goto :end

:error
echo ❌ Installation failed. Try running individual commands manually.
pause
exit /b 1

:end
echo 🎉 Ready to start Aura!
pause
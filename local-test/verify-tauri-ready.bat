@echo off
echo ========================================
echo TAURI READINESS CHECK
echo ========================================
echo.

set "ERRORS=0"

:: Check Rust
echo Checking Rust...
rustc --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Rust not found
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('rustc --version') do echo ✅ Rust: %%i
)

:: Check Cargo
echo Checking Cargo...
cargo --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Cargo not found
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('cargo --version') do echo ✅ Cargo: %%i
)

:: Check Visual Studio Build Tools
echo Checking Visual Studio Build Tools...
where cl >nul 2>&1
if errorlevel 1 (
    echo ❌ Visual Studio Build Tools not found in PATH
    echo 💡 You may need to run from "Developer Command Prompt"
    set /a ERRORS+=1
) else (
    echo ✅ Visual Studio Build Tools found
)

:: Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo ✅ Node.js: %%i
)

:: Check Tauri CLI
echo Checking Tauri CLI...
call npm list -g @tauri-apps/cli >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Tauri CLI not installed globally
    echo 💡 Will use local version
) else (
    echo ✅ Tauri CLI installed globally
)

:: Test simple Rust compilation
echo Testing Rust compilation...
cd /d "%~dp0\.."
cd src-tauri
cargo check >nul 2>&1
if errorlevel 1 (
    echo ❌ Rust compilation test failed
    echo 💡 Run fix-tauri-completely.bat first
    set /a ERRORS+=1
) else (
    echo ✅ Rust compilation test passed
)

cd ..

echo.
if %ERRORS% equ 0 (
    echo ========================================
    echo TAURI STATUS: READY FOR HACKATHON! 🏆
    echo ========================================
    echo.
    echo 🚀 You can now run:
    echo    cd local-test
    echo    .\setup-and-test.bat
    echo.
    echo Your desktop app will work perfectly!
) else (
    echo ========================================
    echo TAURI STATUS: NEEDS SETUP ⚠️
    echo ========================================
    echo.
    echo 🔧 Run this first:
    echo    cd local-test
    echo    .\fix-tauri-completely.bat
    echo.
    echo Then try again.
)

pause
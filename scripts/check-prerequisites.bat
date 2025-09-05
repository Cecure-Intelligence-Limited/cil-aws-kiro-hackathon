@echo off
echo 🔍 Checking Prerequisites for Aura Desktop Assistant
echo ================================================

echo.
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Node.js: 
    node --version
) else (
    echo ❌ Node.js not found. Please install from https://nodejs.org/
    goto :error
)

echo.
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Python: 
    python --version
) else (
    echo ❌ Python not found. Please install from https://python.org/
    goto :error
)

echo.
echo Checking Rust...
rustc --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Rust: 
    rustc --version
) else (
    echo ❌ Rust not found. Please install from https://rustup.rs/
    goto :error
)

echo.
echo 🎉 All prerequisites are installed!
echo You're ready to run Aura Desktop Assistant.
goto :end

:error
echo.
echo ⚠️  Please install missing prerequisites and try again.
exit /b 1

:end
pause
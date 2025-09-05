@echo off
echo 🛠️  Installing Prerequisites for Aura Desktop Assistant
echo ===================================================

echo.
echo Checking if winget is available...
winget --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Winget is available, using it to install prerequisites
    goto :winget_install
) else (
    echo ⚠️  Winget not available, will provide manual instructions
    goto :manual_install
)

:winget_install
echo.
echo Installing Node.js...
winget install OpenJS.NodeJS
if %errorlevel% == 0 (
    echo ✅ Node.js installed
) else (
    echo ⚠️  Node.js installation may have failed
)

echo.
echo Installing Rust...
winget install Rustlang.Rustup
if %errorlevel% == 0 (
    echo ✅ Rust installed
) else (
    echo ⚠️  Rust installation may have failed
)

echo.
echo 🎉 Installation complete!
echo Please close and reopen your command prompt, then run:
echo   scripts\check-prerequisites.bat
goto :end

:manual_install
echo.
echo Please install the following manually:
echo.
echo 1. Node.js (LTS version):
echo    https://nodejs.org/
echo    Download and run the installer
echo.
echo 2. Rust:
echo    https://rustup.rs/
echo    Download rustup-init.exe and run it
echo.
echo After installation:
echo 1. Close and reopen your command prompt
echo 2. Run: scripts\check-prerequisites.bat
goto :end

:end
pause
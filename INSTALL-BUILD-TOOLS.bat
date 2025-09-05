@echo off
echo ========================================
echo Installing Visual Studio Build Tools
echo ========================================
echo.
echo This will install the required build tools for Tauri compilation.
echo.

:: Check if winget is available
winget --version >nul 2>&1
if errorlevel 1 (
    echo Winget not available, using manual download...
    goto :manual_install
)

echo Using winget to install Visual Studio Build Tools...
echo.
echo Installing Microsoft.VisualStudio.2022.BuildTools...
winget install Microsoft.VisualStudio.2022.BuildTools --accept-package-agreements --accept-source-agreements

if errorlevel 1 (
    echo Winget installation failed, trying manual download...
    goto :manual_install
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Please restart your terminal and run:
echo   .\KILL-AND-RESTART.bat
echo.
pause
exit /b 0

:manual_install
echo.
echo ========================================
echo Manual Installation Required
echo ========================================
echo.
echo Please follow these steps:
echo.
echo 1. Open this URL in your browser:
echo    https://visualstudio.microsoft.com/downloads/
echo.
echo 2. Scroll down to "Tools for Visual Studio 2022"
echo.
echo 3. Download "Build Tools for Visual Studio 2022"
echo.
echo 4. Run the installer and select:
echo    - C++ build tools
echo    - Windows 10/11 SDK
echo    - MSVC v143 compiler toolset
echo.
echo 5. After installation, restart your terminal
echo.
echo 6. Run: .\KILL-AND-RESTART.bat
echo.
echo Opening download page...
start https://visualstudio.microsoft.com/downloads/
echo.
pause
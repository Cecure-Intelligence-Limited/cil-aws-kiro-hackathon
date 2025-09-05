@echo off
echo ========================================
echo VISUAL STUDIO BUILD TOOLS INSTALLER
echo ========================================

echo 📋 This script will help you install Visual Studio Build Tools
echo 🔧 Required for Tauri Rust compilation on Windows

echo 🌐 Opening Visual Studio downloads page...
start https://visualstudio.microsoft.com/downloads/

echo.
echo 📋 INSTALLATION INSTRUCTIONS:
echo 1. Download "Build Tools for Visual Studio 2022"
echo 2. Run the installer
echo 3. Select "C++ build tools" workload
echo 4. Make sure these components are selected:
echo    - MSVC v143 - VS 2022 C++ x64/x86 build tools
echo    - Windows 11 SDK (latest version)
echo    - CMake tools for Visual Studio
echo.
echo 💡 Alternative: Install Visual Studio Community 2022
echo    and select "Desktop development with C++" workload
echo.
echo ⏳ After installation, restart your command prompt
echo    and run: npm run tauri dev
echo.

pause
@echo off
echo ========================================
echo RUNNING TAURI WITH PROPER ENVIRONMENT
echo ========================================

echo 🔧 Setting up Visual Studio environment...

REM Find and run vcvarsall.bat
set "VCVARSALL_2022=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
set "VCVARSALL_2019=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"

if exist "%VCVARSALL_2022%" (
    echo ✅ Found Visual Studio 2022 Build Tools
    call "%VCVARSALL_2022%" x64
    goto :run_tauri
)

if exist "%VCVARSALL_2019%" (
    echo ✅ Found Visual Studio 2019 Build Tools
    call "%VCVARSALL_2019%" x64
    goto :run_tauri
)

echo ❌ Could not find vcvarsall.bat
echo 💡 Trying to continue anyway...

:run_tauri
echo.
echo 🚀 Starting Tauri development server...
cd ..
npm run tauri dev
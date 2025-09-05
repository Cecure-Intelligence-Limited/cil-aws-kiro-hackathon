@echo off
echo ========================================
echo Setting up Visual Studio Environment
echo ========================================

REM Find Visual Studio Build Tools
set "VS_PATH="
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
    echo ✅ Found Visual Studio Build Tools 2022
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
    echo ✅ Found Visual Studio Community 2022
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    set "VS_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat"
    echo ✅ Found Visual Studio Professional 2022
)

if "%VS_PATH%"=="" (
    echo ❌ Visual Studio not found
    echo Please install Visual Studio Build Tools 2022 with C++ workload
    pause
    exit /b 1
)

echo 🔧 Setting up Visual Studio environment...
call "%VS_PATH%" x64

echo 🧪 Testing compiler...
where cl.exe >nul 2>&1
if errorlevel 1 (
    echo ❌ Compiler not found after setup
    exit /b 1
) else (
    echo ✅ Compiler found: 
    where cl.exe
)

echo 🧪 Testing linker...
where link.exe >nul 2>&1
if errorlevel 1 (
    echo ❌ Linker not found after setup
    exit /b 1
) else (
    echo ✅ Linker found:
    where link.exe
)

echo ✅ Visual Studio environment ready!
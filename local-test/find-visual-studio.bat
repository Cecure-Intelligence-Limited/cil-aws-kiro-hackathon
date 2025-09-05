@echo off
echo ========================================
echo FINDING VISUAL STUDIO INSTALLATION
echo ========================================

echo 🔍 Searching for Visual Studio installations...

REM Check common Visual Studio paths
set "VS2022_ENTERPRISE=C:\Program Files\Microsoft Visual Studio\2022\Enterprise"
set "VS2022_PROFESSIONAL=C:\Program Files\Microsoft Visual Studio\2022\Professional"
set "VS2022_COMMUNITY=C:\Program Files\Microsoft Visual Studio\2022\Community"
set "VS2022_BUILDTOOLS=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
set "VS2019_ENTERPRISE=C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise"
set "VS2019_PROFESSIONAL=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional"
set "VS2019_COMMUNITY=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community"

echo.
echo 🔍 Checking Visual Studio 2022 installations...
if exist "%VS2022_ENTERPRISE%" (
    echo ✅ Found: Visual Studio 2022 Enterprise
    echo    Path: %VS2022_ENTERPRISE%
    set "FOUND_VS=%VS2022_ENTERPRISE%"
)
if exist "%VS2022_PROFESSIONAL%" (
    echo ✅ Found: Visual Studio 2022 Professional
    echo    Path: %VS2022_PROFESSIONAL%
    set "FOUND_VS=%VS2022_PROFESSIONAL%"
)
if exist "%VS2022_COMMUNITY%" (
    echo ✅ Found: Visual Studio 2022 Community
    echo    Path: %VS2022_COMMUNITY%
    set "FOUND_VS=%VS2022_COMMUNITY%"
)
if exist "%VS2022_BUILDTOOLS%" (
    echo ✅ Found: Visual Studio 2022 Build Tools
    echo    Path: %VS2022_BUILDTOOLS%
    set "FOUND_VS=%VS2022_BUILDTOOLS%"
)

echo.
echo 🔍 Checking Visual Studio 2019 installations...
if exist "%VS2019_ENTERPRISE%" (
    echo ✅ Found: Visual Studio 2019 Enterprise
    echo    Path: %VS2019_ENTERPRISE%
    set "FOUND_VS=%VS2019_ENTERPRISE%"
)
if exist "%VS2019_PROFESSIONAL%" (
    echo ✅ Found: Visual Studio 2019 Professional
    echo    Path: %VS2019_PROFESSIONAL%
    set "FOUND_VS=%VS2019_PROFESSIONAL%"
)
if exist "%VS2019_COMMUNITY%" (
    echo ✅ Found: Visual Studio 2019 Community
    echo    Path: %VS2019_COMMUNITY%
    set "FOUND_VS=%VS2019_COMMUNITY%"
)

if defined FOUND_VS (
    echo.
    echo ✅ Visual Studio found at: %FOUND_VS%
    echo.
    echo 🔍 Looking for vcvarsall.bat...
    if exist "%FOUND_VS%\VC\Auxiliary\Build\vcvarsall.bat" (
        echo ✅ Found vcvarsall.bat
        echo    Path: %FOUND_VS%\VC\Auxiliary\Build\vcvarsall.bat
        echo %FOUND_VS%\VC\Auxiliary\Build\vcvarsall.bat > vs_path.txt
    ) else (
        echo ❌ vcvarsall.bat not found
    )
) else (
    echo ❌ No Visual Studio installation found
    echo.
    echo 💡 Please install Visual Studio 2022 Community with C++ workload
    echo    Download from: https://visualstudio.microsoft.com/downloads/
)

echo.
echo ========================================
echo SEARCH COMPLETE
echo ========================================
pause
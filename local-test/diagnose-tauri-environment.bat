@echo off
echo ========================================
echo TAURI ENVIRONMENT DIAGNOSIS
echo ========================================

echo 🔍 Checking Rust installation...
rustc --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Rust not found
    goto :end
) else (
    echo ✅ Rust found
)

echo.
echo 🔍 Checking Rust toolchain...
rustup show

echo.
echo 🔍 Checking for Visual Studio components...
where cl.exe
if %ERRORLEVEL% neq 0 (
    echo ❌ cl.exe not found in PATH
) else (
    echo ✅ cl.exe found
    cl.exe 2>&1 | findstr "Microsoft"
)

echo.
echo 🔍 Checking for link.exe...
where link.exe
if %ERRORLEVEL% neq 0 (
    echo ❌ link.exe not found in PATH
) else (
    echo ✅ link.exe found
    link.exe 2>&1 | findstr "Microsoft"
)

echo.
echo 🔍 Checking environment variables...
echo VCINSTALLDIR: %VCINSTALLDIR%
echo WindowsSdkDir: %WindowsSdkDir%
echo PATH (Visual Studio related):
echo %PATH% | findstr /i "visual studio"
echo %PATH% | findstr /i "microsoft"

echo.
echo 🔍 Checking Tauri CLI...
cargo tauri --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Tauri CLI not found
) else (
    echo ✅ Tauri CLI found
)

echo.
echo 🔍 Checking Node.js and npm...
node --version
npm --version

:end
echo.
echo ========================================
echo DIAGNOSIS COMPLETE
echo ========================================
pause
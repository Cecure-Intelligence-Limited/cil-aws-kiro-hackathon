@echo off
echo ========================================
echo FIXING RUST TOOLCHAIN FOR TAURI
echo ========================================

echo 🔧 Checking current Rust installation...
rustc --version
if %ERRORLEVEL% neq 0 (
    echo ❌ Rust not found. Please install Rust first from https://rustup.rs/
    pause
    exit /b 1
)

echo 🔧 Updating Rust toolchain...
rustup update

echo 🔧 Adding MSVC target...
rustup target add x86_64-pc-windows-msvc

echo 🔧 Checking for Visual Studio Build Tools...
where cl.exe >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Visual Studio Build Tools not found in PATH
    echo 📋 Please install one of the following:
    echo    1. Visual Studio 2022 Community (with C++ workload)
    echo    2. Visual Studio Build Tools 2022
    echo    3. Or run this in a Visual Studio Developer Command Prompt
    echo.
    echo 🌐 Download from: https://visualstudio.microsoft.com/downloads/
    echo.
    echo 💡 Alternative: Use the GNU toolchain instead
    echo    Run: rustup default stable-x86_64-pc-windows-gnu
    pause
    exit /b 1
)

echo ✅ Visual Studio Build Tools found
echo 🔧 Setting up Rust for MSVC...
rustup default stable-x86_64-pc-windows-msvc

echo 🧹 Cleaning previous Tauri builds...
cd ..
if exist "src-tauri\target" rmdir /s /q "src-tauri\target"

echo ✅ Rust toolchain setup complete!
echo 📋 You can now run: npm run tauri dev
pause
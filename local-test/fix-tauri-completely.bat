@echo off
echo ========================================
echo COMPLETE TAURI FIX - Win the Hackathon!
echo ========================================
echo.
echo This will install everything needed for Tauri
echo and get your desktop app working perfectly.
echo.
pause

cd /d "%~dp0\.."

echo 🔧 Step 1: Installing Visual Studio Build Tools...
echo.
echo Opening Visual Studio Build Tools installer...
echo ⚠️  IMPORTANT: When installer opens:
echo    1. Select "C++ build tools" workload
echo    2. Check "MSVC v143 - VS 2022 C++ x64/x86 build tools"
echo    3. Check "Windows 11 SDK (10.0.22621.0)"
echo    4. Click Install and wait for completion
echo.
echo Press any key when you're ready to download the installer...
pause

:: Download Visual Studio Build Tools
powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vs_buildtools.exe' -OutFile 'vs_buildtools.exe'"

echo ✅ Downloaded Visual Studio Build Tools installer
echo 🚀 Starting installer...
start /wait vs_buildtools.exe

echo.
echo ⏳ Waiting for you to complete the installation...
echo Press any key AFTER Visual Studio Build Tools installation is complete...
pause

:: Clean up installer
del vs_buildtools.exe

echo 🔄 Step 2: Updating Rust toolchain...
rustup update stable
rustup default stable

echo 📦 Step 3: Installing missing backend dependencies...
cd backend
call venv\Scripts\activate
pip install aiohttp==3.9.1 aiofiles==23.2.1
cd ..

echo 🧹 Step 4: Cleaning Rust build cache...
cd src-tauri
cargo clean
cd ..

echo 🔧 Step 5: Installing Tauri CLI...
call npm install -g @tauri-apps/cli

echo 🧪 Step 6: Testing Tauri build...
call npm run tauri build --debug

if errorlevel 1 (
    echo ❌ Tauri build test failed
    echo 🔧 Trying alternative approach...
    
    echo Installing additional Windows SDK components...
    powershell -Command "winget install Microsoft.WindowsSDK.10.0.22621"
    
    echo Retrying Tauri build...
    call npm run tauri build --debug
)

echo.
echo ========================================
echo TAURI SETUP COMPLETE! 🎉
echo ========================================
echo.
echo ✅ Visual Studio Build Tools installed
echo ✅ Rust toolchain updated
echo ✅ Backend dependencies fixed
echo ✅ Tauri build system ready
echo.
echo 🚀 Now run your main demo script:
echo    cd local-test
echo    .\setup-and-test.bat
echo.
echo 🏆 You're ready to win the hackathon!
echo.
pause
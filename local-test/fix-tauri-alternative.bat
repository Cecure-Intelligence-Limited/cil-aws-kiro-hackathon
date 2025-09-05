@echo off
echo ========================================
echo ALTERNATIVE TAURI FIX (GNU TOOLCHAIN)
echo ========================================

echo 🔧 This will switch to GNU toolchain (doesn't require Visual Studio)
echo ⚠️  Note: GNU builds may be slightly larger but work without MSVC

echo 🔧 Installing GNU toolchain...
rustup toolchain install stable-x86_64-pc-windows-gnu
rustup default stable-x86_64-pc-windows-gnu

echo 🔧 Adding GNU target...
rustup target add x86_64-pc-windows-gnu

echo 🧹 Cleaning previous builds...
cd ..
if exist "src-tauri\target" rmdir /s /q "src-tauri\target"

echo 🔧 Testing Rust compilation...
rustc --version
rustc --print target-list | findstr gnu

echo ✅ GNU toolchain setup complete!
echo 📋 You can now run: npm run tauri dev
pause
@echo off
echo 🔍 Aura Installation Status Check
echo =================================

echo.
echo Checking prerequisites...

echo Node.js:
node --version 2>nul && echo ✅ Node.js installed || echo ❌ Node.js missing

echo NPM:
npm --version 2>nul && echo ✅ NPM installed || echo ❌ NPM missing

echo Python:
python --version 2>nul && echo ✅ Python installed || echo ❌ Python missing

echo Rust:
rustc --version 2>nul && echo ✅ Rust installed || echo ❌ Rust missing

echo.
echo Checking project files...

if exist package.json (echo ✅ package.json found) else (echo ❌ package.json missing)
if exist .env (echo ✅ .env file found) else (echo ❌ .env file missing)
if exist backend\main.py (echo ✅ Backend found) else (echo ❌ Backend missing)
if exist src-tauri\src\main.rs (echo ✅ Tauri source found) else (echo ❌ Tauri source missing)

echo.
echo Checking dependencies...
if exist node_modules (echo ✅ Node modules installed) else (echo ❌ Node modules missing - run: npm install)
if exist backend\venv (echo ✅ Python venv found) else (echo ❌ Python venv missing)

echo.
echo 📋 Summary:
echo - If you see ❌ Rust missing: Install from https://rustup.rs/
echo - If you see ❌ Node modules missing: Run 'npm install'
echo - If you see ❌ Python venv missing: Run setup script

pause
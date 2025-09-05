@echo off
echo 🛠️  Setting up Aura Desktop Assistant for Local Testing
echo =====================================================

echo.
echo 1. Creating environment file...
if not exist .env (
    copy .env.template .env
    echo ✅ Created .env file from template
) else (
    echo ⚠️  .env file already exists
)

echo.
echo 2. Installing Node.js dependencies...
call npm install
if %errorlevel% == 0 (
    echo ✅ Node.js dependencies installed
) else (
    echo ❌ Failed to install Node.js dependencies
    goto :error
)

echo.
echo 3. Setting up Python backend...
cd backend
if not exist venv (
    python -m venv venv
    echo ✅ Created Python virtual environment
) else (
    echo ⚠️  Python virtual environment already exists
)

call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% == 0 (
    echo ✅ Python dependencies installed
) else (
    echo ❌ Failed to install Python dependencies
    goto :error
)

cd ..

echo.
echo 4. Creating test data directories...
if not exist documents mkdir documents
if not exist data mkdir data
if not exist temp mkdir temp
echo ✅ Test directories created

echo.
echo 🎉 Setup complete! 
echo.
echo Next steps:
echo 1. Edit .env file with your DATA_DIR path
echo 2. Run: scripts\start-aura.bat
echo 3. Press Ctrl+' to activate Aura
goto :end

:error
echo.
echo ❌ Setup failed. Please check the errors above.
exit /b 1

:end
pause
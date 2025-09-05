@echo off
echo ========================================
echo DEBUG: Aura Setup Test
echo ========================================
echo.

:: Navigate to project root
echo DEBUG: Navigating to project root...
cd /d "%~dp0\.."
echo DEBUG: Current directory: %CD%

:: Test npm install
echo DEBUG: Testing npm install...
call npm install
echo DEBUG: npm install exit code: %ERRORLEVEL%

if errorlevel 1 (
    echo DEBUG: npm install failed with error level %ERRORLEVEL%
    pause
    exit /b 1
) else (
    echo DEBUG: npm install succeeded
)

:: Test backend directory
echo DEBUG: Checking backend directory...
if exist backend (
    echo DEBUG: Backend directory exists
    cd backend
    echo DEBUG: Changed to backend directory: %CD%
    
    :: Test Python venv creation
    echo DEBUG: Testing Python venv creation...
    if not exist venv (
        echo DEBUG: Creating virtual environment...
        python -m venv venv
        echo DEBUG: venv creation exit code: %ERRORLEVEL%
    ) else (
        echo DEBUG: Virtual environment already exists
    )
    
    :: Test activation
    echo DEBUG: Testing venv activation...
    call venv\Scripts\activate
    echo DEBUG: venv activation exit code: %ERRORLEVEL%
    
    cd ..
) else (
    echo DEBUG: Backend directory does not exist!
)

echo DEBUG: Script completed successfully
pause
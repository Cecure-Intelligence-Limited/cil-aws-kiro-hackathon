@echo off
echo 🔍 Checking Aura Configuration
echo =============================

echo.
echo Checking if .env file exists...
if exist .env (
    echo ✅ .env file found
) else (
    echo ❌ .env file not found
    echo Please run: copy .env.template .env
    goto :error
)

echo.
echo Reading DATA_DIR from .env...
for /f "tokens=2 delims==" %%a in ('findstr "DATA_DIR" .env') do set DATA_DIR=%%a

if defined DATA_DIR (
    echo ✅ DATA_DIR is set to: %DATA_DIR%
    
    echo.
    echo Checking if DATA_DIR exists...
    if exist "%DATA_DIR%" (
        echo ✅ DATA_DIR folder exists
    ) else (
        echo ⚠️  DATA_DIR folder doesn't exist, creating it...
        mkdir "%DATA_DIR%" 2>nul
        if exist "%DATA_DIR%" (
            echo ✅ Created DATA_DIR folder
        ) else (
            echo ❌ Failed to create DATA_DIR folder
            goto :error
        )
    )
) else (
    echo ❌ DATA_DIR not found in .env file
    echo Please edit .env and set DATA_DIR to your documents path
    goto :error
)

echo.
echo 🎉 Configuration looks good!
echo You can now run: scripts\start-aura.bat
goto :end

:error
echo.
echo ❌ Configuration needs attention. Please fix the issues above.
exit /b 1

:end
pause
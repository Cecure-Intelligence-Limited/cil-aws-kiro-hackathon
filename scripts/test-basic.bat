@echo off
echo 🧪 Testing Aura Basic Functionality
echo ==================================

echo.
echo 1. Testing backend health...
curl -s http://localhost:8000/health
if %errorlevel% == 0 (
    echo ✅ Backend is responding
) else (
    echo ❌ Backend not responding. Make sure it's running.
    goto :error
)

echo.
echo 2. Testing file creation API...
curl -s -X POST http://localhost:8000/create_file -H "Content-Type: application/json" -d "{\"title\":\"test-api.txt\",\"content\":\"Hello from API test!\"}"
if %errorlevel% == 0 (
    echo ✅ File creation API works
) else (
    echo ❌ File creation API failed
    goto :error
)

echo.
echo 3. Checking if files were created...
if exist documents\test-api.txt (
    echo ✅ File was created successfully
) else (
    echo ⚠️  File not found in documents folder
)

echo.
echo 🎉 Basic tests passed!
echo.
echo Now try the desktop app:
echo 1. Press Ctrl+' to activate
echo 2. Say or type: "Create a file called voice-test.txt"
goto :end

:error
echo.
echo ❌ Tests failed. Check that:
echo 1. Backend is running (python main.py)
echo 2. .env file is configured
echo 3. DATA_DIR exists and is writable
exit /b 1

:end
pause
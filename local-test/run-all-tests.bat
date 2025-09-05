@echo off
echo ========================================
echo Aura Desktop Assistant - Test Suite
echo ========================================
echo.

set "PASSED=0"
set "TOTAL=0"

:: Test 1: Backend API Tests
echo 🧪 Running Backend API Tests...
set /a TOTAL+=1
cd backend
call venv\Scripts\activate
python -m pytest tests/ -v --tb=short
if errorlevel 1 (
    echo ❌ Backend tests failed
) else (
    echo ✅ Backend tests passed
    set /a PASSED+=1
)
cd ..

:: Test 2: Frontend Component Tests
echo 🧪 Running Frontend Component Tests...
set /a TOTAL+=1
npm test -- --run --reporter=verbose
if errorlevel 1 (
    echo ❌ Frontend tests failed
) else (
    echo ✅ Frontend tests passed
    set /a PASSED+=1
)

:: Test 3: Integration Tests
echo 🧪 Running Integration Tests...
set /a TOTAL+=1
python local-test\test-integration.py
if errorlevel 1 (
    echo ❌ Integration tests failed
) else (
    echo ✅ Integration tests passed
    set /a PASSED+=1
)

:: Test 4: Performance Tests
echo 🧪 Running Performance Tests...
set /a TOTAL+=1
python local-test\test-performance.py
if errorlevel 1 (
    echo ❌ Performance tests failed
) else (
    echo ✅ Performance tests passed
    set /a PASSED+=1
)

:: Test 5: Security Tests
echo 🧪 Running Security Tests...
set /a TOTAL+=1
python local-test\test-security.py
if errorlevel 1 (
    echo ❌ Security tests failed
) else (
    echo ✅ Security tests passed
    set /a PASSED+=1
)

:: Summary
echo.
echo ========================================
echo Test Results Summary
echo ========================================
echo Tests Passed: %PASSED%/%TOTAL%
echo.

if %PASSED% equ %TOTAL% (
    echo 🎉 All tests passed! Aura is ready for demo.
    exit /b 0
) else (
    echo ⚠️  Some tests failed. Check output above for details.
    exit /b 1
)
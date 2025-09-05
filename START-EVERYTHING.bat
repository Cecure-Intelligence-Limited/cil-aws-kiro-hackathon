@echo off
echo 🚀 Starting Aura Desktop Assistant - Complete System
echo ================================================

echo.
echo 📁 Checking project structure...
if not exist "backend\documents" (
    echo Creating backend\documents folder...
    mkdir backend\documents
)

echo.
echo 📊 Checking sample data...
if not exist "backend\documents\sample-budget.csv" (
    echo Creating sample budget file...
    echo Employee_Name,Department,Base_Salary,Bonus,Benefits,Total_Monthly > backend\documents\sample-budget.csv
    echo John Smith,Engineering,8500,1200,850,10550 >> backend\documents\sample-budget.csv
    echo Sarah Johnson,Marketing,7200,800,720,8720 >> backend\documents\sample-budget.csv
    echo Mike Davis,Sales,6800,1500,680,8980 >> backend\documents\sample-budget.csv
    echo Lisa Chen,Engineering,9200,1000,920,11120 >> backend\documents\sample-budget.csv
    echo David Wilson,HR,6500,500,650,7650 >> backend\documents\sample-budget.csv
    echo Emma Brown,Finance,7800,900,780,9480 >> backend\documents\sample-budget.csv
    echo Alex Garcia,Engineering,8800,1100,880,10780 >> backend\documents\sample-budget.csv
    echo Rachel Lee,Marketing,6900,700,690,8290 >> backend\documents\sample-budget.csv
    echo Tom Anderson,Sales,7100,1400,710,9210 >> backend\documents\sample-budget.csv
    echo Maria Rodriguez,Finance,7500,800,750,9050 >> backend\documents\sample-budget.csv
)

echo.
echo 🔧 Installing Python dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo 🌐 Starting Backend API Server...
start "Backend API" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo 🧪 Testing API endpoints...
cd ..
python test-endpoints.py

echo.
echo 📱 Installing Frontend dependencies...
npm install
if errorlevel 1 (
    echo ❌ Failed to install npm dependencies
    pause
    exit /b 1
)

echo.
echo 🖥️ Starting Frontend Development Server...
start "Frontend Dev" cmd /k "npm run dev"

echo.
echo ⏳ Waiting for frontend to start...
timeout /t 3 /nobreak > nul

echo.
echo 🖥️ Starting Electron Desktop App...
start "Electron App" cmd /k "npm run electron"

echo.
echo ✅ All services started successfully!
echo.
echo 📋 Services Running:
echo   • Backend API: http://localhost:8000
echo   • Frontend Dev: http://localhost:5173  
echo   • Electron App: Desktop application
echo.
echo 💡 Try these commands in the app:
echo   • "Calculate total salary in my budget file"
echo   • "Update salary with 10%% increase"
echo   • "Add performance rating column"
echo.
echo Press any key to open the API documentation...
pause > nul
start http://localhost:8000/docs

echo.
echo 🎯 System is ready! Check the opened windows.
pause
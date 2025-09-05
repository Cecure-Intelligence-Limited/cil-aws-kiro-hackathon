#!/bin/bash

echo "Starting Aura Desktop Assistant Development Environment..."

echo ""
echo "[1/3] Starting Backend Server..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
BACKEND_PID=$!
cd ..

echo ""
echo "[2/3] Waiting for backend to start..."
sleep 5

echo ""
echo "[3/3] Starting Tauri Development..."
npm run tauri:dev

echo ""
echo "Development environment started!"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:1420"
echo "- Global Shortcut: Ctrl+' or Ctrl+Shift+A"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT
wait
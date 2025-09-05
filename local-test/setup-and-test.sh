#!/bin/bash
echo "========================================"
echo "Aura Desktop Assistant - Setup and Test"
echo "========================================"
echo ""
echo "This script will:"
echo "  1. Verify system prerequisites"
echo "  2. Install all dependencies"
echo "  3. Create demo data"
echo "  4. Launch comprehensive tests"
echo "  5. Start the desktop application"
echo ""
read -p "Press Enter to continue..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check prerequisites
echo "📋 Checking Prerequisites..."
./local-test/check-prerequisites.sh
if [ $? -ne 0 ]; then
    echo "❌ Prerequisites check failed"
    exit 1
fi

# Setup environment
echo "🌍 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.template .env
    echo "✅ Created .env configuration"
fi

# Create directories
mkdir -p documents data
echo "✅ Created project directories"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Frontend installation failed"
    exit 1
fi
echo "✅ Frontend dependencies installed"

# Setup backend
echo "🔧 Setting up backend..."
cd backend
if [ ! -d venv ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Backend installation failed"
    exit 1
fi
echo "✅ Backend dependencies installed"

# Create demo data
echo "📊 Creating demo data..."
cd ..
python3 local-test/create-demo-data.py
echo "✅ Demo data created"

# Run tests
echo "🧪 Running test suite..."
./local-test/run-all-tests.sh
if [ $? -ne 0 ]; then
    echo "⚠️  Some tests failed, but continuing with demo"
fi

# Start backend
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
echo "✅ Backend starting (PID: $BACKEND_PID)"

# Wait for backend
echo "⏳ Waiting for backend to initialize..."
sleep 8

# Test backend connection
cd ..
python3 local-test/test-backend.py
if [ $? -ne 0 ]; then
    echo "⚠️  Backend connection test failed, but continuing"
fi

# Launch application
echo "🎨 Launching Aura Desktop Assistant..."
echo ""
echo "========================================"
echo "DEMO READY!"
echo "========================================"
echo ""
echo "📋 Test Instructions:"
echo "  1. Wait for the application to load"
echo "  2. Press Ctrl+' to activate Aura overlay"
echo "  3. Try these voice commands:"
echo "     - 'Create a meeting notes document'"
echo "     - 'Analyze my sample budget spreadsheet'"
echo "     - 'Summarize the demo document'"
echo ""
echo "🎯 Success Criteria:"
echo "  - Voice commands process in under 2 seconds"
echo "  - Files created with exact content"
echo "  - Calculations are accurate"
echo "  - UI is smooth and responsive"
echo ""

npm run tauri:dev

echo ""
echo "🎉 Demo session complete!"
echo "Check the documents folder for created files."
echo ""
echo "🛑 Cleaning up..."
kill $BACKEND_PID 2>/dev/null
echo "✅ Backend stopped"
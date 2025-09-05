#!/bin/bash
echo "========================================"
echo "Aura Prerequisites Check"
echo "========================================"
echo ""

ERRORS=0

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js not found"
    echo "   Please install Node.js 18+ from https://nodejs.org/"
    ((ERRORS++))
fi

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
elif command -v python &> /dev/null; then
    echo "✅ Python: $(python --version)"
else
    echo "❌ Python not found"
    echo "   Please install Python 3.9+ from https://python.org/"
    ((ERRORS++))
fi

# Check Rust (optional for web demo)
echo "Checking Rust..."
if command -v rustc &> /dev/null; then
    echo "✅ Rust: $(rustc --version)"
else
    echo "⚠️  Rust not found (required for native desktop app)"
    echo "   Install from https://rustup.rs/ for full experience"
fi

# Check Git
echo "Checking Git..."
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version)"
else
    echo "⚠️  Git not found (recommended for development)"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "========================================"
    echo "Prerequisites Status: READY ✅"
    echo "========================================"
    exit 0
else
    echo "========================================"
    echo "Prerequisites Status: MISSING REQUIREMENTS ❌"
    echo "========================================"
    echo ""
    echo "Please install the missing prerequisites and try again."
    exit 1
fi
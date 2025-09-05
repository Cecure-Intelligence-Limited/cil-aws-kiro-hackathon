#!/bin/bash
# Aura Desktop Assistant MCP Server for Unix/Linux/macOS

set -e

# Set environment variables
export AURA_API_URL="${AURA_API_URL:-http://localhost:8000}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export NODE_ENV="${NODE_ENV:-development}"

# Change to the project directory
cd "$(dirname "$0")/.."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Please install Node.js from https://nodejs.org/" >&2
    exit 1
fi

# Check if tsx is available
if ! node -e "require('tsx')" &> /dev/null; then
    echo "Installing tsx..." >&2
    npm install -g tsx
fi

# Start the MCP server
echo "Starting Aura Desktop Assistant MCP Server..." >&2
node -r tsx/cjs src/services/mcpStandalone.ts
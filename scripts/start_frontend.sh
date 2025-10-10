#!/bin/bash

# Wealth Warriors - Frontend Startup Script
# Starts the React frontend development server

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Wealth Warriors - Frontend Startup Script             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Define frontend path
FRONTEND_PATH="./frontend/web/frontend-web/web-test"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_PATH" ]; then
    echo "❌ Error: Frontend directory not found at $FRONTEND_PATH"
    exit 1
fi

echo "[1/3] Navigating to frontend directory..."
cd "$FRONTEND_PATH"
echo "✓ Current directory: $(pwd)"
echo ""

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in $FRONTEND_PATH"
    exit 1
fi

echo "[2/3] Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi
echo ""

echo "[3/3] Starting development server..."
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🚀 Starting React Development Server"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  📍 Frontend will be available at: http://localhost:5173"
echo "  📍 Backend API should be at: http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Start the development server
npm run dev

#!/bin/bash

# Wealth Warriors - Start All Services
# This script starts the backend API server and frontend development server

set -e  # Exit on error

echo "🚀 Starting Wealth Warriors Services..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/lib/python*/site-packages/fastapi/__init__.py" ]; then
    echo -e "${YELLOW}⚠️  Dependencies not installed. Installing...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Kill any existing processes on ports 8000 and 3000
echo -e "${BLUE}🔍 Checking for existing processes...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  Killed process on port 8000" || echo "  Port 8000 is free"
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "  Killed process on port 3000" || echo "  Port 3000 is free"
echo ""

# Start backend server in background
echo -e "${BLUE}🔧 Starting Backend API Server...${NC}"
export PYTHONPATH=.
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo "  Logs: backend.log"
echo ""

# Wait for backend to start
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Save PIDs to file for easy cleanup
echo $BACKEND_PID > .pids

echo -e "${GREEN}✅ Backend service is running!${NC}"
echo ""
echo -e "${BLUE}📝 Access the application:${NC}"
echo "  Frontend: Open frontend/public/index.html in your browser"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}📊 View logs:${NC}"
echo "  Backend: tail -f backend.log"
echo ""
echo -e "${BLUE}🛑 Stop all services:${NC}"
echo "  ./stop_all.sh"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop monitoring (backend will continue running)${NC}"

# Keep script running and show logs
trap 'echo ""; echo "Backend is still running in background. Run ./stop_all.sh to stop it."; exit 0' INT

tail -f backend.log

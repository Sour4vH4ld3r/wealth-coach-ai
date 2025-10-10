#!/bin/bash

# Wealth Warriors - Stop All Services
# This script stops the backend API server and frontend development server

echo "🛑 Stopping Wealth Warriors Backend..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Kill process on port 8000
echo "Stopping Backend (port 8000)..."
if lsof -ti:8000 | xargs kill -9 2>/dev/null; then
    echo -e "${GREEN}✓ Backend stopped${NC}"
else
    echo "  No process running on port 8000"
fi

# Clean up PID file if it exists
if [ -f .pids ]; then
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
    done < .pids
    rm .pids
fi

# Clean up log files (optional)
if [ -f backend.log ]; then
    echo ""
    echo "Log file available:"
    echo "  backend.log"
    echo ""
    read -p "Delete log file? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f backend.log
        echo -e "${GREEN}✓ Log file deleted${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ Backend stopped${NC}"

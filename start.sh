#!/bin/bash

###############################################################################
# Wealth Coach AI Assistant - Startup Script
###############################################################################
# This script starts the complete Wealth Coach AI Assistant stack including:
# - Redis (optional caching layer)
# - Backend API server
# - Knowledge base loading
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Wealth Coach AI Assistant - Startup Script            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

###############################################################################
# 1. Check Python Virtual Environment
###############################################################################
echo -e "${YELLOW}[1/6] Checking Python environment...${NC}"

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

###############################################################################
# 2. Install/Update Dependencies
###############################################################################
echo -e "${YELLOW}[2/6] Checking dependencies...${NC}"

if ! pip list | grep -q "fastapi"; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi
echo ""

###############################################################################
# 3. Check/Start Redis (Optional)
###############################################################################
echo -e "${YELLOW}[3/6] Checking Redis...${NC}"

if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis is already running${NC}"
    else
        echo "Starting Redis server..."
        redis-server --daemonize yes
        sleep 2
        if redis-cli ping &> /dev/null; then
            echo -e "${GREEN}✓ Redis started successfully${NC}"
        else
            echo -e "${YELLOW}⚠ Redis failed to start (will run without caching)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Redis not installed (optional - caching disabled)${NC}"
    echo "  Install with: brew install redis (macOS) or apt install redis (Linux)"
fi
echo ""

###############################################################################
# 4. Check Environment Configuration
###############################################################################
echo -e "${YELLOW}[4/6] Checking configuration...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found!${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please update .env with your API keys before proceeding${NC}"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit and configure .env..."
fi

# Check if OpenAI API key is set
if grep -q 'OPENAI_API_KEY=""' .env; then
    echo -e "${YELLOW}⚠ OpenAI API key not configured in .env${NC}"
    echo "  The assistant will use local fallback mode"
fi

echo -e "${GREEN}✓ Configuration loaded${NC}"
echo ""

###############################################################################
# 5. Load Knowledge Base (Optional)
###############################################################################
echo -e "${YELLOW}[5/6] Checking knowledge base...${NC}"

if [ ! -d "data/vector_store" ] || [ -z "$(ls -A data/vector_store 2>/dev/null)" ]; then
    echo "Knowledge base empty. Loading sample financial content..."
    python scripts/load_knowledge.py
    echo -e "${GREEN}✓ Knowledge base loaded${NC}"
else
    echo -e "${GREEN}✓ Knowledge base already populated${NC}"
    echo "  To reload: python scripts/load_knowledge.py"
fi
echo ""

###############################################################################
# 6. Start API Server
###############################################################################
echo -e "${YELLOW}[6/6] Starting API server...${NC}"
echo ""

export PYTHONPATH=.

echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 Starting Wealth Coach AI Assistant API Server${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  📍 API Server:       http://localhost:8000"
echo -e "  📚 API Docs:         http://localhost:8000/docs"
echo -e "  📖 ReDoc:            http://localhost:8000/redoc"
echo -e "  🔍 Health Check:     http://localhost:8000/health"
echo ""
echo -e "${YELLOW}  Press Ctrl+C to stop the server${NC}"
echo ""

# Start the server
uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info

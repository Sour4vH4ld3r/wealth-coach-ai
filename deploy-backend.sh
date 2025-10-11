#!/bin/bash

# =============================================================================
# Wealth Coach AI - Backend-Only Deployment Script
# =============================================================================

set -e

echo "🚀 Wealth Coach AI - Backend Deployment"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# =============================================================================
# Check if Docker is installed
# =============================================================================
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo ""
    echo "Install Docker with:"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo "  apt install docker-compose-plugin -y"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# =============================================================================
# Check if .env file exists
# =============================================================================
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo ""
    echo "Create .env file:"
    echo "  cp .env.template .env"
    echo "  nano .env"
    echo ""
    echo "Required variables:"
    echo "  - DATABASE_URL"
    echo "  - REDIS_URL"
    echo "  - OPENAI_API_KEY"
    echo "  - JWT_SECRET_KEY"
    exit 1
fi

echo -e "${GREEN}✅ .env file exists${NC}"

# =============================================================================
# Validate required environment variables
# =============================================================================
echo ""
echo "Checking environment variables..."

source .env

REQUIRED_VARS=(
    "DATABASE_URL"
    "REDIS_URL"
    "OPENAI_API_KEY"
    "JWT_SECRET_KEY"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Edit .env file and add missing variables"
    exit 1
fi

echo -e "${GREEN}✅ All required variables set${NC}"

# =============================================================================
# Stop existing containers
# =============================================================================
echo ""
echo "Stopping existing containers..."
docker compose -f docker-compose.backend.yml down 2>/dev/null || true
echo -e "${GREEN}✅ Stopped${NC}"

# =============================================================================
# Pull/Build images
# =============================================================================
echo ""
echo "Building backend image..."
docker compose -f docker-compose.backend.yml build

# =============================================================================
# Start backend
# =============================================================================
echo ""
echo "Starting backend..."
docker compose -f docker-compose.backend.yml up -d

# =============================================================================
# Wait for backend to be ready
# =============================================================================
echo ""
echo "Waiting for backend to be ready..."
sleep 10

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        break
    fi

    echo -n "."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo ""
    echo "Check logs:"
    echo "  docker compose -f docker-compose.backend.yml logs"
    exit 1
fi

# =============================================================================
# Get server IP
# =============================================================================
echo ""
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")

# =============================================================================
# Success message
# =============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Backend Deployed Successfully!                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo "🔗 API URL: http://${SERVER_IP}:8000"
echo "📖 API Docs: http://${SERVER_IP}:8000/docs"
echo "✅ Health Check: http://${SERVER_IP}:8000/health"
echo ""
echo "📊 Useful Commands:"
echo "  View logs:    docker compose -f docker-compose.backend.yml logs -f"
echo "  Stop:         docker compose -f docker-compose.backend.yml down"
echo "  Restart:      docker compose -f docker-compose.backend.yml restart"
echo "  Status:       docker compose -f docker-compose.backend.yml ps"
echo ""
echo -e "${YELLOW}⚠️  Don't forget to configure firewall:${NC}"
echo "  ufw allow 8000/tcp"
echo ""

#!/bin/bash

# =============================================================================
# Wealth Coach AI - Backend + Nginx Docker Deployment Script
# =============================================================================

set -e

echo "🚀 Wealth Coach AI - Backend + Nginx Deployment"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Check if Docker is installed
# =============================================================================
echo -e "${BLUE}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo ""
    echo "Install Docker with:"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo "  apt install docker-compose-plugin -y"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"
docker --version

# =============================================================================
# Check if .env file exists
# =============================================================================
echo ""
echo -e "${BLUE}Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo ""
    echo "Create .env file:"
    echo "  cp .env.template .env"
    echo "  nano .env"
    echo ""
    echo "Required variables:"
    echo "  - DATABASE_URL (Supabase)"
    echo "  - REDIS_URL (Upstash)"
    echo "  - OPENAI_API_KEY"
    echo "  - JWT_SECRET_KEY"
    exit 1
fi

echo -e "${GREEN}✅ .env file exists${NC}"

# =============================================================================
# Validate required environment variables
# =============================================================================
echo ""
echo -e "${BLUE}Validating environment variables...${NC}"

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
# Check for port conflicts
# =============================================================================
echo ""
echo -e "${BLUE}Checking port availability...${NC}"

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 1
    fi
    return 0
}

PORT_CONFLICTS=()

if ! check_port 80; then
    PORT_CONFLICTS+=("80 (HTTP)")
fi

if ! check_port 443; then
    PORT_CONFLICTS+=("443 (HTTPS)")
fi

if [ ${#PORT_CONFLICTS[@]} -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: The following ports are in use:${NC}"
    for port in "${PORT_CONFLICTS[@]}"; do
        echo "  - Port $port"
    done
    echo ""
    echo "Existing web servers detected. You may need to:"
    echo "  1. Stop existing web servers"
    echo "  2. Or configure Nginx to use different ports"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ Ports 80 and 443 are available${NC}"
fi

# =============================================================================
# Stop existing containers
# =============================================================================
echo ""
echo -e "${BLUE}Stopping existing containers...${NC}"
docker compose -f docker-compose.nginx.yml down 2>/dev/null || true
echo -e "${GREEN}✅ Stopped${NC}"

# =============================================================================
# Build images
# =============================================================================
echo ""
echo -e "${BLUE}Building Docker images...${NC}"
docker compose -f docker-compose.nginx.yml build --no-cache

# =============================================================================
# Start services
# =============================================================================
echo ""
echo -e "${BLUE}Starting services...${NC}"
docker compose -f docker-compose.nginx.yml up -d

# =============================================================================
# Wait for services to be ready
# =============================================================================
echo ""
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 15

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Services are healthy!${NC}"
        break
    fi

    echo -n "."
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Services failed to start${NC}"
    echo ""
    echo "Check logs:"
    echo "  docker compose -f docker-compose.nginx.yml logs"
    exit 1
fi

# =============================================================================
# Get server IP
# =============================================================================
echo ""
echo -e "${BLUE}Getting server information...${NC}"
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

# =============================================================================
# Display container status
# =============================================================================
echo ""
echo -e "${BLUE}Container Status:${NC}"
docker compose -f docker-compose.nginx.yml ps

# =============================================================================
# Success message
# =============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Deployment Successful!                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🔗 Access Your API:${NC}"
echo "   • HTTP: http://${SERVER_IP}/"
echo "   • Health: http://${SERVER_IP}/health"
echo "   • API Docs: http://${SERVER_IP}/docs"
echo ""
echo -e "${YELLOW}🔒 Next Steps (Optional):${NC}"
echo "   1. Point your domain to ${SERVER_IP}"
echo "   2. Setup SSL certificate (Let's Encrypt)"
echo "   3. Enable HTTPS in Nginx config"
echo "   4. Configure firewall: ufw allow 80/tcp && ufw allow 443/tcp"
echo ""
echo -e "${BLUE}📊 Useful Commands:${NC}"
echo "   View logs:    docker compose -f docker-compose.nginx.yml logs -f"
echo "   Stop:         docker compose -f docker-compose.nginx.yml down"
echo "   Restart:      docker compose -f docker-compose.nginx.yml restart"
echo "   Status:       docker compose -f docker-compose.nginx.yml ps"
echo ""
echo -e "${GREEN}✅ For full guide, see: NGINX_DOCKER_DEPLOY.md${NC}"
echo ""

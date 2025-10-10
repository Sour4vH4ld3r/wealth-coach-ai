#!/bin/bash
# =============================================================================
# PRODUCTION DEPLOYMENT SCRIPT
# Wealth Coach AI - Automated Production Deployment
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo ""
    echo "========================================================================"
    echo "  $1"
    echo "========================================================================"
    echo ""
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Do not run this script as root!"
    exit 1
fi

print_header "WEALTH COACH AI - PRODUCTION DEPLOYMENT"

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    exit 1
else
    print_success "Docker installed: $(docker --version)"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose not found. Please install Docker Compose first."
    exit 1
else
    print_success "Docker Compose installed: $(docker-compose --version)"
fi

# Step 2: Environment Configuration
print_header "Step 2: Environment Configuration"

if [ ! -f ".env" ]; then
    print_warning ".env file not found!"
    echo "Creating .env from .env.production.example..."

    if [ -f ".env.production.example" ]; then
        cp .env.production.example .env
        print_warning "Please configure .env with your production values"
        print_warning "Edit .env and update:"
        echo "  - DATABASE_URL"
        echo "  - REDIS_URL"
        echo "  - OPENAI_API_KEY"
        echo "  - JWT_SECRET_KEY"
        echo "  - CORS_ORIGINS"
        echo ""
        read -p "Press Enter after configuring .env..."
    else
        print_error ".env.production.example not found!"
        exit 1
    fi
else
    print_success ".env file found"
fi

# Step 3: Verify Critical Environment Variables
print_header "Step 3: Verifying Configuration"

source .env

required_vars=("DATABASE_URL" "REDIS_URL" "OPENAI_API_KEY" "JWT_SECRET_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
else
    print_success "All required environment variables configured"
fi

# Check if DEBUG is disabled
if [ "$DEBUG" = "true" ]; then
    print_error "DEBUG is enabled! Set DEBUG=false in .env for production"
    exit 1
else
    print_success "DEBUG mode is disabled"
fi

# Step 4: Create necessary directories
print_header "Step 4: Creating Directories"

mkdir -p logs
mkdir -p data/knowledge_base
mkdir -p config/nginx/ssl
mkdir -p backups

print_success "Directories created"

# Step 5: Build Docker images
print_header "Step 5: Building Docker Images"

echo "This may take several minutes..."
if docker-compose -f docker-compose.prod.yml build; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# Step 6: Pull external images
print_header "Step 6: Pulling External Images"

docker-compose -f docker-compose.prod.yml pull nginx prometheus grafana
print_success "External images pulled"

# Step 7: Stop existing containers
print_header "Step 7: Stopping Existing Containers"

if docker-compose -f docker-compose.prod.yml ps -q | grep -q .; then
    print_warning "Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down
    print_success "Existing containers stopped"
else
    print_success "No existing containers to stop"
fi

# Step 8: Start production services
print_header "Step 8: Starting Production Services"

if docker-compose -f docker-compose.prod.yml up -d; then
    print_success "Production services started"
else
    print_error "Failed to start production services"
    exit 1
fi

# Step 9: Wait for services to be ready
print_header "Step 9: Waiting for Services"

echo "Waiting for backend to be ready..."
sleep 10

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose -f docker-compose.prod.yml exec -T backend curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
        break
    else
        echo "Waiting for backend... (attempt $((attempt+1))/$max_attempts)"
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Backend failed to become healthy"
    echo "Check logs: docker-compose -f docker-compose.prod.yml logs backend"
    exit 1
fi

# Step 10: Display deployment status
print_header "Step 10: Deployment Status"

echo "Container Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
print_success "Production deployment completed successfully!"

# Step 11: Post-deployment instructions
print_header "Post-Deployment Instructions"

echo "1. Verify health check:"
echo "   curl http://localhost:8000/health"
echo ""
echo "2. View logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "3. Access services:"
echo "   - Backend API: http://localhost:8000"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000"
echo ""
echo "4. Load knowledge base (if not done):"
echo "   docker-compose -f docker-compose.prod.yml exec backend python load_knowledge_pgvector.py"
echo ""
echo "5. Configure SSL/HTTPS:"
echo "   - Install SSL certificates in config/nginx/ssl/"
echo "   - Update nginx configuration"
echo "   - Restart nginx: docker-compose -f docker-compose.prod.yml restart nginx"
echo ""
echo "6. Set up monitoring alerts in Grafana"
echo ""
echo "7. Configure automated backups"
echo ""

print_header "Deployment Complete! 🎉"

echo "For full deployment guide, see: PRODUCTION_DEPLOYMENT.md"
echo ""

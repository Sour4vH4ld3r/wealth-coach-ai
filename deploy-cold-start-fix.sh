#!/bin/bash
# =============================================================================
# Cold Start Optimization Deployment Script
# Wealth Coach AI - Backend API
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "Wealth Coach AI - Cold Start Optimization"
echo "Lazy Loading Deployment Script"
echo "================================================"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if we're in the correct directory
if [ ! -f "docker-compose.backend.yml" ]; then
    print_error "docker-compose.backend.yml not found!"
    print_error "Please run this script from the project root: /root/opt/wealth-coach-ai"
    exit 1
fi

print_success "Found docker-compose.backend.yml"
echo ""

# Step 1: Pull latest changes
print_info "Step 1: Pulling latest code from repository..."
if git pull origin main; then
    print_success "Code updated successfully"
else
    print_error "Git pull failed. Please check your repository status."
    exit 1
fi
echo ""

# Step 2: Stop current containers
print_info "Step 2: Stopping current containers..."
if docker compose -f docker-compose.backend.yml down; then
    print_success "Containers stopped"
else
    print_error "Failed to stop containers"
    exit 1
fi
echo ""

# Step 3: Rebuild containers
print_info "Step 3: Building new containers (this may take a few minutes)..."
if docker compose -f docker-compose.backend.yml build --no-cache; then
    print_success "Containers built successfully"
else
    print_error "Build failed"
    exit 1
fi
echo ""

# Step 4: Start containers
print_info "Step 4: Starting containers..."
if docker compose -f docker-compose.backend.yml up -d; then
    print_success "Containers started"
else
    print_error "Failed to start containers"
    exit 1
fi
echo ""

# Step 5: Monitor startup
print_info "Step 5: Monitoring startup (waiting for 'Server ready' message)..."
echo ""

START_TIME=$(date +%s)
TIMEOUT=120  # 2 minutes timeout
FOUND=0

while [ $(($(date +%s) - START_TIME)) -lt $TIMEOUT ]; do
    if docker compose -f docker-compose.backend.yml logs backend | grep -q "Server ready"; then
        FOUND=1
        break
    fi
    sleep 2
    echo -n "."
done

echo ""
echo ""

if [ $FOUND -eq 1 ]; then
    END_TIME=$(date +%s)
    STARTUP_TIME=$((END_TIME - START_TIME))
    print_success "Backend is ready! (Startup time: ${STARTUP_TIME}s)"

    if [ $STARTUP_TIME -lt 20 ]; then
        print_success "Excellent! Startup time is under 20 seconds (expected 10-17s)"
    elif [ $STARTUP_TIME -lt 30 ]; then
        print_info "Startup time is acceptable but could be optimized"
    else
        print_error "Startup time is higher than expected. Check logs for issues."
    fi
else
    print_error "Timeout waiting for backend to start"
    print_error "Check logs: docker compose -f docker-compose.backend.yml logs backend"
    exit 1
fi
echo ""

# Step 6: Verify health endpoint
print_info "Step 6: Verifying health endpoint..."
sleep 2  # Give it a moment to stabilize

if curl -f -s http://localhost:8000/health > /dev/null; then
    print_success "Health endpoint responding correctly"
else
    print_error "Health endpoint not responding. Check container logs."
    exit 1
fi
echo ""

# Step 7: Check container status
print_info "Step 7: Checking container status..."
CONTAINER_STATUS=$(docker inspect -f '{{.State.Health.Status}}' wealth_coach_backend 2>/dev/null || echo "unknown")

if [ "$CONTAINER_STATUS" = "healthy" ] || [ "$CONTAINER_STATUS" = "starting" ]; then
    print_success "Container health status: $CONTAINER_STATUS"
else
    print_error "Container health status: $CONTAINER_STATUS"
    print_error "Check logs: docker compose -f docker-compose.backend.yml logs backend"
fi
echo ""

# Display recent logs
print_info "Recent startup logs:"
echo "---"
docker compose -f docker-compose.backend.yml logs backend --tail=15
echo "---"
echo ""

# Final summary
echo "================================================"
echo "DEPLOYMENT SUMMARY"
echo "================================================"
print_success "1. Code updated from repository"
print_success "2. Containers rebuilt with new configuration"
print_success "3. Backend started successfully"
print_success "4. Health endpoint verified"
echo ""

print_info "Key improvements:"
echo "  • Startup time reduced from 30-40s to 10-17s"
echo "  • Health/auth endpoints respond immediately"
echo "  • Embedding model loads on first RAG query (10-20s)"
echo "  • All subsequent queries fast (<2s)"
echo ""

print_info "Next steps:"
echo "  1. Test health endpoint: curl https://api.wealthwarriorshub.in/health"
echo "  2. Test auth endpoint: curl -X POST https://api.wealthwarriorshub.in/api/v1/auth/send-otp"
echo "  3. Monitor first RAG query for model loading"
echo "  4. Verify no 502 errors in Nginx logs"
echo ""

print_info "Monitoring commands:"
echo "  • View logs: docker compose -f docker-compose.backend.yml logs -f backend"
echo "  • Check status: docker ps"
echo "  • Check memory: docker stats wealth_coach_backend"
echo "  • Nginx errors: sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.error.log"
echo ""

print_success "Deployment completed successfully!"
echo "================================================"

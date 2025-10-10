#!/bin/bash

# =============================================================================
# Wealth Coach AI - Excloud VPS Server Setup Script
# =============================================================================
# This script sets up an Excloud VPS for production deployment
# Run as: bash server-setup.sh
# =============================================================================

set -e

echo "🚀 Starting Wealth Coach AI Server Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# 1. System Updates
# =============================================================================
echo -e "${GREEN}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# =============================================================================
# 2. Install Docker
# =============================================================================
echo -e "${GREEN}🐳 Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${YELLOW}⚠️  Docker already installed${NC}"
fi

# =============================================================================
# 3. Install Docker Compose
# =============================================================================
echo -e "${GREEN}🔧 Installing Docker Compose...${NC}"
sudo apt install docker-compose-plugin -y

# =============================================================================
# 4. Install Required Tools
# =============================================================================
echo -e "${GREEN}🛠️  Installing required tools...${NC}"
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    ncdu \
    net-tools

# =============================================================================
# 5. Setup Firewall
# =============================================================================
echo -e "${GREEN}🔥 Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw reload

echo -e "${GREEN}✅ Firewall configured${NC}"

# =============================================================================
# 6. Create Application Directory
# =============================================================================
echo -e "${GREEN}📁 Creating application directory...${NC}"
sudo mkdir -p /opt/wealth-coach-ai
sudo chown $USER:$USER /opt/wealth-coach-ai

# =============================================================================
# 7. Clone Repository
# =============================================================================
echo -e "${GREEN}📥 Repository setup...${NC}"
if [ ! -d "/opt/wealth-coach-ai/.git" ]; then
    echo "Please clone your repository manually:"
    echo "cd /opt/wealth-coach-ai"
    echo "git clone https://github.com/Sour4vH4ld3r/wealth-coach-ai.git ."
else
    echo -e "${YELLOW}⚠️  Repository already exists${NC}"
fi

# =============================================================================
# 8. Setup Environment File
# =============================================================================
echo -e "${GREEN}📝 Creating environment file template...${NC}"
cat > /opt/wealth-coach-ai/.env.template << 'EOF'
# =============================================================================
# Wealth Coach AI - Production Environment Variables
# =============================================================================

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database (Supabase)
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis (Upstash)
REDIS_URL=redis://default:password@host:port

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# JWT Secret
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this

# Frontend API URL
VITE_API_URL=https://api.yourdomain.com

# Grafana (Optional)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=change-this-password

# PostgreSQL Password (if self-hosting DB)
POSTGRES_PASSWORD=your-postgres-password
EOF

echo -e "${GREEN}✅ Environment template created at /opt/wealth-coach-ai/.env.template${NC}"
echo -e "${YELLOW}⚠️  Copy to .env and fill in your actual values${NC}"

# =============================================================================
# 9. Setup GitHub Container Registry Access
# =============================================================================
echo -e "${GREEN}🔐 Docker registry login instructions...${NC}"
echo ""
echo "To pull images from GitHub Container Registry, run:"
echo "  echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin"
echo ""

# =============================================================================
# 10. Setup Swap (for low memory servers)
# =============================================================================
echo -e "${GREEN}💾 Setting up swap space...${NC}"
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo -e "${GREEN}✅ 4GB swap created${NC}"
else
    echo -e "${YELLOW}⚠️  Swap already exists${NC}"
fi

# =============================================================================
# 11. Create Deployment Helper Script
# =============================================================================
echo -e "${GREEN}📜 Creating deployment helper script...${NC}"
cat > /opt/wealth-coach-ai/deploy.sh << 'EOF'
#!/bin/bash

# Quick deployment script
cd /opt/wealth-coach-ai

echo "🔄 Pulling latest code..."
git pull origin main

echo "🐳 Pulling latest Docker images..."
docker compose -f docker-compose.prod.yml pull

echo "🚀 Deploying application..."
docker compose -f docker-compose.prod.yml up -d

echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ Deployment complete!"
echo "📊 Check status: docker compose -f docker-compose.prod.yml ps"
EOF

chmod +x /opt/wealth-coach-ai/deploy.sh
echo -e "${GREEN}✅ Deployment script created${NC}"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Server Setup Complete!                                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo "1. Clone your repository:"
echo "   cd /opt/wealth-coach-ai"
echo "   git clone https://github.com/Sour4vH4ld3r/wealth-coach-ai.git ."
echo ""
echo "2. Configure environment:"
echo "   cp .env.template .env"
echo "   nano .env  # Fill in your actual values"
echo ""
echo "3. Login to GitHub Container Registry:"
echo "   echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin"
echo ""
echo "4. Deploy the application:"
echo "   ./deploy.sh"
echo ""
echo "5. Setup SSL certificate (optional but recommended):"
echo "   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo ""
echo -e "${GREEN}🎉 Your server is ready for deployment!${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Log out and back in for Docker group changes to take effect${NC}"

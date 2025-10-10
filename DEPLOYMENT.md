# 🚀 Wealth Coach AI - Excloud VPS Deployment Guide

Complete guide for deploying Wealth Coach AI to your Excloud VPS server.

---

## 📊 Server Requirements

### Minimum Configuration (Testing)
- **CPU:** 2 vCPU cores
- **RAM:** 4GB
- **Storage:** 40GB SSD
- **OS:** Ubuntu 22.04 LTS

### Recommended Configuration (Production)
- **CPU:** 4 vCPU cores
- **RAM:** 8GB
- **Storage:** 80GB SSD
- **OS:** Ubuntu 22.04 LTS
- **Bandwidth:** 2TB/month

### With Monitoring (Prometheus + Grafana)
- **CPU:** 6 vCPU cores
- **RAM:** 12GB
- **Storage:** 100GB SSD
- **Bandwidth:** 3TB/month

---

## 🔧 Initial Server Setup

### 1. Order Excloud VPS

1. Go to [Excloud](https://www.excloud.in/) or your Excloud provider
2. Select VPS plan matching requirements above
3. Choose **Ubuntu 22.04 LTS** as OS
4. Note your server IP address and root password

### 2. First Login

```bash
# SSH into your server
ssh root@your-server-ip

# Change root password (recommended)
passwd
```

### 3. Run Automated Setup Script

```bash
# Download and run setup script
wget https://raw.githubusercontent.com/Sour4vH4ld3r/wealth-coach-ai/main/deploy/server-setup.sh
chmod +x server-setup.sh
bash server-setup.sh
```

**What this script does:**
- ✅ Updates system packages
- ✅ Installs Docker & Docker Compose
- ✅ Installs Nginx, Certbot (for SSL)
- ✅ Configures firewall (UFW)
- ✅ Creates application directory
- ✅ Sets up 4GB swap space
- ✅ Creates deployment helper scripts

### 4. Manual Setup (Alternative)

If you prefer manual setup, see the script for commands: `deploy/server-setup.sh`

---

## 📥 Application Deployment

### 1. Clone Repository

```bash
# Navigate to application directory
cd /opt/wealth-coach-ai

# Clone repository
git clone https://github.com/Sour4vH4ld3r/wealth-coach-ai.git .

# Or if already cloned, pull latest
git pull origin main
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp .env.template .env

# Edit environment file
nano .env
```

**Required environment variables:**

```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database (Supabase - get from https://supabase.com/)
DATABASE_URL=postgresql://user:password@db.xxx.supabase.co:5432/postgres

# Redis (Upstash - get from https://upstash.com/)
REDIS_URL=redis://default:password@region.upstash.io:port

# OpenAI API (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT Secret (generate random string)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Frontend API URL
VITE_API_URL=https://api.yourdomain.com  # or http://your-server-ip:8000

# Grafana Admin Password
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)
```

### 3. Setup Cloud Services

#### Supabase (PostgreSQL Database)

1. Go to: https://supabase.com/
2. Create new project
3. Enable **pgvector** extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Copy connection string to `DATABASE_URL`

#### Upstash (Redis Cache)

1. Go to: https://upstash.com/
2. Create new Redis database
3. Copy connection URL to `REDIS_URL`

### 4. Login to GitHub Container Registry

```bash
# Generate Personal Access Token at:
# https://github.com/settings/tokens
# Scopes needed: read:packages

# Login to registry
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u Sour4vH4ld3r --password-stdin
```

### 5. Deploy Application

```bash
# Using helper script
./deploy.sh

# Or manually
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 6. Verify Deployment

```bash
# Check running containers
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Test API health
curl http://localhost:8000/health

# Expected output: {"status":"healthy"}
```

---

## 🌐 Domain & SSL Setup

### 1. Point Domain to Server

Add these DNS records at your domain registrar:

```
Type    Name    Value               TTL
A       @       your-server-ip      3600
A       www     your-server-ip      3600
CNAME   api     yourdomain.com      3600
```

### 2. Configure Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/wealth-coach-ai
```

**Nginx configuration:**

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/wealth-coach-ai /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 3. Setup SSL with Let's Encrypt

```bash
# Install certificate for both domains
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect HTTP to HTTPS (recommended)
```

**Auto-renewal is configured automatically!**

Test renewal:
```bash
sudo certbot renew --dry-run
```

---

## 🔄 GitHub Actions Auto-Deployment

### 1. Add GitHub Secrets

Go to: `https://github.com/Sour4vH4ld3r/wealth-coach-ai/settings/secrets/actions`

**Required secrets:**

```
DEPLOY_HOST = your-excloud-server-ip
DEPLOY_USER = deploy  # or your username
DEPLOY_SSH_KEY = <paste SSH private key>
```

### 2. Generate SSH Key for GitHub Actions

**On your VPS:**

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy

# Press Enter for no passphrase

# Add to authorized_keys
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys

# Display private key (copy this for GitHub secret DEPLOY_SSH_KEY)
cat ~/.ssh/github_deploy
```

### 3. Test Deployment

```bash
# Push to main branch
git push origin main

# GitHub Actions will automatically:
# 1. Run tests
# 2. Build Docker images
# 3. Push to GitHub Container Registry
# 4. SSH into your VPS
# 5. Pull latest images
# 6. Restart services
```

Monitor at: `https://github.com/Sour4vH4ld3r/wealth-coach-ai/actions`

---

## 📊 Monitoring Setup (Optional)

### Enable Prometheus & Grafana

```bash
# Edit docker-compose.prod.yml to uncomment monitoring services
# Or use profile:
docker compose -f docker-compose.prod.yml --profile monitoring up -d
```

**Access dashboards:**
- Prometheus: `http://your-server-ip:9090`
- Grafana: `http://your-server-ip:3000`
  - Default login: `admin` / `<GRAFANA_ADMIN_PASSWORD from .env>`

### Setup Grafana Dashboards

1. Login to Grafana
2. Add Prometheus data source: `http://prometheus:9090`
3. Import dashboard ID: `1860` (Node Exporter)

---

## 🔐 Security Hardening

### 1. SSH Security

```bash
# Disable root login
sudo nano /etc/ssh/sshd_config

# Change these lines:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

### 2. Fail2Ban (Prevent brute force)

```bash
# Install
sudo apt install fail2ban -y

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Automatic Security Updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🛠️ Maintenance Commands

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend
```

### Update Application

```bash
# Pull latest code
cd /opt/wealth-coach-ai
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build
```

### Database Backup

```bash
# Backup Supabase database
pg_dump -h db.xxx.supabase.co -U postgres -d postgres > backup.sql

# Restore
psql -h db.xxx.supabase.co -U postgres -d postgres < backup.sql
```

### Clean Up Docker

```bash
# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f

# Full cleanup
docker system prune -a --volumes -f
```

### Monitor Resources

```bash
# System resources
htop

# Disk usage
df -h
ncdu /

# Docker stats
docker stats

# Service status
docker compose -f docker-compose.prod.yml ps
```

---

## 🚨 Troubleshooting

### Application Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check .env file
cat .env

# Verify environment variables
docker compose -f docker-compose.prod.yml config
```

### Database Connection Issues

```bash
# Test database connection
docker compose -f docker-compose.prod.yml exec backend python -c "
from backend.database import get_db
print('Database connected:', next(get_db()))
"
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check Nginx config
sudo nginx -t
```

### Port Already in Use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Out of Memory

```bash
# Check memory
free -h

# Increase swap
sudo fallocate -l 8G /swapfile2
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2
```

---

## 📈 Performance Optimization

### Enable Redis Caching

Already configured in production. Verify:

```bash
# Test Redis connection
docker compose -f docker-compose.prod.yml exec backend python -c "
import redis
r = redis.from_url('redis://redis:6379/0')
print('Redis ping:', r.ping())
"
```

### Database Connection Pooling

Already configured in production settings.

### Enable Gzip Compression

Add to Nginx config:

```nginx
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

---

## 🎯 Production Checklist

- [ ] Server meets minimum requirements
- [ ] Domain pointing to server IP
- [ ] SSL certificate installed
- [ ] Environment variables configured
- [ ] Database (Supabase) setup
- [ ] Redis (Upstash) setup
- [ ] GitHub Actions secrets added
- [ ] Firewall configured
- [ ] Nginx configured
- [ ] Application running
- [ ] Health check passing
- [ ] Logs accessible
- [ ] Backups configured
- [ ] Monitoring setup (optional)

---

## 📞 Support

- **GitHub Issues:** https://github.com/Sour4vH4ld3r/wealth-coach-ai/issues
- **Documentation:** Check project README.md

---

## 📚 Additional Resources

- [Excloud Documentation](https://www.excloud.in/docs)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Supabase Docs](https://supabase.com/docs)
- [Upstash Docs](https://upstash.com/docs)

---

**🎉 Congratulations! Your Wealth Coach AI is now running on Excloud VPS!**

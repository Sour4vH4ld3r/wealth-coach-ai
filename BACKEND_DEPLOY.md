# 🚀 Backend-Only Deployment Guide
## Wealth Coach AI - FastAPI Backend Deployment

**Deploy only the backend API using Docker**

---

## 📋 What You Get

```
✅ FastAPI Backend API
✅ Runs on port 8000
✅ Health monitoring
✅ Automatic restarts
✅ Log management
✅ Uses cloud PostgreSQL (Supabase)
✅ Uses cloud Redis (Upstash)
```

---

## 🎯 Prerequisites

### Required Services (Cloud)

1. **Supabase** (PostgreSQL Database) - Free tier available
2. **Upstash** (Redis Cache) - Free tier available
3. **OpenAI API Key** - Paid service

---

## 🚀 Quick Deployment

### Step 1: Connect to Server

```bash
# SSH into your VPS
ssh root@your-server-ip
```

### Step 2: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

### Step 3: Setup Application

```bash
# Create directory
mkdir -p /opt/wealth-coach-backend
cd /opt/wealth-coach-backend

# Clone repository
git clone https://github.com/Sour4vH4ld3r/wealth-coach-ai.git .
```

### Step 4: Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit configuration
nano .env
```

**Minimum required variables:**

```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database (Supabase)
DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:5432/postgres

# Redis (Upstash)
REDIS_URL=redis://default:pass@region.upstash.io:port

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxx

# JWT Secret
JWT_SECRET_KEY=$(openssl rand -hex 32)

# CORS (allow all origins for now)
CORS_ORIGINS=*
```

**Save:** `Ctrl+X`, then `Y`, then `Enter`

### Step 5: Deploy Backend

```bash
# Pull/Build and start
docker compose -f docker-compose.backend.yml up -d --build

# Check status
docker compose -f docker-compose.backend.yml ps

# View logs
docker compose -f docker-compose.backend.yml logs -f
```

### Step 6: Test API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy"}
```

```bash
# Test from your local machine
curl http://your-server-ip:8000/health
```

---

## 🔧 Setup Cloud Services

### 1. Supabase (PostgreSQL)

**Create Database:**

```
1. Go to: https://supabase.com/
2. Sign in with GitHub
3. Click: New Project
   - Name: wealth-coach-ai
   - Database Password: <strong password>
   - Region: <closest to your server>
4. Wait 2 minutes for setup
```

**Enable pgvector:**

```sql
1. Go to: SQL Editor
2. Run this:

CREATE EXTENSION IF NOT EXISTS vector;
```

**Get Connection String:**

```
1. Go to: Project Settings → Database
2. Find: Connection string (URI)
3. Copy the full URL
4. Paste into .env as DATABASE_URL
```

### 2. Upstash (Redis)

**Create Redis:**

```
1. Go to: https://upstash.com/
2. Sign in with GitHub
3. Click: Create Database
   - Name: wealth-coach-redis
   - Type: Regional
   - Region: <closest to your server>
4. Click: Create
```

**Get Connection URL:**

```
1. In database dashboard
2. Copy: Redis Connect URL
3. Paste into .env as REDIS_URL
```

### 3. OpenAI API Key

**Get API Key:**

```
1. Go to: https://platform.openai.com/
2. Sign in
3. Go to: API keys
4. Click: Create new secret key
   - Name: wealth-coach-backend
5. Copy and save immediately
6. Paste into .env as OPENAI_API_KEY
```

---

## 📊 Server Requirements

### Minimum (Testing)
```
✅ 1 vCPU
✅ 2GB RAM
✅ 20GB Storage
✅ Ubuntu 22.04 LTS
💰 ~$12-15/month
```

### Recommended (Production)
```
✅ 2 vCPU
✅ 4GB RAM
✅ 40GB Storage
✅ Ubuntu 22.04 LTS
💰 ~$24/month
```

---

## 🌐 Domain & SSL Setup (Optional)

### 1. Point Domain to Server

**Add DNS A Record:**

```
Type: A
Name: api
Value: your-server-ip
TTL: 3600
```

### 2. Install Nginx

```bash
apt install nginx -y
```

### 3. Configure Nginx

```bash
nano /etc/nginx/sites-available/backend
```

**Paste this configuration:**

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable site:**

```bash
ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4. Install SSL Certificate

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d api.yourdomain.com

# Follow prompts
# Certificates auto-renew every 90 days
```

**Test SSL:**

```bash
curl https://api.yourdomain.com/health
```

---

## 🔥 Firewall Configuration

```bash
# Enable firewall
ufw enable

# Allow SSH
ufw allow ssh

# Allow HTTP & HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow backend port (if not using nginx)
ufw allow 8000/tcp

# Check status
ufw status
```

---

## 📋 Common Operations

### View Logs

```bash
# Follow logs
docker compose -f docker-compose.backend.yml logs -f

# Last 100 lines
docker compose -f docker-compose.backend.yml logs --tail=100

# Backend only
docker logs -f wealth_coach_backend
```

### Restart Backend

```bash
docker compose -f docker-compose.backend.yml restart
```

### Stop Backend

```bash
docker compose -f docker-compose.backend.yml down
```

### Start Backend

```bash
docker compose -f docker-compose.backend.yml up -d
```

### Update Backend

```bash
cd /opt/wealth-coach-backend
git pull origin main
docker compose -f docker-compose.backend.yml up -d --build
```

### Check Status

```bash
docker compose -f docker-compose.backend.yml ps
```

### Access Container Shell

```bash
docker compose -f docker-compose.backend.yml exec backend bash
```

### View Resource Usage

```bash
docker stats wealth_coach_backend
```

### Clean Up

```bash
# Remove old images
docker image prune -f

# Full cleanup
docker system prune -a -f
```

---

## 🔍 API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status":"healthy"}
```

### API Documentation

```
📖 Swagger UI: http://your-server-ip:8000/docs
📖 ReDoc: http://your-server-ip:8000/redoc
```

### Example API Call

```bash
# Chat endpoint (example)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What is a 401k?",
    "user_id": "user123"
  }'
```

---

## 🚨 Troubleshooting

### Container Keeps Restarting

```bash
# Check logs
docker logs wealth_coach_backend

# Common issues:
# ❌ Wrong DATABASE_URL
# ❌ Wrong REDIS_URL
# ❌ Missing OPENAI_API_KEY
# ❌ Invalid JWT_SECRET_KEY
```

### Database Connection Error

```bash
# Test database connection
docker compose -f docker-compose.backend.yml exec backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
conn = engine.connect()
print('✅ Database connected')
conn.close()
"
```

### Redis Connection Error

```bash
# Test Redis connection
docker compose -f docker-compose.backend.yml exec backend python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL'))
print('✅ Redis ping:', r.ping())
"
```

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Out of Memory

```bash
# Check memory
free -h

# Add swap
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Can't Access API from Outside

```bash
# Check firewall
ufw status

# Allow port 8000
ufw allow 8000/tcp

# Check container is listening
docker compose -f docker-compose.backend.yml exec backend netstat -tlnp | grep 8000
```

---

## 📊 Monitoring

### Basic Health Check

```bash
# Create health check script
cat > /opt/health-check.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $response -eq 200 ]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is down (HTTP $response)"
    # Restart backend
    cd /opt/wealth-coach-backend
    docker compose -f docker-compose.backend.yml restart
fi
EOF

chmod +x /opt/health-check.sh
```

### Setup Cron Job for Health Checks

```bash
# Add to crontab
crontab -e

# Add this line (checks every 5 minutes)
*/5 * * * * /opt/health-check.sh >> /var/log/backend-health.log 2>&1
```

### View Logs

```bash
tail -f /var/log/backend-health.log
```

---

## 📝 Environment Variables Reference

### Required Variables

```bash
ENVIRONMENT=production           # Environment mode
DEBUG=false                     # Debug mode (false for production)
LOG_LEVEL=WARNING              # Logging level

DATABASE_URL=postgresql://...   # Supabase PostgreSQL URL
REDIS_URL=redis://...          # Upstash Redis URL
OPENAI_API_KEY=sk-proj-...     # OpenAI API key
JWT_SECRET_KEY=xxx...          # JWT secret (32+ chars)
```

### Optional Variables

```bash
CORS_ORIGINS=*                 # Allowed CORS origins
MAX_WORKERS=4                  # Uvicorn workers
PORT=8000                      # API port
HOST=0.0.0.0                   # Bind address
```

---

## 💰 Monthly Cost Estimate

```
┌──────────────────────────────────────┐
│ Service              Cost            │
├──────────────────────────────────────┤
│ VPS Server (2vCPU)   $12-24/month   │
│ Supabase (Free)      $0/month       │
│ Upstash (Free)       $0/month       │
│ OpenAI API           $10-50/month   │
├──────────────────────────────────────┤
│ TOTAL                $22-74/month   │
└──────────────────────────────────────┘
```

---

## ✅ Deployment Checklist

```
Pre-deployment:
☐ VPS server ready (Ubuntu 22.04)
☐ Docker installed
☐ Repository cloned

Cloud Services:
☐ Supabase database created
☐ pgvector extension enabled
☐ Upstash Redis created
☐ OpenAI API key obtained

Configuration:
☐ .env file created
☐ All required variables set
☐ JWT secret generated

Deployment:
☐ Backend container running
☐ Health check passing
☐ Logs clean (no errors)
☐ API accessible

Optional:
☐ Domain configured
☐ Nginx installed
☐ SSL certificate installed
☐ Firewall configured
☐ Health monitoring setup
```

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Start backend
docker compose -f docker-compose.backend.yml up -d

# Stop backend
docker compose -f docker-compose.backend.yml down

# Restart backend
docker compose -f docker-compose.backend.yml restart

# View logs
docker compose -f docker-compose.backend.yml logs -f

# Check status
docker compose -f docker-compose.backend.yml ps

# Update code
git pull && docker compose -f docker-compose.backend.yml up -d --build

# Test health
curl http://localhost:8000/health

# View API docs
open http://your-server-ip:8000/docs
```

---

## 📞 Support

- **GitHub Issues:** https://github.com/Sour4vH4ld3r/wealth-coach-ai/issues
- **API Documentation:** http://your-server-ip:8000/docs

---

## 🎉 Success!

**Your backend API is now live!**

```
🔗 API: http://your-server-ip:8000
📖 Docs: http://your-server-ip:8000/docs
✅ Health: http://your-server-ip:8000/health
```

**Test it:**

```bash
curl http://your-server-ip:8000/health
```

---

**Made with ❤️ for easy backend deployment**

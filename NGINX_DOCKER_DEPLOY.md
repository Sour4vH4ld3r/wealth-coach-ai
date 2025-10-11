# 🚀 Backend + Nginx Docker Deployment Guide
## Wealth Coach AI - Complete Docker Deployment with Nginx

**Deploy FastAPI backend with Nginx reverse proxy using Docker**

---

## 📋 What You Get

```
✅ FastAPI Backend API (port 8000 - internal)
✅ Nginx Reverse Proxy (ports 80, 443)
✅ Automatic SSL/HTTPS support
✅ Load balancing ready
✅ Production-grade configuration
✅ Health monitoring
✅ Automatic restarts
✅ Centralized logging
```

---

## 🎯 Architecture

```
Internet
    ↓
Nginx (Port 80/443)
    ↓
Backend API (Port 8000 - internal)
    ↓
Supabase (PostgreSQL) + Upstash (Redis)
```

---

## 🚀 Quick Deployment

### Step 1: Connect to Server

```bash
# SSH into your server
ssh root@167.71.226.46

# Update system
apt update && apt upgrade -y
```

### Step 2: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

**Expected output:**
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

### Step 3: Clone Repository

```bash
# Create directory
mkdir -p /opt/wealth-coach-ai
cd /opt/wealth-coach-ai

# Clone project
git clone https://github.com/Sour4vH4ld3r/wealth-coach-ai.git .

# Verify files
ls -la
```

**You should see:**
```
✅ docker-compose.nginx.yml
✅ config/nginx/
✅ Dockerfile.prod
✅ .env.template
```

### Step 4: Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit configuration
nano .env
```

**Required variables:**

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

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=<paste-generated-secret>

# CORS
CORS_ORIGINS=*
```

**Generate JWT Secret:**
```bash
openssl rand -hex 32
```

**Save:** `Ctrl+X`, `Y`, `Enter`

### Step 5: Deploy with Docker

```bash
# Build and start services
docker compose -f docker-compose.nginx.yml up -d --build

# Check status
docker compose -f docker-compose.nginx.yml ps

# View logs
docker compose -f docker-compose.nginx.yml logs -f
```

**Expected output:**
```
✅ Container wealth_coach_backend    Started
✅ Container wealth_coach_nginx      Started
```

### Step 6: Test Deployment

```bash
# Test from server
curl http://localhost/health

# Test from outside (use your server IP)
curl http://167.71.226.46/health
```

**Expected response:**
```json
{"status":"healthy"}
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
   - Database Password: <generate strong password>
   - Region: Mumbai, IN (closest to Bangalore)
4. Wait 2 minutes for setup
```

**Enable pgvector extension:**

```sql
1. Go to: SQL Editor in Supabase dashboard
2. Run this query:

CREATE EXTENSION IF NOT EXISTS vector;

3. Click "Run"
```

**Get Connection String:**

```
1. Go to: Project Settings → Database
2. Scroll to: Connection string
3. Select: URI
4. Copy the full URL
5. Replace [YOUR-PASSWORD] with your actual password
6. Paste into .env as DATABASE_URL
```

**Example:**
```
DATABASE_URL=postgresql://postgres:YourPassword@db.xxx.supabase.co:5432/postgres
```

### 2. Upstash (Redis)

**Create Redis Database:**

```
1. Go to: https://upstash.com/
2. Sign in with GitHub
3. Click: Create Database
   - Name: wealth-coach-redis
   - Type: Regional
   - Region: Mumbai (closest to your server)
   - TLS: Enabled
4. Click: Create
```

**Get Connection URL:**

```
1. In database dashboard, find "Redis Connect URL"
2. Copy the URL (starts with redis:// or rediss://)
3. Paste into .env as REDIS_URL
```

**Example:**
```
REDIS_URL=redis://default:your-password@region.upstash.io:port
```

### 3. OpenAI API Key

**Get API Key:**

```
1. Go to: https://platform.openai.com/
2. Sign in
3. Click: API keys (left sidebar)
4. Click: Create new secret key
   - Name: wealth-coach-ai
   - Permissions: All
5. Copy the key immediately (you won't see it again!)
6. Paste into .env as OPENAI_API_KEY
```

**Example:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🌐 Domain & SSL Setup

### Option 1: Using IP Address (No Domain)

**Already working!** Your API is accessible at:
```
http://167.71.226.46/
http://167.71.226.46/health
http://167.71.226.46/docs
```

### Option 2: Using Custom Domain (Recommended)

#### Step 1: Point Domain to Server

**Add DNS A Record at your domain registrar:**

```
Type: A
Name: api (or @)
Value: 167.71.226.46
TTL: 3600
```

**Example domains:**
- `api.yourdomain.com` → 167.71.226.46
- `wealthcoach.yourdomain.com` → 167.71.226.46

**Wait 5-10 minutes for DNS propagation**

**Verify:**
```bash
ping api.yourdomain.com
```

#### Step 2: Update Nginx Configuration

```bash
cd /opt/wealth-coach-ai
nano config/nginx/conf.d/backend.conf
```

**Change line 15:**
```nginx
# From:
server_name _;

# To:
server_name api.yourdomain.com;
```

**Save:** `Ctrl+X`, `Y`, `Enter`

#### Step 3: Install Certbot in Container

```bash
# Stop services
docker compose -f docker-compose.nginx.yml down

# Start services
docker compose -f docker-compose.nginx.yml up -d
```

#### Step 4: Get SSL Certificate (Let's Encrypt)

**Install Certbot on server:**

```bash
apt install certbot -y

# Stop nginx temporarily
docker compose -f docker-compose.nginx.yml stop nginx

# Get certificate
certbot certonly --standalone -d api.yourdomain.com

# Follow prompts:
# 1. Enter email
# 2. Agree to terms (Y)
# 3. Share email (optional)
```

**Certificates will be saved to:**
```
/etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
/etc/letsencrypt/live/api.yourdomain.com/privkey.pem
```

#### Step 5: Copy Certificates to Project

```bash
# Create SSL directory
mkdir -p /opt/wealth-coach-ai/config/nginx/ssl

# Copy certificates
cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem \
   /opt/wealth-coach-ai/config/nginx/ssl/

cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem \
   /opt/wealth-coach-ai/config/nginx/ssl/
```

#### Step 6: Enable HTTPS in Nginx

```bash
nano config/nginx/conf.d/backend.conf
```

**Uncomment the HTTPS server block (lines starting with #):**

1. Find the commented HTTPS section
2. Remove all `#` characters from lines 51-90
3. Change `yourdomain.com` to your actual domain
4. Uncomment the redirect line in the HTTP section (line 22)

**Save:** `Ctrl+X`, `Y`, `Enter`

#### Step 7: Restart Services

```bash
docker compose -f docker-compose.nginx.yml restart
```

**Test HTTPS:**
```bash
curl https://api.yourdomain.com/health
```

#### Step 8: Setup Auto-Renewal

```bash
# Test renewal
certbot renew --dry-run

# Add to crontab
crontab -e

# Add this line (renews daily at 3 AM):
0 3 * * * certbot renew --quiet --post-hook "cd /opt/wealth-coach-ai && cp /etc/letsencrypt/live/api.yourdomain.com/*.pem config/nginx/ssl/ && docker compose -f docker-compose.nginx.yml restart nginx"
```

---

## 🔥 Configure Firewall

```bash
# Enable firewall
ufw enable

# Allow SSH (IMPORTANT!)
ufw allow ssh
ufw allow 22/tcp

# Allow HTTP & HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Check status
ufw status
```

**Output should show:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

## 📊 Monitoring & Management

### View Logs

```bash
# All services
docker compose -f docker-compose.nginx.yml logs -f

# Backend only
docker compose -f docker-compose.nginx.yml logs -f backend

# Nginx only
docker compose -f docker-compose.nginx.yml logs -f nginx

# Last 100 lines
docker compose -f docker-compose.nginx.yml logs --tail=100
```

### Check Container Status

```bash
docker compose -f docker-compose.nginx.yml ps
```

**Expected output:**
```
NAME                    STATUS              PORTS
wealth_coach_backend    Up 5 minutes        8000/tcp
wealth_coach_nginx      Up 5 minutes        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.nginx.yml restart

# Restart backend only
docker compose -f docker-compose.nginx.yml restart backend

# Restart nginx only
docker compose -f docker-compose.nginx.yml restart nginx
```

### Stop Services

```bash
docker compose -f docker-compose.nginx.yml down
```

### Start Services

```bash
docker compose -f docker-compose.nginx.yml up -d
```

### Update Application

```bash
cd /opt/wealth-coach-ai
git pull origin main
docker compose -f docker-compose.nginx.yml up -d --build
```

### Access Container Shell

```bash
# Backend container
docker compose -f docker-compose.nginx.yml exec backend bash

# Nginx container
docker compose -f docker-compose.nginx.yml exec nginx sh

# Exit: type 'exit'
```

### View Resource Usage

```bash
# Container stats
docker stats

# System resources
htop

# Disk usage
df -h

# Nginx logs
docker compose -f docker-compose.nginx.yml exec nginx cat /var/log/nginx/access.log
```

---

## 🔍 API Endpoints

### Health Check

```bash
curl http://167.71.226.46/health
# or
curl https://api.yourdomain.com/health
```

**Response:**
```json
{"status":"healthy"}
```

### API Documentation

```
📖 Swagger UI: http://167.71.226.46/docs
📖 ReDoc: http://167.71.226.46/redoc
📖 OpenAPI JSON: http://167.71.226.46/openapi.json
```

### Test API Call

```bash
# Example: Chat endpoint
curl -X POST http://167.71.226.46/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What is a 401k?",
    "user_id": "user123"
  }'
```

---

## 🚨 Troubleshooting

### 1. Containers Won't Start

```bash
# Check logs
docker compose -f docker-compose.nginx.yml logs

# Common issues:
# ❌ Port 80/443 already in use
# ❌ Wrong DATABASE_URL
# ❌ Missing OPENAI_API_KEY
```

**Fix port conflicts:**
```bash
# Check what's using port 80
lsof -i :80

# Stop conflicting service
systemctl stop nginx  # If nginx is running outside Docker
```

### 2. Can't Access from Outside

```bash
# Check firewall
ufw status

# Ensure ports are open
ufw allow 80/tcp
ufw allow 443/tcp

# Check containers are running
docker compose -f docker-compose.nginx.yml ps
```

### 3. SSL Certificate Issues

```bash
# Check certificate files
ls -la /etc/letsencrypt/live/api.yourdomain.com/

# Check copied certificates
ls -la config/nginx/ssl/

# Test nginx configuration
docker compose -f docker-compose.nginx.yml exec nginx nginx -t
```

### 4. Backend Connection Errors

```bash
# Test backend directly
docker compose -f docker-compose.nginx.yml exec backend curl http://localhost:8000/health

# Check backend logs
docker compose -f docker-compose.nginx.yml logs backend

# Test database connection
docker compose -f docker-compose.nginx.yml exec backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
print('✅ Database connected')
"
```

### 5. Nginx 502 Bad Gateway

```bash
# Check if backend is running
docker compose -f docker-compose.nginx.yml ps backend

# Check backend logs
docker compose -f docker-compose.nginx.yml logs backend

# Restart both services
docker compose -f docker-compose.nginx.yml restart
```

---

## 📝 Configuration Files

### docker-compose.nginx.yml

Located at: `/opt/wealth-coach-ai/docker-compose.nginx.yml`

**Services:**
- `backend`: FastAPI application
- `nginx`: Reverse proxy

### Nginx Configuration

**Main config:** `config/nginx/nginx.conf`
**Backend config:** `config/nginx/conf.d/backend.conf`

**Edit Nginx config:**
```bash
nano config/nginx/conf.d/backend.conf
# After editing, restart nginx
docker compose -f docker-compose.nginx.yml restart nginx
```

---

## 🎯 Production Checklist

```
Initial Setup:
☐ Docker installed
☐ Repository cloned
☐ .env configured

Cloud Services:
☐ Supabase database created
☐ pgvector extension enabled
☐ Upstash Redis created
☐ OpenAI API key obtained

Deployment:
☐ Containers running
☐ Health check passing (/health)
☐ API accessible from outside
☐ Firewall configured

Optional (Recommended):
☐ Domain pointed to server
☐ SSL certificate installed
☐ HTTPS working
☐ Auto-renewal configured
☐ Monitoring setup
```

---

## 💰 Monthly Cost Estimate

```
┌─────────────────────────────────────────┐
│ Service              Cost               │
├─────────────────────────────────────────┤
│ DigitalOcean Droplet $48/month         │
│ (4 vCPU, 8GB RAM)                      │
│ Supabase (Free tier) $0/month          │
│ Upstash (Free tier)  $0/month          │
│ OpenAI API           $10-50/month      │
│ Domain (.com)        ~$1/month         │
│ SSL (Let's Encrypt)  Free              │
├─────────────────────────────────────────┤
│ TOTAL                $59-99/month      │
└─────────────────────────────────────────┘
```

---

## 📋 Quick Commands Reference

```bash
# Start everything
docker compose -f docker-compose.nginx.yml up -d

# Stop everything
docker compose -f docker-compose.nginx.yml down

# View logs
docker compose -f docker-compose.nginx.yml logs -f

# Restart
docker compose -f docker-compose.nginx.yml restart

# Check status
docker compose -f docker-compose.nginx.yml ps

# Update and redeploy
git pull && docker compose -f docker-compose.nginx.yml up -d --build

# Test health
curl http://localhost/health

# View Nginx logs
docker compose -f docker-compose.nginx.yml logs nginx

# Test Nginx config
docker compose -f docker-compose.nginx.yml exec nginx nginx -t
```

---

## 🎉 Success!

**Your backend API with Nginx is now live!**

```
🔗 API: http://167.71.226.46/
📖 Docs: http://167.71.226.46/docs
✅ Health: http://167.71.226.46/health
```

**After domain & SSL setup:**
```
🔗 API: https://api.yourdomain.com/
📖 Docs: https://api.yourdomain.com/docs
✅ Health: https://api.yourdomain.com/health
```

---

## 📞 Support

- **GitHub Issues:** https://github.com/Sour4vH4ld3r/wealth-coach-ai/issues
- **Documentation:** Check project README.md

---

**Built with ❤️ for production-ready deployments**

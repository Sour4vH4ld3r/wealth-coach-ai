# 🚀 Backend-Only Quick Deploy

Deploy just the FastAPI backend in **5 minutes**.

---

## 📦 What You Need

1. ✅ A VPS server (DigitalOcean, AWS, etc.)
2. ✅ Ubuntu 22.04 LTS
3. ✅ 2GB RAM minimum
4. ✅ Supabase account (free)
5. ✅ Upstash account (free)
6. ✅ OpenAI API key

---

## ⚡ Super Quick Start

```bash
# 1. SSH into your server
ssh root@your-server-ip

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# 3. Clone project
git clone https://github.com/Sour4vH4ld3r/wealth-coach-ai.git
cd wealth-coach-ai

# 4. Setup environment
cp .env.template .env
nano .env  # Add your API keys (see below)

# 5. Deploy!
./deploy-backend.sh

# ✅ Done! API running on http://your-server-ip:8000
```

---

## 🔑 Get Your API Keys

### 1. Supabase (Database) - 2 minutes

```
1. Visit: https://supabase.com/
2. Sign in with GitHub
3. Click: New Project
   - Name: wealth-coach-ai
   - Password: <generate strong password>
4. Wait 2 minutes
5. Go to: Settings → Database
6. Copy: Connection string (URI)
```

**Enable pgvector:**
```sql
-- Go to SQL Editor and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Upstash (Redis) - 1 minute

```
1. Visit: https://upstash.com/
2. Sign in with GitHub
3. Click: Create Database
   - Name: wealth-coach-redis
   - Type: Regional
4. Copy: Redis URL
```

### 3. OpenAI - 2 minutes

```
1. Visit: https://platform.openai.com/
2. Go to: API Keys
3. Click: Create new secret key
4. Copy the key (starts with sk-proj-)
```

---

## 📝 Configure .env File

```bash
nano .env
```

**Paste these values:**

```bash
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database (paste your Supabase URL)
DATABASE_URL=postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres

# Redis (paste your Upstash URL)
REDIS_URL=redis://default:[password]@region.upstash.io:port

# OpenAI (paste your API key)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-random-secret-here

# CORS
CORS_ORIGINS=*
```

**Save:** `Ctrl+X`, `Y`, `Enter`

---

## 🎯 Deploy Backend

### Option 1: Automated Script (Recommended)

```bash
./deploy-backend.sh
```

**This script:**
- ✅ Checks Docker installation
- ✅ Validates environment variables
- ✅ Builds Docker image
- ✅ Starts backend container
- ✅ Runs health check
- ✅ Shows you the API URL

### Option 2: Manual Deployment

```bash
# Build and start
docker compose -f docker-compose.backend.yml up -d --build

# Check status
docker compose -f docker-compose.backend.yml ps

# View logs
docker compose -f docker-compose.backend.yml logs -f
```

---

## ✅ Test Your Backend

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}

# From your local machine:
curl http://your-server-ip:8000/health
```

**Open API Documentation:**
```
http://your-server-ip:8000/docs
```

---

## 🌐 Add Domain & SSL (Optional)

### 1. Point domain to server

**DNS A Record:**
```
api.yourdomain.com → your-server-ip
```

### 2. Install Nginx & SSL

```bash
# Install Nginx
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
cat > /etc/nginx/sites-available/backend << 'EOF'
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
EOF

# Enable site
ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d api.yourdomain.com
```

**Now access via HTTPS:**
```
https://api.yourdomain.com/health
```

---

## 📊 Useful Commands

```bash
# View logs
docker compose -f docker-compose.backend.yml logs -f

# Restart backend
docker compose -f docker-compose.backend.yml restart

# Stop backend
docker compose -f docker-compose.backend.yml down

# Update backend
git pull && ./deploy-backend.sh

# Check container stats
docker stats

# Access container shell
docker compose -f docker-compose.backend.yml exec backend bash
```

---

## 🔥 Configure Firewall

```bash
# Enable firewall
ufw enable

# Allow SSH
ufw allow ssh

# Allow backend port
ufw allow 8000/tcp

# If using Nginx
ufw allow 80/tcp
ufw allow 443/tcp

# Check status
ufw status
```

---

## 🚨 Troubleshooting

### Backend won't start

```bash
# Check logs
docker compose -f docker-compose.backend.yml logs

# Common issues:
# - Wrong DATABASE_URL
# - Wrong REDIS_URL
# - Missing OPENAI_API_KEY
```

### Can't connect to database

```bash
# Test connection
docker compose -f docker-compose.backend.yml exec backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
conn = engine.connect()
print('✅ Connected')
"
```

### Port already in use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

---

## 💰 Monthly Costs

```
VPS (2 vCPU, 4GB):   $12-24/month
Supabase (Free):     $0/month
Upstash (Free):      $0/month
OpenAI API:          $10-50/month
──────────────────────────────────
Total:               $22-74/month
```

---

## 📖 Full Documentation

For detailed deployment guide, see: [BACKEND_DEPLOY.md](BACKEND_DEPLOY.md)

---

## 🎉 You're Done!

Your backend API is live at:

```
🔗 http://your-server-ip:8000
📖 http://your-server-ip:8000/docs
✅ http://your-server-ip:8000/health
```

---

**Questions?** Open an issue: https://github.com/Sour4vH4ld3r/wealth-coach-ai/issues

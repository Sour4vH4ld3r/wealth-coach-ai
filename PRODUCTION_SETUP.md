# 🚀 Production Environment Setup Guide

Complete guide for configuring `.env.production` on your VPS server.

---

## 📋 Overview

**This guide uses cloud services for production:**
- ✅ **Supabase** - PostgreSQL database with pgvector
- ✅ **Upstash** - Redis cache
- ✅ **OpenAI** - AI/LLM API

**Your local `.env` remains unchanged for development.**

---

## ⚡ Quick Setup

### Step 1: Copy Production Template

**On your VPS server:**

```bash
cd /opt/wealth-coach-ai

# Copy production template
cp .env.production .env.production.local

# Edit with your credentials
nano .env.production.local
```

### Step 2: Configure Cloud Services

#### 1. Supabase (Database)

**Setup:**
```
1. Go to: https://supabase.com/
2. Sign in with GitHub
3. Click: New Project
   - Name: wealth-coach-ai
   - Database Password: <generate strong password>
   - Region: Mumbai, IN (or closest to your VPS)
4. Wait 2 minutes for project creation
```

**Enable pgvector:**
```sql
-- Go to SQL Editor in Supabase
-- Run this command:
CREATE EXTENSION IF NOT EXISTS vector;
```

**Get Connection String:**
```
1. Go to: Project Settings → Database
2. Scroll to: Connection string
3. Select: URI
4. Copy the URL
5. Replace [YOUR-PASSWORD] with actual password
```

**Add to .env.production.local:**
```bash
DATABASE_URL=postgresql://postgres:YourActualPassword@db.xxx.supabase.co:5432/postgres
```

#### 2. Upstash (Redis)

**Setup:**
```
1. Go to: https://upstash.com/
2. Sign in with GitHub
3. Click: Create Database
   - Name: wealth-coach-redis
   - Type: Regional
   - Region: Mumbai (or closest)
   - TLS: Enabled
4. Click: Create
```

**Get Connection URL:**
```
1. In database dashboard
2. Copy: Redis Connect URL (starts with redis:// or rediss://)
```

**Add to .env.production.local:**
```bash
REDIS_URL=redis://default:YourRedisPassword@region.upstash.io:port
```

#### 3. OpenAI (AI API)

**Setup:**
```
1. Go to: https://platform.openai.com/
2. Sign in
3. Go to: API keys
4. Click: Create new secret key
   - Name: wealth-coach-production
5. Copy the key (starts with sk-proj-)
```

**Add to .env.production.local:**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Generate Security Keys

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate session secret
openssl rand -hex 32
```

**Add to .env.production.local:**
```bash
JWT_SECRET_KEY=<paste-first-output>
SESSION_SECRET_KEY=<paste-second-output>
```

### Step 4: Configure CORS (Important!)

**For testing with IP address:**
```bash
CORS_ORIGINS=*
```

**For production with domain:**
```bash
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### Step 5: Secure the File

```bash
# Restrict permissions (only root can read)
chmod 600 .env.production.local

# Verify
ls -la .env.production.local
# Should show: -rw------- (600)
```

---

## 🐳 Deploy with Production Config

### Option 1: Use .env.production.local

```bash
# Stop existing containers
docker compose -f docker-compose.backend.yml down

# Start with production config
docker compose -f docker-compose.backend.yml --env-file .env.production.local up -d

# Check status
docker compose -f docker-compose.backend.yml ps

# Test
curl http://localhost:8000/health
```

### Option 2: Create Production Docker Compose

**Create `docker-compose.production.yml`:**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        - BUILD_ENV=production
    container_name: wealth_coach_backend_prod
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env.production.local
    networks:
      - backend_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  backend_network:
    driver: bridge
```

**Deploy:**

```bash
docker compose -f docker-compose.production.yml up -d --build
```

---

## ✅ Verification Checklist

**Before deploying, verify all these values:**

```bash
# Check DATABASE_URL
echo $DATABASE_URL | grep "supabase.co"

# Check REDIS_URL
echo $REDIS_URL | grep "upstash.io"

# Check OPENAI_API_KEY
echo $OPENAI_API_KEY | grep "^sk-proj-"

# Check JWT_SECRET_KEY (should be 64 chars)
echo $JWT_SECRET_KEY | wc -c
# Output: 65 (64 chars + newline)
```

---

## 🔍 Test Production Config

### 1. Test Database Connection

```bash
docker compose -f docker-compose.backend.yml --env-file .env.production.local run --rm backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
conn = engine.connect()
print('✅ Database connected successfully')
conn.close()
"
```

### 2. Test Redis Connection

```bash
docker compose -f docker-compose.backend.yml --env-file .env.production.local run --rm backend python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL'))
print('✅ Redis ping:', r.ping())
"
```

### 3. Test OpenAI API

```bash
docker compose -f docker-compose.backend.yml --env-file .env.production.local run --rm backend python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
print('✅ OpenAI API key is valid')
"
```

### 4. Test Full Application

```bash
# Start application
docker compose -f docker-compose.backend.yml --env-file .env.production.local up -d

# Wait 15 seconds
sleep 15

# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

---

## 🔒 Security Best Practices

### 1. File Permissions

```bash
# Production env file should be readable only by owner
chmod 600 .env.production.local

# Check
ls -la .env.production.local
# Should show: -rw-------
```

### 2. Never Commit to Git

```bash
# Ensure .gitignore includes
echo ".env.production*" >> .gitignore
echo ".env.local" >> .gitignore
```

### 3. Rotate Keys Regularly

```bash
# Generate new JWT secret every 90 days
openssl rand -hex 32

# Update in .env.production.local
# Restart services
```

### 4. Monitor Access

```bash
# Check who can access the file
ls -l .env.production.local

# Check recent access
stat .env.production.local
```

---

## 📊 Environment Variables Reference

### Required (Must Configure)

```bash
DATABASE_URL              # Supabase PostgreSQL connection string
REDIS_URL                 # Upstash Redis connection string
OPENAI_API_KEY           # OpenAI API key
JWT_SECRET_KEY           # Generate with: openssl rand -hex 32
SESSION_SECRET_KEY       # Generate with: openssl rand -hex 32
```

### Important (Recommended)

```bash
CORS_ORIGINS             # Set to your domain or * for testing
ENVIRONMENT=production   # Should be "production"
DEBUG=false             # Should be false for production
LOG_LEVEL=WARNING       # WARNING or ERROR for production
```

### Optional (Nice to Have)

```bash
SENTRY_DSN              # Error tracking
SMTP_HOST               # Email notifications
SLACK_WEBHOOK_URL       # Slack notifications
ENABLE_METRICS=true     # Performance monitoring
```

---

## 🚨 Troubleshooting

### Issue: Database Connection Failed

```bash
# Test connection string format
echo $DATABASE_URL

# Should be:
# postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Common mistakes:
# ❌ Missing password
# ❌ Wrong port (should be 5432)
# ❌ Missing /postgres at the end
# ❌ Extra spaces or quotes
```

### Issue: Redis Connection Failed

```bash
# Test Redis URL format
echo $REDIS_URL

# Should be:
# redis://default:password@region.upstash.io:port

# Common mistakes:
# ❌ Using rediss:// (SSL) without proper config
# ❌ Wrong port
# ❌ Missing password
```

### Issue: OpenAI API Key Invalid

```bash
# Check key format
echo $OPENAI_API_KEY | head -c 10

# Should output: sk-proj-xx

# Common mistakes:
# ❌ Old format key (sk-xxx instead of sk-proj-)
# ❌ Spaces in the key
# ❌ Quotes around the key
```

### Issue: Permission Denied

```bash
# Fix file permissions
chmod 600 .env.production.local

# Fix logs directory
mkdir -p logs
chmod 777 logs

# Fix data directory
mkdir -p data/knowledge_base
chmod 755 data/knowledge_base
```

---

## 📝 Production Deployment Commands

```bash
# Full production deployment
cd /opt/wealth-coach-ai

# 1. Pull latest code
git pull origin main

# 2. Verify environment
cat .env.production.local | grep -E "(DATABASE_URL|REDIS_URL|OPENAI_API_KEY)"

# 3. Build and deploy
docker compose -f docker-compose.backend.yml --env-file .env.production.local up -d --build

# 4. Check logs
docker compose -f docker-compose.backend.yml logs -f

# 5. Test
curl http://localhost:8000/health
```

---

## 🎯 Quick Start Summary

```bash
# 1. Copy and edit production config
cp .env.production .env.production.local
nano .env.production.local

# 2. Add these (minimum required):
#    - DATABASE_URL (from Supabase)
#    - REDIS_URL (from Upstash)
#    - OPENAI_API_KEY (from OpenAI)
#    - JWT_SECRET_KEY (generate with: openssl rand -hex 32)

# 3. Secure the file
chmod 600 .env.production.local

# 4. Deploy
docker compose -f docker-compose.backend.yml --env-file .env.production.local up -d --build

# 5. Test
curl http://localhost:8000/health
```

---

## 💰 Monthly Costs

```
Supabase (Free tier):    $0/month
Upstash (Free tier):     $0/month
OpenAI API:              $10-50/month (pay as you go)
VPS Server:              $24-48/month
─────────────────────────────────────
Total:                   $34-98/month
```

---

## 📞 Support

- **GitHub Issues:** https://github.com/Sour4vH4ld3r/wealth-coach-ai/issues
- **Documentation:** Check project README files

---

**🎉 Your production environment is ready for cloud deployment!**

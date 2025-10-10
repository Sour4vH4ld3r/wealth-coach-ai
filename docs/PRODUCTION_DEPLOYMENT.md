# Production Deployment Guide
## Wealth Coach AI - Complete Production Setup

---

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [SSL/TLS Configuration](#ssltls-configuration)
5. [Docker Deployment](#docker-deployment)
6. [Monitoring Setup](#monitoring-setup)
7. [Security Checklist](#security-checklist)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## 🔧 **Prerequisites**

### Required Services
- **Supabase Account**: PostgreSQL with pgvector
- **Upstash Account**: Redis cloud service
- **OpenAI API Key**: For LLM functionality
- **Domain Name**: e.g., `wealthcoach.yourdomain.com`
- **Server**: VPS/Cloud instance with Docker support

### Server Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: 2+ cores
- **Storage**: 20GB+ SSD
- **Docker**: v20.10+
- **Docker Compose**: v2.0+

---

## 🌍 **Environment Setup**

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/wealth-coach-ai.git
cd wealth-coach-ai
```

### Step 2: Create Production Environment File
```bash
cp .env.production.example .env
```

### Step 3: Configure Environment Variables

Edit `.env` and update the following **CRITICAL** values:

#### **Database Configuration**
```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/YOUR_DB"
```
Get this from your Supabase project dashboard.

#### **Redis Configuration**
```env
REDIS_URL="rediss://default:YOUR_PASSWORD@YOUR_HOST:6379"
```
Get this from your Upstash console.

#### **OpenAI API Key**
```env
OPENAI_API_KEY="sk-..."
```

#### **JWT Secret** (IMPORTANT!)
```bash
# Generate a secure JWT secret:
openssl rand -hex 32

# Add to .env:
JWT_SECRET_KEY="your-generated-secret-here"
```

#### **CORS Origins**
```env
CORS_ORIGINS='["https://wealthcoach.yourdomain.com","https://www.wealthcoach.yourdomain.com"]'
```

#### **API Keys**
```bash
# Generate secure API keys:
openssl rand -hex 16

# Add to .env:
VALID_API_KEYS='["your-generated-key-1","your-generated-key-2"]'
```

---

## 🗄️ **Database Configuration**

### Step 1: Setup Supabase PostgreSQL

1. **Create Supabase Project**
   - Go to https://supabase.com
   - Create new project
   - Note down connection string

2. **Enable pgvector Extension**
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

3. **Create Database Schema**
```bash
# Run database migrations
python -m alembic upgrade head
```

4. **Create Vector Search Function**
```bash
# Upload and execute setup_pgvector.sql
psql $DATABASE_URL < setup_pgvector.sql
```

### Step 2: Load Knowledge Base
```bash
# Activate virtual environment
source venv/bin/activate

# Load financial knowledge documents
python load_knowledge_pgvector.py
```

**Expected Output:**
```
✅ KNOWLEDGE BASE LOADED SUCCESSFULLY!
   Documents loaded: 52
   pgvector is now your vector database
```

---

## 🔒 **SSL/TLS Configuration**

### Option 1: Let's Encrypt (Free, Recommended)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate certificates
sudo certbot certonly --standalone -d wealthcoach.yourdomain.com

# Certificates will be saved to:
# /etc/letsencrypt/live/wealthcoach.yourdomain.com/
```

### Option 2: Custom SSL Certificates

Place your certificates in:
```
config/nginx/ssl/fullchain.pem
config/nginx/ssl/privkey.pem
```

### Update nginx.prod.conf
```nginx
ssl_certificate /etc/nginx/ssl/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/privkey.pem;
```

---

## 🐳 **Docker Deployment**

### Step 1: Build Images
```bash
# Build all production images
docker-compose -f docker-compose.prod.yml build
```

### Step 2: Start Services
```bash
# Start in detached mode
docker-compose -f docker-compose.prod.yml up -d
```

### Step 3: Verify Deployment
```bash
# Check running containers
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Step 4: Health Check
```bash
# Test backend health
curl https://wealthcoach.yourdomain.com/api/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "vector_db": {"status": "healthy", "document_count": 52}
  }
}
```

---

## 📊 **Monitoring Setup**

### Prometheus Configuration

Create `config/prometheus/prometheus.prod.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

### Grafana Configuration

1. **Access Grafana**: https://monitoring.wealthcoach.yourdomain.com
2. **Default Login**:
   - Username: `admin`
   - Password: From `GRAFANA_ADMIN_PASSWORD` in `.env`

3. **Add Prometheus Data Source**:
   - URL: `http://prometheus:9090`

4. **Import Dashboards**:
   - FastAPI metrics
   - System metrics
   - Custom business metrics

### Create Basic Auth for Monitoring
```bash
# Install htpasswd
sudo apt-get install apache2-utils

# Create password file
htpasswd -c config/nginx/.htpasswd admin

# Enter password when prompted
```

---

## 🔐 **Security Checklist**

### Before Going Live

- [ ] Changed `JWT_SECRET_KEY` from default
- [ ] Generated unique API keys
- [ ] Configured CORS with specific domains
- [ ] Disabled `DEBUG=false`
- [ ] Disabled API documentation (`SWAGGER_UI=false`)
- [ ] Set `LOG_LEVEL=WARNING`
- [ ] SSL certificates installed and valid
- [ ] Firewall configured (UFW/iptables)
- [ ] Rate limiting enabled
- [ ] Database credentials rotated
- [ ] Redis password set
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured

### Firewall Configuration
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### Update SSH Security
```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh
```

---

## 💾 **Backup & Recovery**

### Automated Backups

#### Database Backup Script
Create `scripts/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="wealth_coach_${DATE}.sql.gz"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump $DATABASE_URL | gzip > "$BACKUP_DIR/$FILENAME"

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $FILENAME"
```

#### Setup Cron Job
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_db.sh >> /var/log/backup.log 2>&1
```

### Vector Store Backup
```bash
# Export pgvector data
python scripts/export_vectors.py --output backups/vectors_$(date +%Y%m%d).json
```

### Recovery
```bash
# Restore database
gunzip < backup.sql.gz | psql $DATABASE_URL

# Reload vectors
python load_knowledge_pgvector.py
```

---

## 🚀 **Deployment Commands**

### Quick Start
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Update Deployment
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Full Cleanup (CAUTION!)
```bash
# Stop and remove everything including volumes
docker-compose -f docker-compose.prod.yml down -v
```

---

## 🔍 **Troubleshooting**

### Issue: Backend Not Starting

**Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

**Common causes:**
- Database connection failed (check `DATABASE_URL`)
- Redis connection failed (check `REDIS_URL`)
- Missing environment variables

### Issue: SSL Certificate Errors

**Renew Let's Encrypt:**
```bash
sudo certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

### Issue: High Memory Usage

**Check resource usage:**
```bash
docker stats
```

**Adjust resources in `docker-compose.prod.yml`:**
```yaml
deploy:
  resources:
    limits:
      memory: 1G  # Reduce if needed
```

### Issue: Database Connection Pool Exhausted

**Increase pool size in `.env`:**
```env
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=20
```

### Issue: Vector Search Not Working

**Verify documents loaded:**
```bash
python -c "
from backend.services.vector_store.pgvector_store import get_vector_store
print(f'Documents: {get_vector_store().count()}')
"
```

---

## 📈 **Performance Optimization**

### 1. Enable Redis Caching
```env
CACHE_ENABLED=true
QUERY_CACHE_TTL=7200
EMBEDDING_CACHE_TTL=86400
```

### 2. Optimize Worker Count
```bash
# Rule of thumb: (2 x CPU cores) + 1
WORKERS=5  # For 2-core server
```

### 3. Database Connection Pooling
```env
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

### 4. Enable Nginx Caching
Add to nginx.prod.conf:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
}
```

---

## 🎯 **Production Checklist**

### Pre-Launch
- [ ] All environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations completed
- [ ] Knowledge base loaded (52 documents)
- [ ] Health checks passing
- [ ] Monitoring dashboards configured
- [ ] Backup strategy tested
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Documentation updated

### Post-Launch
- [ ] Monitor error logs
- [ ] Check response times
- [ ] Verify caching effectiveness
- [ ] Test backup/recovery
- [ ] Monitor resource usage
- [ ] Set up alerts for critical issues

---

## 📞 **Support**

### Logs Location
- **Backend**: `/app/logs/`
- **Nginx**: `/var/log/nginx/`
- **Docker**: `docker-compose logs`

### Monitoring URLs
- **Grafana**: https://monitoring.wealthcoach.yourdomain.com
- **Prometheus**: https://monitoring.wealthcoach.yourdomain.com/prometheus/

### Emergency Contacts
- **Supabase Support**: https://supabase.com/support
- **Upstash Support**: https://upstash.com/support
- **OpenAI Support**: https://help.openai.com/

---

## ✅ **Success Indicators**

After deployment, you should see:

✅ All health checks passing
✅ Vector search working (52 documents)
✅ API responding within 200ms
✅ Cache hit rate > 80%
✅ Zero error logs in first hour
✅ SSL certificate valid
✅ Monitoring dashboards showing data

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Production URL**: https://wealthcoach.yourdomain.com

---

*For issues or questions, refer to the troubleshooting section or consult the development team.*

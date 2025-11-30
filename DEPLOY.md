# Wealth Coach AI - Production Deployment Guide

**Last Updated:** November 30, 2025
**Version:** 1.0 - Production Ready
**Domain:** api.wealthwarriorshub.in

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Architecture](#deployment-architecture)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the production deployment of the Wealth Coach AI backend using Docker and Nginx reverse proxy with SSL.

### Current Production Stack
- **Backend:** FastAPI with Gunicorn + Uvicorn workers
- **Database:** PostgreSQL (Supabase)
- **Cache:** Redis (Upstash)
- **Vector DB:** pgvector (PostgreSQL)
- **LLM:** OpenAI GPT-3.5-turbo
- **Web Server:** Nginx with SSL (Let's Encrypt)
- **Container:** Docker with production-optimized image

---

## Prerequisites

### Required Services
- ✅ Domain name pointed to your server (api.wealthwarriorshub.in)
- ✅ Server with Docker installed (Ubuntu 20.04+ recommended)
- ✅ SSL certificate from Let's Encrypt
- ✅ Supabase PostgreSQL database
- ✅ Upstash Redis instance
- ✅ OpenAI API key

### Required Files (Already Configured)
- ✅ `docker-compose.backend.yml` - Production Docker configuration
- ✅ `Dockerfile.prod` - Optimized production Dockerfile
- ✅ `nginx-live.conf` - Nginx reverse proxy config
- ✅ `.env` - Environment variables (DO NOT commit)

---

## Quick Start

```bash
# 1. Clone repository on server
git clone <your-repo-url>
cd wealthWarriors

# 2. Copy environment file
cp .env.example .env
# Edit .env with production credentials

# 3. Deploy with Docker Compose
docker-compose -f docker-compose.backend.yml up -d

# 4. Configure Nginx (if not already done)
sudo cp nginx-live.conf /etc/nginx/sites-available/api.wealthwarriorshub.in
sudo ln -s /etc/nginx/sites-available/api.wealthwarriorshub.in /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 5. Verify deployment
curl https://api.wealthwarriorshub.in/health
```

---

## Deployment Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Nginx:443  │ (SSL termination, reverse proxy)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Docker:8000 │ (Backend container)
└──────┬──────┘
       │
       ├─────► PostgreSQL (Supabase)
       ├─────► Redis (Upstash)
       └─────► OpenAI API
```

---

## Step-by-Step Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. SSL Certificate Setup

```bash
# Obtain SSL certificate
sudo certbot --nginx -d api.wealthwarriorshub.in

# Certificates will be saved at:
# /etc/letsencrypt/live/api.wealthwarriorshub.in/fullchain.pem
# /etc/letsencrypt/live/api.wealthwarriorshub.in/privkey.pem

# Auto-renewal is configured automatically
```

### 3. Environment Configuration

Create `.env` file with production credentials:

```env
# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=rediss://default:password@host:6379

# OpenAI
OPENAI_API_KEY=sk-...

# JWT
JWT_SECRET_KEY=<generate-secure-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
ALLOWED_ORIGINS=["https://app.wealthwarriorshub.in"]
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
MAX_RETRIES=3

# RAG Configuration
RAG_TOP_K=5
MAX_TOKENS_PER_REQUEST=500
CACHE_ENABLED=true
CACHE_TTL=3600

# BulkSMS (OTP)
BULKSMS_API_KEY=your-key
BULKSMS_SENDER_ID=WEALTH
```

### 4. Deploy Backend Container

```bash
# Build and start container
docker-compose -f docker-compose.backend.yml up -d --build

# Check container status
docker-compose -f docker-compose.backend.yml ps

# View logs
docker-compose -f docker-compose.backend.yml logs -f

# Expected output:
# ✓ Redis connection established
# ✓ Vector database loaded
# ✓ Embedding service configured (lazy loading enabled)
# 🚀 Server ready on 0.0.0.0:8000
```

### 5. Configure Nginx

```bash
# Copy Nginx configuration
sudo cp nginx-live.conf /etc/nginx/sites-available/api.wealthwarriorshub.in

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/api.wealthwarriorshub.in /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Enable Nginx on boot
sudo systemctl enable nginx
```

### 6. Knowledge Base Setup

```bash
# Upload financial knowledge documents
mkdir -p data/knowledge_base

# Add your documents (markdown, pdf, txt)
# Documents will be automatically indexed on startup

# Restart to index new documents
docker-compose -f docker-compose.backend.yml restart
```

---

## Post-Deployment

### Health Checks

```bash
# Basic health check
curl https://api.wealthwarriorshub.in/health

# Detailed health check
curl https://api.wealthwarriorshub.in/api/v1/health/detailed

# API documentation
# Visit: https://api.wealthwarriorshub.in/docs
```

### Monitoring

```bash
# View real-time logs
docker-compose -f docker-compose.backend.yml logs -f

# Check container stats
docker stats wealth_coach_backend

# Check Nginx logs
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.access.log
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.error.log
```

### Performance Tuning

Current configuration:
- **Workers:** 1 (Gunicorn worker)
- **Worker Class:** uvicorn.workers.UvicornWorker
- **Timeout:** 120s
- **Memory Limit:** 2GB
- **CPU Limit:** 2 cores
- **Lazy Loading:** Enabled for embedding model (60-70% faster startup)

To scale up:
```yaml
# Edit docker-compose.backend.yml
command: >
    gunicorn backend.main:app
    --workers 4  # Increase workers
    --worker-class uvicorn.workers.UvicornWorker
    --bind 0.0.0.0:8000
```

---

## Maintenance

### Update Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.backend.yml up -d --build

# Or zero-downtime update:
docker-compose -f docker-compose.backend.yml up -d --no-deps --build backend
```

### Backup

```bash
# Database backups are handled by Supabase (daily automatic backups)

# Backup knowledge base
tar -czf knowledge_base_backup_$(date +%Y%m%d).tar.gz data/knowledge_base/

# Backup environment file (encrypted)
gpg -c .env
```

### SSL Certificate Renewal

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Renewal happens automatically via cron
# Check renewal timer:
sudo systemctl status certbot.timer
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.backend.yml logs backend

# Common issues:
# - Missing .env file
# - Invalid database credentials
# - Port 8000 already in use

# Fix port conflict
sudo lsof -ti:8000 | xargs kill -9
```

### 502 Bad Gateway

```bash
# Check if backend is running
docker-compose -f docker-compose.backend.yml ps

# Check Nginx can reach backend
curl http://127.0.0.1:8000/health

# Restart backend
docker-compose -f docker-compose.backend.yml restart
```

### High Memory Usage

```bash
# Check memory usage
docker stats wealth_coach_backend

# Reduce workers or adjust limits in docker-compose.backend.yml
# Restart container
docker-compose -f docker-compose.backend.yml restart
```

### WebSocket Connection Issues

```bash
# Check Nginx WebSocket configuration in nginx-live.conf
# Ensure these headers are set:
# - proxy_set_header Upgrade $http_upgrade
# - proxy_set_header Connection "upgrade"

# Test WebSocket connection
wscat -c wss://api.wealthwarriorshub.in/ws/chat
```

---

## Security Checklist

- ✅ SSL/TLS enabled (HTTPS)
- ✅ Non-root user in Docker container
- ✅ Environment variables not committed
- ✅ Rate limiting configured
- ✅ CORS properly configured
- ✅ Security headers enabled in Nginx
- ✅ Firewall configured (allow 80, 443, 22 only)
- ✅ Regular security updates
- ✅ Database connection over SSL
- ✅ Redis connection over TLS

---

## Performance Metrics

Current production performance:
- **Startup Time:** ~30s (with lazy loading)
- **Response Time:** <200ms (cached), <2s (RAG)
- **Token Usage:** 420-596 tokens per AI response
- **Memory Usage:** ~1.2GB average
- **CPU Usage:** <30% average
- **Uptime:** 99.9% target

---

## Support & Resources

- **API Documentation:** https://api.wealthwarriorshub.in/docs
- **Health Check:** https://api.wealthwarriorshub.in/health
- **Detailed Health:** https://api.wealthwarriorshub.in/api/v1/health/detailed

---

## Quick Reference

### Production Files
- `docker-compose.backend.yml` - Production Docker Compose
- `Dockerfile.prod` - Production Dockerfile
- `nginx-live.conf` - Nginx configuration
- `.env` - Environment variables

### Common Commands
```bash
# Start
docker-compose -f docker-compose.backend.yml up -d

# Stop
docker-compose -f docker-compose.backend.yml down

# Restart
docker-compose -f docker-compose.backend.yml restart

# Logs
docker-compose -f docker-compose.backend.yml logs -f

# Rebuild
docker-compose -f docker-compose.backend.yml up -d --build
```

---

**Deployment Status:** ✅ Production Ready
**Last Tested:** November 30, 2025
**Maintained By:** Wealth Coach AI Team

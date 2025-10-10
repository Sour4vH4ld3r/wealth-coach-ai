# Deployment Guide - Wealth Coach AI Assistant

## Overview

This guide covers deploying Wealth Coach AI to a single VPS for <$20/month operation supporting 1000+ concurrent users.

---

## Infrastructure Requirements

### Minimum VPS Specifications
- **RAM**: 4GB
- **CPU**: 2 vCPU
- **Storage**: 40GB SSD
- **Bandwidth**: 2TB/month

### Recommended VPS Providers
1. **Hetzner Cloud** - CPX21 (€8.46/month) ⭐ Best value
2. **DigitalOcean** - Basic Droplet ($24/month)
3. **Vultr** - High Frequency ($12/month)
4. **Linode** - Shared CPU ($12/month)

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

**Pros**: Easy setup, isolated services, portable
**Cons**: Slight overhead vs bare metal

**Steps**:

1. **Provision VPS and SSH in**:
```bash
ssh root@your-server-ip
```

2. **Install Docker & Docker Compose**:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

3. **Clone repository** (or upload files):
```bash
git clone https://github.com/yourusername/wealthWarriors.git
cd wealthWarriors
```

4. **Configure environment**:
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Critical .env settings**:
```env
ENVIRONMENT=production
DEBUG=false
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
REDIS_URL=redis://redis:6379/0
CHROMA_HOST=chromadb
```

5. **Generate JWT secret**:
```bash
openssl rand -hex 32
# Copy output to JWT_SECRET_KEY in .env
```

6. **Start services**:
```bash
docker-compose up -d
```

7. **Load knowledge base**:
```bash
docker-compose exec backend python scripts/load_knowledge.py
```

8. **Verify deployment**:
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

---

### Option 2: Systemd Service (Bare Metal)

**Pros**: Lower overhead, direct control
**Cons**: More complex setup

1. **Install dependencies**:
```bash
apt update && apt install -y python3.11 python3-pip redis-server nginx
```

2. **Setup application**:
```bash
cd /opt
git clone <repo-url> wealthcoach
cd wealthcoach
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Create systemd service**:
```bash
nano /etc/systemd/system/wealthcoach.service
```

```ini
[Unit]
Description=Wealth Coach AI API
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/wealthcoach
Environment="PATH=/opt/wealthcoach/venv/bin"
ExecStart=/opt/wealthcoach/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Enable and start**:
```bash
systemctl enable wealthcoach
systemctl start wealthcoach
systemctl status wealthcoach
```

---

## Nginx Configuration

### Basic Reverse Proxy

Create `/etc/nginx/sites-available/wealthcoach`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=20r/m;
    limit_req zone=api burst=5 nodelay;

    # Proxy settings
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint (no rate limit)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # Logging
    access_log /var/log/nginx/wealthcoach_access.log;
    error_log /var/log/nginx/wealthcoach_error.log;
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/wealthcoach /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

## SSL Certificate (Let's Encrypt)

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Obtain certificate
certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
# Test renewal:
certbot renew --dry-run
```

---

## Monitoring & Logging

### 1. View Application Logs

**Docker**:
```bash
docker-compose logs -f backend
docker-compose logs -f redis
docker-compose logs -f chromadb
```

**Systemd**:
```bash
journalctl -u wealthcoach -f
```

### 2. Monitor Resources

```bash
# CPU and memory
htop

# Disk usage
df -h

# Docker stats
docker stats
```

### 3. Setup Log Rotation

Create `/etc/logrotate.d/wealthcoach`:
```
/opt/wealthcoach/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload wealthcoach
    endscript
}
```

---

## Cost Optimization

### 1. Redis Memory Management

In `docker-compose.yml`, Redis is configured with:
```yaml
command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

This limits Redis to 256MB and auto-evicts old cache entries.

### 2. LLM Token Limits

In `.env`:
```env
MAX_TOKENS_PER_REQUEST=500
MAX_REQUESTS_PER_USER_PER_DAY=100
```

Limits prevent runaway costs from abuse or bugs.

### 3. Cache Hit Rate Monitoring

Check cache effectiveness:
```bash
curl http://localhost:8000/api/v1/metrics
```

Target: >80% cache hit rate

### 4. ChromaDB Optimization

- Use embedded mode (no separate server)
- Batch document insertions
- Periodic cleanup of old embeddings

---

## Backup Strategy

### Automated Backups

Create `/opt/backup-wealthcoach.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

mkdir -p $BACKUP_DIR

# Backup vector database
tar -czf $BACKUP_DIR/chroma_$DATE.tar.gz /opt/wealthcoach/data/vector_store

# Backup Redis (if using persistence)
docker-compose exec -T redis redis-cli BGSAVE
cp /var/lib/docker/volumes/wealthwarriors_redis_data/_data/dump.rdb \
   $BACKUP_DIR/redis_$DATE.rdb

# Backup environment config
cp /opt/wealthcoach/.env $BACKUP_DIR/env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /opt/backup-wealthcoach.sh
```

---

## Security Hardening

### 1. Firewall (UFW)

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw enable
```

### 2. Fail2Ban for SSH

```bash
apt install fail2ban -y
systemctl enable fail2ban
```

### 3. Environment Security

```bash
# Restrict .env permissions
chmod 600 .env

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh
```

### 4. Security Headers (Nginx)

Add to nginx config:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

---

## Scaling Strategies

### Vertical Scaling (Single Server)
1. Upgrade to 8GB RAM VPS (~$16/month)
2. Increase worker count: `--workers 8`
3. Allocate more Redis memory: `512mb`

### Horizontal Scaling (Multiple Servers)
1. Load balancer (Nginx/HAProxy)
2. Separate Redis server
3. Shared ChromaDB (NFS mount or S3)
4. Database for conversations (PostgreSQL)

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs backend

# Check disk space
df -h

# Check memory
free -h

# Restart services
docker-compose restart
```

### High Memory Usage

```bash
# Check Docker stats
docker stats

# Reduce worker count
# Edit docker-compose.yml: --workers 2

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

### Slow Responses

1. Check cache hit rate in `/api/v1/metrics`
2. Monitor LLM API response times
3. Verify Redis is running
4. Check network latency to OpenAI

### ChromaDB Issues

```bash
# Rebuild vector database
docker-compose exec backend python scripts/load_knowledge.py --reset

# Check collection count
curl http://localhost:8001/api/v1/collections
```

---

## Health Monitoring

### Uptime Monitoring Services (Free Tier)
- **UptimeRobot**: 50 monitors, 5-min checks
- **Healthchecks.io**: Cron job monitoring
- **StatusCake**: Uptime and performance

### Custom Health Check Script

```bash
#!/bin/bash
HEALTH_URL="http://localhost:8000/api/v1/health/detailed"
RESPONSE=$(curl -s $HEALTH_URL)

if echo "$RESPONSE" | grep -q "healthy"; then
    echo "✓ Service healthy"
    exit 0
else
    echo "✗ Service unhealthy"
    echo "$RESPONSE"
    # Send alert (email, Slack, etc.)
    exit 1
fi
```

---

## Maintenance Checklist

### Daily
- [ ] Check error logs for issues
- [ ] Monitor cost in OpenAI dashboard
- [ ] Verify all services running

### Weekly
- [ ] Review cache hit rate metrics
- [ ] Check disk space usage
- [ ] Review rate limit violations

### Monthly
- [ ] Update dependencies (security patches)
- [ ] Review and optimize costs
- [ ] Test backup restoration
- [ ] Renew SSL cert (auto with Let's Encrypt)

---

## Emergency Procedures

### Service Crash
```bash
docker-compose restart backend
```

### Out of Disk Space
```bash
docker system prune -a --volumes
```

### High API Costs
```bash
# Temporarily disable service
docker-compose stop backend

# Investigate in logs
docker-compose logs backend | grep "tokens_used"
```

### Data Loss
```bash
# Restore from backup
tar -xzf /opt/backups/chroma_YYYYMMDD.tar.gz -C /
docker-compose restart
```

---

## Production Deployment Checklist

- [ ] VPS provisioned and configured
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned/uploaded
- [ ] .env configured with production values
- [ ] JWT secret generated and set
- [ ] OpenAI API key configured
- [ ] Services started with docker-compose
- [ ] Knowledge base loaded
- [ ] Nginx installed and configured
- [ ] SSL certificate obtained
- [ ] Firewall (UFW) enabled
- [ ] Fail2Ban configured
- [ ] Automated backups scheduled
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] API tested end-to-end
- [ ] Documentation reviewed

---

## Support & Resources

- **Logs**: `docker-compose logs -f`
- **Metrics**: `http://your-domain.com/api/v1/metrics`
- **Health**: `http://your-domain.com/api/v1/health/detailed`
- **API Docs**: `http://your-domain.com/docs`

For issues, check logs first, then consult troubleshooting section above.

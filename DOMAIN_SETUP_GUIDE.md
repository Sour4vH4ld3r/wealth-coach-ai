i# Domain Setup Guide - Wealth Warriors Hub
# Complete Nginx Configuration for Production Deployment

## Overview

This guide will help you set up three domains with Nginx:

- **api.wealthwarriorshub.in** - Backend API (Port 8000)
- **webchat.wealthwarriorshub.in** - Frontend Application
- **wealthwarriorshub.in** - Landing Page

**Server IP**: `Your-DigitalOcean-Droplet-IP`

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [DNS Configuration](#dns-configuration)
3. [Install Nginx](#install-nginx)
4. [Configure Backend API](#configure-backend-api)
5. [Configure Frontend](#configure-frontend)
6. [Configure Landing Page](#configure-landing-page)
7. [SSL Setup with Let's Encrypt](#ssl-setup-with-lets-encrypt)
8. [Testing & Verification](#testing--verification)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- ✅ Ubuntu server (DigitalOcean Droplet)
- ✅ Root or sudo access
- ✅ Backend running on port 8000
- ✅ Domain purchased and access to DNS management
- ✅ Firewall configured (ports 80, 443, 8000)

---

## DNS Configuration

### Step 1: Add DNS Records

Go to your domain registrar's DNS management panel and add these A records:

| Type | Host                | Value (Points to)              | TTL  |
|------|---------------------|--------------------------------|------|
| A    | api                 | YOUR_SERVER_IP                 | 3600 |
| A    | webchat             | YOUR_SERVER_IP                 | 3600 |
| A    | @                   | YOUR_SERVER_IP                 | 3600 |
| A    | www                 | YOUR_SERVER_IP                 | 3600 |

**Example:**
```
A    api        157.245.110.123    3600
A    webchat    157.245.110.123    3600
A    @          157.245.110.123    3600
A    www        157.245.110.123    3600
```

### Step 2: Verify DNS Propagation

Wait 5-15 minutes, then verify:

```bash
# Check API subdomain
dig api.wealthwarriorshub.in +short

# Check webchat subdomain
dig webchat.wealthwarriorshub.in +short

# Check root domain
dig wealthwarriorshub.in +short

# Should all return your server IP
```

---

## Install Nginx

### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Nginx

```bash
sudo apt install nginx -y
```

### Step 3: Start and Enable Nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

### Step 4: Configure Firewall

```bash
# Allow Nginx through firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# Verify
sudo ufw status
```

### Step 5: Test Nginx

Visit `http://YOUR_SERVER_IP` in browser - you should see the Nginx welcome page.

--- completed ...............

## Configure Backend API

### Step 1: Create Backend Nginx Config

```bash
sudo nano /etc/nginx/sites-available/api.wealthwarriorshub.in
```

**Paste this configuration:**

```nginx
# Backend API Configuration
# api.wealthwarriorshub.in

server {
    listen 80;
    listen [::]:80;

    server_name api.wealthwarriorshub.in;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/api.wealthwarriorshub.in.access.log;
    error_log /var/log/nginx/api.wealthwarriorshub.in.error.log;

    # API endpoint
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;

        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support (if needed)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # Block common exploits
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### Step 2: Enable Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/api.wealthwarriorshub.in /etc/nginx/sites-enabled/


sudo nano /etc/nginx/sites-available/sujoydasmotivation.com
# sudo ln -s /etc/nginx/sites-available/sujoydasmotivation.com /etc/nginx/sites-enabled/


# Test configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

### Step 3: Verify API

```bash
# Test from server
curl http://api.wealthwarriorshub.in/health

# Should return: {"status":"healthy"}
```

---

## Configure Frontend

### Step 1: Create Frontend Directory

```bash
sudo mkdir -p /var/www/webchat.wealthwarriorshub.in
sudo chown -R $USER:$USER /var/www/webchat.wealthwarriorshub.in
```

### Step 2: Create Frontend Nginx Config

```bash
sudo nano /etc/nginx/sites-available/webchat.wealthwarriorshub.in
```

**Paste this configuration:**

```nginx
# Frontend Application Configuration
# webchat.wealthwarriorshub.in

server {
    listen 80;
    listen [::]:80;

    server_name webchat.wealthwarriorshub.in;

    root /var/www/webchat.wealthwarriorshub.in;
    index index.html index.htm;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/webchat.wealthwarriorshub.in.access.log;
    error_log /var/log/nginx/webchat.wealthwarriorshub.in.error.log;

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Disable caching for HTML
    location ~* \.html$ {
        expires -1;
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate";
    }

    # Block common exploits
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;
}
```

### Step 3: Deploy Frontend Files

```bash
# Upload your built frontend files to:
# /var/www/webchat.wealthwarriorshub.in/

# Example using SCP from your local machine:
scp -r ./dist/* root@YOUR_SERVER_IP:/var/www/webchat.wealthwarriorshub.in/

# Or using rsync:
rsync -avz --progress ./dist/ root@YOUR_SERVER_IP:/var/www/webchat.wealthwarriorshub.in/
```

### Step 4: Enable Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/webchat.wealthwarriorshub.in /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Configure Landing Page

### Step 1: Create Landing Page Directory

```bash
sudo mkdir -p /var/www/wealthwarriorshub.in
sudo chown -R $USER:$USER /var/www/wealthwarriorshub.in
```

### Step 2: Create Landing Page Nginx Config

```bash
sudo nano /etc/nginx/sites-available/wealthwarriorshub.in
```

**Paste this configuration:**

```nginx
# Landing Page Configuration
# wealthwarriorshub.in

server {
    listen 80;
    listen [::]:80;

    server_name wealthwarriorshub.in www.wealthwarriorshub.in;

    root /var/www/wealthwarriorshub.in;
    index index.html index.htm;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/wealthwarriorshub.in.access.log;
    error_log /var/log/nginx/wealthwarriorshub.in.error.log;

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;
}
```

### Step 3: Create Simple Landing Page

```bash
# Create a basic landing page
sudo nano /var/www/wealthwarriorshub.in/index.html
```

**Basic HTML template:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wealth Warriors Hub</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 2rem;
            max-width: 800px;
        }
        h1 { font-size: 3rem; margin-bottom: 1rem; }
        p { font-size: 1.2rem; margin-bottom: 2rem; }
        .links { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
        .btn {
            padding: 1rem 2rem;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Wealth Warriors Hub</h1>
        <p>Your AI-Powered Financial Coaching Platform</p>
        <div class="links">
            <a href="https://webchat.wealthwarriorshub.in" class="btn">Launch App</a>
            <a href="https://api.wealthwarriorshub.in/docs" class="btn">API Docs</a>
        </div>
    </div>
</body>
</html>
```

### Step 4: Enable Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/wealthwarriorshub.in /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## SSL Setup with Let's Encrypt

### Step 1: Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Step 2: Obtain SSL Certificates

**Important:** DNS must be propagated and pointing to your server before running these commands!

```bash
# Get certificate for API
sudo certbot --nginx -d api.wealthwarriorshub.in

# Get certificate for frontend
sudo certbot --nginx -d webchat.wealthwarriorshub.in

# Get certificate for landing page (including www)
sudo certbot --nginx -d wealthwarriorshub.in -d www.wealthwarriorshub.in

sudo certbot --nginx -d sujoydasmotivation.com -d www.sujoydasmotivation.com

sudo certbot --nginx -d souravhalder.in -d www.souravhalder.in -d dev.souravhalder.in
```

**During setup:**
- Enter your email address
- Agree to Terms of Service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

### Step 3: Verify Auto-Renewal

```bash
# Test renewal process
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

Certificates auto-renew every 60 days. The timer runs twice daily.

### Step 4: Update Nginx Configs (Certbot does this automatically)

After running Certbot, your configs will have SSL blocks added. Verify:

```bash
# Check API config
sudo cat /etc/nginx/sites-available/api.wealthwarriorshub.in | grep ssl

# Should show SSL certificate paths
```

---

## Testing & Verification

### Step 1: Test Each Domain

```bash
# Test API
curl https://api.wealthwarriorshub.in/health

# Test frontend (should return HTML)
curl -I https://webchat.wealthwarriorshub.in

# Test landing page (should return HTML)
curl -I https://wealthwarriorshub.in
```

### Step 2: Test SSL Certificates

Visit each domain in a browser and check for the padlock icon:

- ✅ https://api.wealthwarriorshub.in/health
- ✅ https://webchat.wealthwarriorshub.in
- ✅ https://wealthwarriorshub.in

### Step 3: Test SSL Rating

Check SSL configuration quality:

```bash
# Use SSL Labs (online)
# Visit: https://www.ssllabs.com/ssltest/

# Or use testssl.sh
git clone https://github.com/drwetter/testssl.sh.git
cd testssl.sh
./testssl.sh https://api.wealthwarriorshub.in
```

### Step 4: Monitor Logs

```bash
# Watch API logs
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.access.log

# Watch error logs
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.error.log

# Check all Nginx logs
sudo tail -f /var/log/nginx/*.log
```

---

## Troubleshooting

### Issue: 502 Bad Gateway (API)

**Cause:** Backend not running or connection refused.

**Fix:**
```bash
# Check if backend is running
docker compose -f docker-compose.backend.yml ps

# Check backend health
curl http://localhost:8000/health

# Restart backend
docker compose -f docker-compose.backend.yml restart

# Check Nginx error logs
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.error.log
```

### Issue: 404 Not Found (Frontend/Landing)

**Cause:** Files not uploaded or wrong directory.

**Fix:**
```bash
# Check if files exist
ls -la /var/www/webchat.wealthwarriorshub.in/
ls -la /var/www/wealthwarriorshub.in/

# Check file permissions
sudo chown -R www-data:www-data /var/www/webchat.wealthwarriorshub.in
sudo chown -R www-data:www-data /var/www/wealthwarriorshub.in
```

### Issue: SSL Certificate Error

**Cause:** DNS not propagated or wrong domain name.

**Fix:**
```bash
# Verify DNS
dig api.wealthwarriorshub.in +short

# Delete and recreate certificate
sudo certbot delete --cert-name api.wealthwarriorshub.in
sudo certbot --nginx -d api.wealthwarriorshub.in
```

### Issue: Nginx Won't Start

**Cause:** Configuration syntax error.

**Fix:**
```bash
# Test configuration
sudo nginx -t

# Check which config has error
sudo nginx -T | grep -B5 "test failed"

# View detailed error
sudo systemctl status nginx.service
```

### Issue: CORS Errors (API)

**Cause:** CORS not configured in backend.

**Fix:** Add to API Nginx config:

```nginx
location / {
    # Add CORS headers
    add_header 'Access-Control-Allow-Origin' 'https://webchat.wealthwarriorshub.in' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;

    # Handle preflight
    if ($request_method = 'OPTIONS') {
        return 204;
    }

    proxy_pass http://localhost:8000;
    # ... rest of proxy config
}
```

---

## Security Best Practices

### 1. Enable Rate Limiting

Add to Nginx http block (`/etc/nginx/nginx.conf`):

```nginx
http {
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=20r/s;

    # ... rest of config
}
```

Add to API location block:

```nginx
location / {
    limit_req zone=api_limit burst=20 nodelay;
    # ... rest of config
}
```

### 2. Hide Nginx Version

Edit `/etc/nginx/nginx.conf`:

```nginx
http {
    server_tokens off;
    # ... rest of config
}
```

### 3. Configure Fail2Ban

```bash
# Install fail2ban
sudo apt install fail2ban -y

# Create Nginx jail
sudo nano /etc/fail2ban/jail.local
```

Add:

```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/*error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/*error.log
```

```bash
# Restart fail2ban
sudo systemctl restart fail2ban
```

### 4. Regular Updates

```bash
# Set up unattended upgrades
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## Maintenance Commands

### Restart Services

```bash
# Restart Nginx
sudo systemctl restart nginx

# Reload Nginx (zero downtime)
sudo systemctl reload nginx

# Restart backend
cd /opt/wealth-coach-ai
docker compose -f docker-compose.backend.yml restart
```

### Check Status

```bash
# Nginx status
sudo systemctl status nginx

# Backend status
docker compose -f docker-compose.backend.yml ps

# Check ports
sudo netstat -tulpn | grep -E ':(80|443|8000)'
```

### View Logs

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Backend logs
docker compose -f docker-compose.backend.yml logs -f
```

### Certificate Management

```bash
# List certificates
sudo certbot certificates

# Renew all certificates
sudo certbot renew

# Renew specific certificate
sudo certbot renew --cert-name api.wealthwarriorshub.in
```

---

## Quick Reference

### File Locations

```
Nginx configs:      /etc/nginx/sites-available/
Enabled sites:      /etc/nginx/sites-enabled/
Nginx logs:         /var/log/nginx/
SSL certificates:   /etc/letsencrypt/live/
Frontend files:     /var/www/webchat.wealthwarriorshub.in/
Landing page:       /var/www/wealthwarriorshub.in/
Backend:            /opt/wealth-coach-ai/
```

### Common Commands

```bash
# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Backend health check
curl http://localhost:8000/health

# View SSL certificate info
sudo certbot certificates

# Renew SSL certificates
sudo certbot renew --dry-run
```

---

## Support & Resources

- **Nginx Documentation**: https://nginx.org/en/docs/
- **Certbot Documentation**: https://certbot.eff.org/
- **DigitalOcean Tutorials**: https://www.digitalocean.com/community/tutorials
- **SSL Labs Test**: https://www.ssllabs.com/ssltest/

---

## Completion Checklist

- [ ] DNS records configured for all domains
- [ ] DNS propagated (verified with dig)
- [ ] Nginx installed and running
- [ ] Backend API accessible via domain
- [ ] Frontend deployed and accessible
- [ ] Landing page deployed and accessible
- [ ] SSL certificates installed for all domains
- [ ] HTTPS redirects working
- [ ] Health checks passing
- [ ] Logs being written correctly
- [ ] Auto-renewal configured for SSL
- [ ] Firewall rules configured
- [ ] Security headers added
- [ ] Rate limiting configured (optional)

---

**Your domains are now live! 🚀**

- Backend API: https://api.wealthwarriorshub.in
- Frontend App: https://webchat.wealthwarriorshub.in
- Landing Page: https://wealthwarriorshub.in

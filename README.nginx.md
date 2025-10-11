# 🌊 Backend + Nginx Docker - Quick Start

Deploy FastAPI backend with Nginx reverse proxy in **5 commands**.

---

## ⚡ Super Quick Deploy

**On your server (IP: 167.71.226.46):**

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh && apt install docker-compose-plugin -y

# 2. Clone project
cd /opt && mkdir -p wealth-coach-ai && cd wealth-coach-ai
git clone https://github.com/Sour4vH4ld3r/wealth-coach-ai.git .

# 3. Configure
cp .env.template .env
nano .env  # Add your API keys (see below)

# 4. Deploy
./deploy-nginx.sh

# ✅ Done! API live at: http://167.71.226.46/
```

---

## 🔑 What to Add in .env

```bash
# Get from https://supabase.com/
DATABASE_URL=postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres

# Get from https://upstash.com/
REDIS_URL=redis://default:pass@region.upstash.io:port

# Get from https://platform.openai.com/
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxx

# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=<paste-generated-secret>
```

---

## 🎯 What You Get

```
Internet → Nginx (Port 80/443) → Backend API (Port 8000)
                                      ↓
                         Supabase + Upstash + OpenAI
```

**Features:**
- ✅ Production-ready Nginx reverse proxy
- ✅ Automatic SSL/HTTPS support (with domain)
- ✅ Load balancing ready
- ✅ Health monitoring
- ✅ Automatic restarts
- ✅ Centralized logging

---

## 🌐 Access Your API

```
🔗 API: http://167.71.226.46/
📖 Docs: http://167.71.226.46/docs
✅ Health: http://167.71.226.46/health
```

---

## 🔒 Optional: Add Domain & SSL

### 1. Point Domain

Add DNS A Record:
```
api.yourdomain.com → 167.71.226.46
```

### 2. Get SSL Certificate

```bash
# Install certbot
apt install certbot -y

# Stop nginx temporarily
docker compose -f docker-compose.nginx.yml stop nginx

# Get certificate
certbot certonly --standalone -d api.yourdomain.com

# Copy certificates
mkdir -p config/nginx/ssl
cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem config/nginx/ssl/
cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem config/nginx/ssl/
```

### 3. Update Nginx Config

```bash
nano config/nginx/conf.d/backend.conf
```

1. Change `server_name _;` to `server_name api.yourdomain.com;`
2. Uncomment the HTTPS server block (remove all `#`)
3. Save file

### 4. Restart

```bash
docker compose -f docker-compose.nginx.yml up -d
```

**Now access via HTTPS:**
```
https://api.yourdomain.com/health
```

---

## 📊 Manage Services

```bash
# View logs
docker compose -f docker-compose.nginx.yml logs -f

# Restart
docker compose -f docker-compose.nginx.yml restart

# Stop
docker compose -f docker-compose.nginx.yml down

# Update
git pull && ./deploy-nginx.sh

# Check status
docker compose -f docker-compose.nginx.yml ps
```

---

## 🔥 Configure Firewall

```bash
ufw enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
```

---

## 🚨 Troubleshooting

### Port 80/443 Already in Use

```bash
# Check what's using the ports
lsof -i :80
lsof -i :443

# Stop conflicting service
systemctl stop nginx  # If nginx running outside Docker
```

### Can't Access from Outside

```bash
# Check firewall
ufw status

# Open ports
ufw allow 80/tcp
ufw allow 443/tcp
```

### Containers Won't Start

```bash
# Check logs
docker compose -f docker-compose.nginx.yml logs

# Rebuild
docker compose -f docker-compose.nginx.yml up -d --build
```

---

## 📖 Full Documentation

For detailed guide with screenshots: [NGINX_DOCKER_DEPLOY.md](NGINX_DOCKER_DEPLOY.md)

---

## 💰 Monthly Costs

```
DigitalOcean (4vCPU, 8GB): $48/month
Supabase (Free):           $0/month
Upstash (Free):            $0/month
OpenAI API:                $10-50/month
────────────────────────────────────
Total:                     $58-98/month
```

---

## ✅ Production Checklist

```
☐ Docker installed
☐ Repository cloned
☐ .env configured
☐ Supabase database + pgvector enabled
☐ Upstash Redis created
☐ OpenAI API key obtained
☐ Containers running
☐ Health check passing
☐ Firewall configured
☐ Domain pointed (optional)
☐ SSL installed (optional)
```

---

## 🎉 You're Live!

```
🔗 http://167.71.226.46/
📖 http://167.71.226.46/docs
✅ http://167.71.226.46/health
```

**Questions?** Check [NGINX_DOCKER_DEPLOY.md](NGINX_DOCKER_DEPLOY.md) or open an issue.

---

**Made with ❤️ for easy deployment**

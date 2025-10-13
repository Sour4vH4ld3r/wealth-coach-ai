# Frontend Deployment Guide

Production deployment guide for Wealth Coach AI React frontend.

---

## Quick Deploy

### 1. On Your Droplet

```bash
# Clone/pull latest code
cd /path/to/wealthWarriors

# Build and start frontend
docker-compose -f docker-compose.frontend.yml up -d --build
```

**That's it!** Frontend will be available on port 3000.

---

## Deployment Options

### Option 1: Standalone Frontend (Port 3000)

```bash
docker-compose -f docker-compose.frontend.yml up -d --build
```

**Access**: `http://your-droplet-ip:3000`

### Option 2: Change to Port 80

Edit `docker-compose.frontend.yml`:
```yaml
ports:
  - "80:80"  # Change from 3000:80
```

**Access**: `http://your-droplet-ip`

### Option 3: Custom API URL

```bash
docker-compose -f docker-compose.frontend.yml build \
  --build-arg VITE_API_URL=https://your-custom-api.com \
  && docker-compose -f docker-compose.frontend.yml up -d
```

---

## File Structure

```
wealthWarriors/
├── docker-compose.frontend.yml       # Frontend Docker Compose
└── frontend/web/frontend-web/web-test/
    ├── Dockerfile.prod               # Production Dockerfile
    ├── nginx.conf                    # Nginx configuration
    ├── .env.example                  # Environment variables template
    └── src/                          # React source code
```

---

## Configuration

### Environment Variables

Create `.env` file in `frontend/web/frontend-web/web-test/`:

```bash
# Copy example
cd frontend/web/frontend-web/web-test
cp .env.example .env

# Edit values
nano .env
```

**Available variables:**
- `VITE_API_URL` - Backend API URL (default: https://api.wealthwarriorshub.in)
- `VITE_APP_ENV` - Environment (default: production)
- `VITE_DEBUG` - Debug mode (default: false)

### Build Arguments

Pass at build time:
```bash
docker-compose -f docker-compose.frontend.yml build \
  --build-arg VITE_API_URL=https://api.example.com \
  --build-arg VITE_DEBUG=true
```

---

## Docker Commands

### Build
```bash
docker-compose -f docker-compose.frontend.yml build
```

### Start
```bash
docker-compose -f docker-compose.frontend.yml up -d
```

### Stop
```bash
docker-compose -f docker-compose.frontend.yml down
```

### View Logs
```bash
docker-compose -f docker-compose.frontend.yml logs -f
```

### Restart
```bash
docker-compose -f docker-compose.frontend.yml restart
```

### Rebuild & Restart
```bash
docker-compose -f docker-compose.frontend.yml up -d --build --force-recreate
```

---

## Health Check

```bash
# Check container status
docker ps | grep wealth-coach-frontend

# Check health endpoint
curl http://localhost:3000/health

# Expected: "healthy"
```

---

## Nginx Configuration

The included `nginx.conf` provides:

✅ **React Router support** - All routes serve index.html
✅ **Gzip compression** - Faster load times
✅ **Static asset caching** - 1 year cache for JS/CSS/images
✅ **Security headers** - XSS protection, frame options
✅ **Health check endpoint** - `/health` for monitoring

### Custom Nginx Config

Edit `frontend/web/frontend-web/web-test/nginx.conf` and rebuild.

---

## Production Checklist

- [ ] Update `VITE_API_URL` to production backend URL
- [ ] Set `VITE_DEBUG=false`
- [ ] Build with production Dockerfile (`Dockerfile.prod`)
- [ ] Verify health check: `curl http://localhost:3000/health`
- [ ] Test frontend: Open in browser
- [ ] Check logs: `docker-compose -f docker-compose.frontend.yml logs`
- [ ] Setup reverse proxy (optional, see below)

---

## Reverse Proxy Setup (Optional)

### Using Nginx on Host

Add to your host nginx config:

```nginx
server {
    listen 80;
    server_name app.wealthwarriorshub.in;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Using Caddy

```caddy
app.wealthwarriorshub.in {
    reverse_proxy localhost:3000
}
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.frontend.yml logs

# Check if port is in use
sudo lsof -i :3000

# Remove and recreate
docker-compose -f docker-compose.frontend.yml down
docker-compose -f docker-compose.frontend.yml up -d --build
```

### Build Fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose -f docker-compose.frontend.yml build --no-cache
```

### API Connection Issues

1. Check `VITE_API_URL` is correct
2. Verify backend is running: `curl https://api.wealthwarriorshub.in/health`
3. Check browser console for errors
4. Verify CORS settings on backend

### White Screen / 404 Errors

1. Check nginx config has `try_files $uri $uri/ /index.html`
2. Verify build created files: `docker exec wealth-coach-frontend ls /usr/share/nginx/html`
3. Check nginx logs: `docker logs wealth-coach-frontend`

---

## Monitoring

### Container Status
```bash
docker ps --filter name=wealth-coach-frontend
```

### Resource Usage
```bash
docker stats wealth-coach-frontend
```

### Logs
```bash
# Real-time logs
docker logs -f wealth-coach-frontend

# Last 100 lines
docker logs --tail 100 wealth-coach-frontend
```

---

## Updating

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.frontend.yml up -d --build
```

---

## Security

### HTTPS (Recommended)

Use a reverse proxy (nginx/caddy) with Let's Encrypt:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d app.wealthwarriorshub.in
```

### Security Headers

Already included in `nginx.conf`:
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block

---

## Performance

### Build Optimization

Already optimized:
- ✅ Multi-stage Docker build
- ✅ Gzip compression
- ✅ Static asset caching (1 year)
- ✅ Minified production build

### CDN (Optional)

For global distribution, deploy to:
- **Vercel** - Zero config React deployment
- **Netlify** - Automatic builds from Git
- **Cloudflare Pages** - Global CDN with edge caching

---

## Support

**Issues?**
1. Check logs: `docker-compose -f docker-compose.frontend.yml logs`
2. Verify backend: `curl https://api.wealthwarriorshub.in/health`
3. Test locally: `cd frontend/web/frontend-web/web-test && npm run dev`

**Documentation:**
- React: https://react.dev
- Vite: https://vitejs.dev
- Docker: https://docs.docker.com

---

**Version**: 1.0.0
**Date**: 2025-01-13
**Status**: ✅ Production Ready

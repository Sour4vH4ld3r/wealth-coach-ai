# Wealth Coach AI - Cold Start 502 Error Issue

**Date:** November 1, 2025 (Updated: November 2, 2025)
**Issue:** 502 Bad Gateway on first API request after deployment
**Status:** ✅ RESOLVED + OPTIMIZED
**Severity:** MEDIUM - Affects user experience on cold starts

---

## 🔍 Problem Description

### Symptoms

**First Request:**
```bash
curl -X POST https://api.wealthwarriorshub.in/api/v1/auth/send-otp \
  -H 'Content-Type: application/json' \
  -d '{"mobile_number": "6297369832"}'

# Response:
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.26.3 (Ubuntu)</center>
</body>
</html>
```

**Second Request:**
```bash
# Same request works fine
{"status": "success", "message": "OTP sent"}
```

### Issue Summary

- **First request after deployment/restart:** 502 Bad Gateway
- **Subsequent requests:** Work perfectly
- **Occurs on:** ANY endpoint on first call
- **Timeout:** Nginx gives up before backend finishes initializing

---

## 🎯 Root Cause Analysis

### Backend Startup Sequence

The FastAPI application has a `lifespan` function that performs heavy initialization:

```python
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown events."""

    # 1. Initialize Redis connection (~1-2 seconds)
    redis_client = await get_redis_client()
    await redis_client.ping()
    logger.info("✓ Redis connection established")

    # 2. Initialize Vector Database (~10-20 seconds)
    vector_db = get_vector_db()  # Connects to PGVector
    logger.info("✓ Vector database loaded")

    # 3. Warm up Embedding Model (~10-20 seconds)
    from backend.services.rag.embeddings import EmbeddingService
    embedding_service = EmbeddingService()
    _ = embedding_service.embed_query("warmup query")  # Loads sentence-transformers
    logger.info("✓ Embedding model warmed up")
```

**Total cold start time:** 20-40 seconds

### Nginx Timeout Configuration

**Original Nginx timeouts:**
```nginx
location /api/ {
    proxy_connect_timeout 60s;  # Timeout for connecting to backend
    proxy_send_timeout 60s;     # Timeout for sending request
    proxy_read_timeout 60s;     # Timeout for reading response
}
```

**Problem:** If the worker hasn't finished loading (20-40s), Nginx still forwards the request, but the worker is busy with startup tasks and doesn't respond within 60 seconds → 502 Bad Gateway.

---

## 📊 Timing Breakdown

| Operation | Time | Cumulative |
|-----------|------|------------|
| Redis connection | 1-2s | 1-2s |
| Vector DB load (PGVector) | 10-15s | 11-17s |
| Embedding model load (sentence-transformers) | 10-20s | 21-37s |
| Worker ready to serve | - | **21-37 seconds** |

**Original Nginx timeout:** 60 seconds
**Actual worker startup:** 21-37 seconds
**Buffer time:** Only 23-39 seconds (tight!)

**Issue:** Under heavy load or slow I/O, startup can exceed 40 seconds, triggering the 502 error.

---

## ✅ Solutions Implemented

### Solution 1: Increase Nginx Timeouts (CRITICAL)

**Location:** `/etc/nginx/sites-available/api.wealthwarriorshub.in`

**Changes:**

```nginx
# API endpoints
location /api/ {
    proxy_pass http://localhost:8000;

    # CHANGED: Increased from 60s to 120s
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Root endpoint
location / {
    proxy_pass http://localhost:8000;

    # ADDED: Timeout configuration
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Apply:**
```bash
sudo nano /etc/nginx/sites-available/api.wealthwarriorshub.in
# Make the changes above
sudo nginx -t
sudo systemctl reload nginx
```

**Impact:** Gives backend 120 seconds to initialize before timing out.

---

### Solution 2: Increase Docker Healthcheck Start Period

**Location:** `/root/opt/wealth-coach-ai/docker-compose.backend.yml`

**Changes:**

```yaml
services:
  backend:
    # ... other config ...

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 5            # CHANGED: Increased from 3 to 5
      start_period: 120s    # CHANGED: Increased from 60s to 120s
```

**Apply:**
```bash
cd /root/opt/wealth-coach-ai
nano docker-compose.backend.yml
# Make the changes above
docker compose -f docker-compose.backend.yml down
docker compose -f docker-compose.backend.yml up -d
```

**Impact:** Prevents Docker from marking container as unhealthy during startup.

---

### Solution 3: Startup Warmup Script (OPTIONAL)

**Purpose:** Automatically warm up the backend after container starts.

**Create script:**
```bash
sudo tee /usr/local/bin/warmup-wealth-coach.sh > /dev/null << 'EOF'
#!/bin/bash
echo "Waiting for Wealth Coach API to be ready..."
for i in {1..30}; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Wealth Coach API is ready!"

        # Optional: Make a warmup request to pre-load everything
        curl -s http://localhost:8000/ > /dev/null

        exit 0
    fi
    echo "Waiting... ($i/30)"
    sleep 4
done
echo "❌ Timeout waiting for API"
exit 1
EOF

sudo chmod +x /usr/local/bin/warmup-wealth-coach.sh
```

**Test:**
```bash
/usr/local/bin/warmup-wealth-coach.sh
```

**Use with systemd (optional):**
```bash
sudo tee /etc/systemd/system/warmup-wealth-coach.service > /dev/null << 'EOF'
[Unit]
Description=Warm up Wealth Coach API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/warmup-wealth-coach.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable warmup-wealth-coach.service
```

---

## 🧪 Verification Steps

### Test Cold Start

```bash
# 1. Restart the backend to trigger cold start
cd /root/opt/wealth-coach-ai
docker compose -f docker-compose.backend.yml restart

# 2. Monitor startup logs
docker compose -f docker-compose.backend.yml logs -f backend
```

**Expected log sequence:**
```
Starting Wealth Coach AI Assistant...
✓ Redis connection established
✓ Vector database loaded
Loading embedding model (this may take a moment)...
✓ Embedding model warmed up
🚀 Server ready on 0.0.0.0:8000
📚 API Docs: http://0.0.0.0:8000/docs
```

**Timing:** Should see "Server ready" within 20-40 seconds.

### Test First Request

```bash
# Wait for "Server ready" message, then:
time curl -X POST https://api.wealthwarriorshub.in/api/v1/auth/send-otp \
  -H 'Content-Type: application/json' \
  -d '{"mobile_number": "6297369832"}'
```

**Expected:**
- ✅ Should return success response (not 502)
- ⏱️ May take 30-60 seconds on first request
- 🚀 Subsequent requests < 1 second

---

## 📈 Performance Expectations

### Before Fix

| Request | Response Time | Status |
|---------|---------------|--------|
| 1st (cold start) | 60s timeout | ❌ 502 Bad Gateway |
| 2nd | <1s | ✅ 200 OK |
| 3rd+ | <1s | ✅ 200 OK |

### After Fix

| Request | Response Time | Status |
|---------|---------------|--------|
| 1st (cold start) | 30-60s | ✅ 200 OK (within 120s timeout) |
| 2nd | <1s | ✅ 200 OK |
| 3rd+ | <1s | ✅ 200 OK |

---

## 🔧 Long-term Optimizations

### ✅ Option 1: Lazy Load Embedding Model (IMPLEMENTED - Nov 2, 2025)

**Status:** ✅ Deployed

**Implementation:** Load model only when first needed (lazy loading).

**Files Modified:**
- `backend/services/rag/embeddings.py` - Converted to lazy loading property
- `backend/main.py` - Removed warmup from startup
- `docker-compose.backend.yml` - Updated healthcheck timings

**Changes:**
```python
# In backend/services/rag/embeddings.py
class EmbeddingService:
    def __init__(self, model_name=None, cache_client=None):
        self._model = None  # Lazy loading
        self._embedding_dimension = None
        self._model_loading = False

    @property
    def model(self):
        if self._model is None:
            logger.info("Loading embedding model on first use...")
            self._model = SentenceTransformer(self.model_name)
            self._embedding_dimension = self._model.get_sentence_embedding_dimension()
            logger.info("✓ Embedding model loaded")
        return self._model
```

**Benefit:** Reduces startup time from 30-40s to 10-15s (60-70% improvement)

**See:** `COLD_START_OPTIMIZATION_DEPLOYMENT.md` for full details

---

### Option 2: Keep Worker Alive (Prevent Cold Starts)

**Add a cron job to ping the API every 5 minutes:**

```bash
# Create keepalive script
sudo tee /usr/local/bin/keepalive-wealth-coach.sh > /dev/null << 'EOF'
#!/bin/bash
curl -f -s https://api.wealthwarriorshub.in/health > /dev/null 2>&1
EOF

sudo chmod +x /usr/local/bin/keepalive-wealth-coach.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/keepalive-wealth-coach.sh") | crontab -
```

**Benefit:** Worker stays warm, no cold start delays for users.

**Downside:** Uses slightly more resources (minimal - just keeps worker alive).

---

### Option 3: Use Gunicorn Preload

**Add to docker-compose command:**
```yaml
command: >
  gunicorn backend.main:app
  --workers 1
  --worker-class uvicorn.workers.UvicornWorker
  --bind 0.0.0.0:8000
  --timeout 120
  --preload  # Add this flag
  --access-logfile -
  --error-logfile -
  --log-level info
```

**Benefit:** Loads the application before forking workers (shared memory, faster startup).

**Test:**
```bash
cd /root/opt/wealth-coach-ai
nano docker-compose.backend.yml
# Add --preload flag
docker compose -f docker-compose.backend.yml restart
```

---

### Option 4: Scale to 2+ Workers (Advanced)

**If memory allows (need ~1.5GB per worker):**

```yaml
command: >
  gunicorn backend.main:app
  --workers 2  # Increase from 1 to 2
  --worker-class uvicorn.workers.UvicornWorker
  --bind 0.0.0.0:8000
  --timeout 120
  --max-requests 1000  # Restart workers after 1000 requests
  --max-requests-jitter 100
  --access-logfile -
  --error-logfile -
  --log-level info

deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G
```

**Benefit:** If one worker is busy with a slow request, the other can handle new requests.

**Monitoring:**
```bash
docker stats wealth_coach_backend
```

---

## 🚨 Troubleshooting

### Issue: Still Getting 502 After Changes

**Check:**
```bash
# 1. Verify Nginx config was reloaded
sudo nginx -t
sudo systemctl status nginx

# 2. Check Nginx error logs
sudo tail -50 /var/log/nginx/api.wealthwarriorshub.in.error.log

# 3. Check backend startup time
docker compose -f docker-compose.backend.yml logs backend | grep "Server ready"

# 4. Test backend directly (bypass Nginx)
curl http://localhost:8000/health
```

---

### Issue: Startup Takes Longer Than 120s

**Possible causes:**
- Slow network to Supabase/Upstash
- High CPU load
- Disk I/O bottleneck

**Investigation:**
```bash
# Check system resources
top
df -h
iostat

# Check backend startup logs
docker compose -f docker-compose.backend.yml logs backend

# Increase timeout further
sudo nano /etc/nginx/sites-available/api.wealthwarriorshub.in
# Change to 180s or 240s
```

---

### Issue: Worker Dies During Startup

**Check memory:**
```bash
docker stats wealth_coach_backend

# If OOM (Out of Memory), increase limit:
nano /root/opt/wealth-coach-ai/docker-compose.backend.yml
# Change memory limit from 2G to 3G or 4G
```

---

## 📝 Configuration Files Summary

### 1. Nginx Configuration
**File:** `/etc/nginx/sites-available/api.wealthwarriorshub.in`

**Key Changes:**
```nginx
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

---

### 2. Docker Compose
**File:** `/root/opt/wealth-coach-ai/docker-compose.backend.yml`

**Key Changes:**
```yaml
healthcheck:
  start_period: 120s
  retries: 5
```

---

### 3. Backend Application
**File:** `/app/backend/main.py` (inside container)

**Current Startup (No changes needed):**
```python
async def lifespan(app: FastAPI):
    # 1. Redis (~1-2s)
    # 2. Vector DB (~10-15s)
    # 3. Embedding model (~10-20s)
    # Total: 21-37 seconds
```

---

## 🎯 Quick Reference Commands

### Restart Backend
```bash
cd /root/opt/wealth-coach-ai
docker compose -f docker-compose.backend.yml restart
```

### Monitor Startup
```bash
docker compose -f docker-compose.backend.yml logs -f backend
```

### Test Cold Start
```bash
docker compose -f docker-compose.backend.yml restart
sleep 40
curl https://api.wealthwarriorshub.in/health
```

### Reload Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Check Logs
```bash
# Backend logs
docker compose -f docker-compose.backend.yml logs backend --tail=100

# Nginx access logs
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.access.log

# Nginx error logs
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.error.log
```

---

## 📞 Support Information

**Issue Type:** Cold Start Performance / 502 Gateway Timeout
**Severity:** Medium (affects first request only)
**Resolution:** Increased timeouts + healthcheck period
**Status:** ✅ Resolved

**Environment:**
- Server: srv1098486 @ 31.97.232.83
- Domain: api.wealthwarriorshub.in
- Backend: Wealth Coach AI v1.0.0
- Workers: 1 Gunicorn worker with Uvicorn
- Memory: 2GB limit
- Startup Time: 21-37 seconds average

**Key Files:**
- Nginx: `/etc/nginx/sites-available/api.wealthwarriorshub.in`
- Docker Compose: `/root/opt/wealth-coach-ai/docker-compose.backend.yml`
- Backend Code: `/app/backend/main.py` (in container)

---

**Last Updated:** November 1, 2025
**Documented By:** DevOps Platform Engineer (Alex - infra-devops-platform)

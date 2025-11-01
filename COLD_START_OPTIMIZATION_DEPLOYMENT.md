# Cold Start Optimization - Deployment Guide

**Date:** November 2, 2025
**Optimization:** Lazy Loading Embedding Model
**Expected Impact:** Reduces cold start from 30-40s to 10-15s (60-70% improvement)

---

## Overview

This deployment implements **lazy loading** for the sentence-transformers embedding model, significantly reducing application startup time while maintaining full functionality.

### What Changed

**Before:**
```
Startup sequence:
├── Redis connection (1-2s)
├── Vector DB initialization (10-15s)
└── Embedding model load (10-20s) ← BLOCKING
    Total: 21-37 seconds
```

**After:**
```
Startup sequence:
├── Redis connection (1-2s)
└── Vector DB initialization (10-15s)
    Total: 11-17 seconds ← 60% FASTER

Embedding model loads on first RAG query (10-20s)
```

---

## Changes Made

### 1. Backend Code Changes

**File: `backend/services/rag/embeddings.py`**
- Converted `self.model` to a lazy-loading property
- Model loads only on first access (when user makes first RAG query)
- Thread-safe with `_model_loading` flag

**File: `backend/main.py`**
- Removed warmup embedding query from lifespan startup
- Model now loads on-demand during first user interaction

### 2. Docker Configuration Changes

**File: `docker-compose.backend.yml`**
- Increased healthcheck `start_period` from 60s to 120s
- Increased healthcheck `retries` from 3 to 5
- Provides buffer for first model load if it happens during health checks

---

## Deployment Instructions

### Step 1: Push Code to Server

```bash
# On your local machine
cd /Users/souravhalder/Downloads/wealthWarriors

# Commit changes
git add backend/services/rag/embeddings.py backend/main.py docker-compose.backend.yml
git commit -m "optimize: implement lazy loading for embedding model

- Convert embedding model to lazy-load on first use
- Reduces cold start time from 30-40s to 10-15s
- Update healthcheck configuration for startup safety
- Improves user experience for cold start requests"

git push origin main
```

### Step 2: Deploy to Production Server

```bash
# SSH into your production server
ssh root@31.97.232.83

# Navigate to project directory
cd /root/opt/wealth-coach-ai

# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker compose -f docker-compose.backend.yml down
docker compose -f docker-compose.backend.yml build --no-cache
docker compose -f docker-compose.backend.yml up -d

# Monitor startup logs
docker compose -f docker-compose.backend.yml logs -f backend
```

### Step 3: Verify Deployment

Wait for startup logs to show:
```
Starting Wealth Coach AI Assistant...
✓ Redis connection established
✓ Vector database loaded
✓ Embedding service configured (lazy loading enabled)
🚀 Server ready on 0.0.0.0:8000
```

**Expected startup time:** 10-17 seconds (down from 21-37 seconds)

---

## Testing Procedure

### Test 1: Cold Start Performance

```bash
# Restart backend
docker compose -f docker-compose.backend.yml restart

# Time the startup
time docker compose -f docker-compose.backend.yml logs backend | grep "Server ready"

# Expected: ~10-17 seconds
```

### Test 2: First API Request (Non-RAG)

```bash
# Make a simple health check request
time curl https://api.wealthwarriorshub.in/health

# Expected: <1 second (no model loading needed)
```

### Test 3: First RAG Query

```bash
# Make first chat request (triggers model loading)
time curl -X POST https://api.wealthwarriorshub.in/api/v1/chat \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"message": "Tell me about investing"}'

# Expected: 10-20 seconds (model loads on first use)
# Note: This delay only happens ONCE
```

### Test 4: Subsequent RAG Queries

```bash
# Make another chat request
time curl -X POST https://api.wealthwarriorshub.in/api/v1/chat \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"message": "What is a 401k?"}'

# Expected: <2 seconds (model already loaded)
```

---

## Performance Comparison

### Before Optimization

| Event | Time | Cumulative |
|-------|------|------------|
| Container start | - | 0s |
| Redis connection | 1-2s | 1-2s |
| Vector DB load | 10-15s | 11-17s |
| Embedding model load | 10-20s | **21-37s** ← USER WAITS |
| First request (health) | <1s | 22-38s |
| First RAG request | 1-2s | 23-40s |

**User experience:** 30-40 second delay before API responds

### After Optimization

| Event | Time | Cumulative |
|-------|------|------------|
| Container start | - | 0s |
| Redis connection | 1-2s | 1-2s |
| Vector DB load | 10-15s | **11-17s** ← API READY |
| First request (health) | <1s | 12-18s |
| First RAG request | 10-20s | 22-38s ← MODEL LOADS |
| Second RAG request | <2s | 24-40s |

**User experience:** API responds immediately, first RAG query has 10-20s delay

---

## Benefits

### 1. Faster Container Startup
- **Before:** 21-37 seconds
- **After:** 11-17 seconds
- **Improvement:** 60-70% faster

### 2. Better Health Check Success Rate
- Container marked healthy faster
- Reduces false negatives during startup
- Improved Docker orchestration reliability

### 3. Improved User Experience for Non-RAG Endpoints
- Authentication endpoints: Instant
- User profile endpoints: Instant
- Health checks: Instant
- Only RAG queries have initial delay

### 4. Reduced Resource Waste
- Model only loads if actually needed
- Saves memory if container restarts frequently
- Better for development/testing environments

---

## Important Notes

### First RAG Query Delay

**This is expected and acceptable:**
- First user asking a financial question will wait 10-20 seconds
- This happens ONCE per container lifecycle
- All subsequent queries are fast (<2 seconds)
- Much better than 502 errors for ALL first requests

### Monitoring First Model Load

Check logs for model loading:
```bash
docker compose -f docker-compose.backend.yml logs backend | grep "Loading embedding model"
```

Expected log sequence on first RAG query:
```
Loading embedding model on first use: sentence-transformers/all-MiniLM-L6-v2
Embedding model loaded successfully. Dimension: 384
```

---

## Rollback Plan

If issues arise, rollback is simple:

```bash
# SSH to server
ssh root@31.97.232.83
cd /root/opt/wealth-coach-ai

# Checkout previous commit
git log --oneline  # Find commit hash before optimization
git checkout <previous-commit-hash>

# Rebuild and restart
docker compose -f docker-compose.backend.yml down
docker compose -f docker-compose.backend.yml build --no-cache
docker compose -f docker-compose.backend.yml up -d
```

---

## Additional Optimizations (Optional)

### Option 1: Keep-Alive Script (Prevent Cold Starts)

Prevents container from ever going "cold" by pinging periodically:

```bash
# Create keep-alive script
sudo tee /usr/local/bin/keepalive-wealth-coach.sh > /dev/null << 'EOF'
#!/bin/bash
curl -f -s https://api.wealthwarriorshub.in/health > /dev/null 2>&1
EOF

sudo chmod +x /usr/local/bin/keepalive-wealth-coach.sh

# Add to crontab (ping every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/keepalive-wealth-coach.sh") | crontab -
```

**Benefit:** Container stays warm, no startup delays for users
**Cost:** Minimal resource usage

### Option 2: Preload with Gunicorn

Add `--preload` flag to Gunicorn in docker-compose.yml:

```yaml
command: >
  gunicorn backend.main:app
  --workers 1
  --worker-class uvicorn.workers.UvicornWorker
  --bind 0.0.0.0:8000
  --timeout 120
  --preload  # Add this
```

**Benefit:** Loads application before forking workers
**Note:** May reduce effectiveness of lazy loading

---

## Troubleshooting

### Issue: First RAG Query Still Times Out

**Check:**
```bash
# Verify Nginx timeout is 120s
sudo cat /etc/nginx/sites-available/api.wealthwarriorshub.in | grep proxy_read_timeout

# Should show: proxy_read_timeout 120s;
```

**Fix if needed:**
```bash
sudo nano /etc/nginx/sites-available/api.wealthwarriorshub.in
# Increase timeout to 180s
sudo nginx -t
sudo systemctl reload nginx
```

### Issue: Model Not Loading on First Query

**Check logs:**
```bash
docker compose -f docker-compose.backend.yml logs backend | grep -i "embedding"
```

**Expected:** Should see "Loading embedding model on first use"

**If not appearing:** Model might have loaded during startup (check for errors in lazy loading implementation)

### Issue: Container Unhealthy After Restart

**Check healthcheck status:**
```bash
docker ps
# Look for "health: starting" or "unhealthy"

# View healthcheck logs
docker inspect wealth_coach_backend | grep -A 10 Health
```

**Fix:** Increase healthcheck `start_period` in docker-compose.yml

---

## Performance Monitoring

### Monitor Startup Time

```bash
# Track startup over time
docker compose -f docker-compose.backend.yml restart
START_TIME=$(date +%s)
docker compose -f docker-compose.backend.yml logs backend | grep -q "Server ready" && END_TIME=$(date +%s)
echo "Startup time: $((END_TIME - START_TIME)) seconds"
```

### Monitor First RAG Query

```bash
# Check when model loads
docker compose -f docker-compose.backend.yml logs backend --follow | grep "Loading embedding model"
```

### Monitor Memory Usage

```bash
# Track memory before and after model load
docker stats wealth_coach_backend --no-stream
```

Expected memory usage:
- **After startup (no model):** ~500-700 MB
- **After first RAG query (model loaded):** ~1.2-1.5 GB

---

## Success Criteria

✅ **Startup time:** 10-17 seconds (down from 21-37s)
✅ **Health endpoint:** Responds in <1s after startup
✅ **Auth endpoints:** Work immediately after startup
✅ **First RAG query:** Completes in 10-20s (acceptable)
✅ **Subsequent RAG queries:** <2 seconds
✅ **No 502 errors:** On any endpoint after startup
✅ **Container health:** Green status within 20 seconds

---

## Support Information

**Optimization Type:** Cold Start Performance - Lazy Loading
**Severity:** HIGH IMPACT (60-70% startup time reduction)
**Status:** ✅ Ready for deployment

**Files Modified:**
- `/Users/souravhalder/Downloads/wealthWarriors/backend/services/rag/embeddings.py`
- `/Users/souravhalder/Downloads/wealthWarriors/backend/main.py`
- `/Users/souravhalder/Downloads/wealthWarriors/docker-compose.backend.yml`

**Testing Checklist:**
- [ ] Code deployed to production
- [ ] Container startup time verified (<20s)
- [ ] Health endpoint responsive immediately
- [ ] First RAG query completes successfully
- [ ] Subsequent queries fast (<2s)
- [ ] Nginx logs show no 502 errors
- [ ] Docker healthcheck shows healthy status

---

**Deployed By:** DevOps Engineer
**Date:** November 2, 2025
**Related Document:** COLD_START_502_ISSUE.md

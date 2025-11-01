# Quick Deploy Reference - Cold Start Fix

**ONE-PAGE DEPLOYMENT GUIDE**

---

## TL;DR

**What:** Lazy loading for embedding model (60-70% faster startup)
**Risk:** LOW (pure optimization, easy rollback)
**Downtime:** ~2 minutes during deployment

---

## Deploy in 5 Commands

```bash
# 1. Local: Commit and push
cd /Users/souravhalder/Downloads/wealthWarriors
git add . && git commit -m "optimize: lazy loading (60-70% faster)" && git push

# 2. SSH to server
ssh root@31.97.232.83

# 3. Navigate and pull
cd /root/opt/wealth-coach-ai && git pull origin main

# 4. Run deployment script
chmod +x deploy-cold-start-fix.sh && ./deploy-cold-start-fix.sh

# 5. Done! (Script handles everything else)
```

---

## Quick Test

```bash
# Should respond in <1 second (no 502 error)
curl https://api.wealthwarriorshub.in/health
```

---

## What Changed?

| Before | After |
|--------|-------|
| Startup: 30-40s | Startup: 10-17s |
| First request: 502 error | First request: ✅ works |
| Model loads at startup | Model loads on first RAG query |

---

## Expected Behavior

1. **Container starts** → 10-17 seconds ✅
2. **Health endpoint** → Works immediately ✅
3. **Auth endpoints** → Work immediately ✅
4. **First chat query** → 10-20s delay (ONE TIME) ⏱️
5. **All future queries** → Fast (<2s) 🚀

---

## Quick Verify

```bash
# Check startup time (should be 10-17s)
docker compose -f docker-compose.backend.yml logs backend | grep "Server ready"

# Check health (should return immediately)
curl https://api.wealthwarriorshub.in/health

# Check container status (should be "healthy")
docker ps
```

---

## Rollback (If Needed)

```bash
cd /root/opt/wealth-coach-ai
git log --oneline -5  # Find previous commit
git checkout <commit-hash>
docker compose -f docker-compose.backend.yml down
docker compose -f docker-compose.backend.yml build --no-cache
docker compose -f docker-compose.backend.yml up -d
```

---

## Files Modified

- ✅ `backend/services/rag/embeddings.py` (lazy loading property)
- ✅ `backend/main.py` (removed warmup)
- ✅ `docker-compose.backend.yml` (healthcheck timing)

---

## Success Metrics

- ✅ Startup < 20 seconds
- ✅ Health endpoint < 1 second
- ✅ No 502 errors
- ✅ Container "healthy"

---

## Support

**Full docs:** See `DEPLOYMENT_SUMMARY.md` or `COLD_START_OPTIMIZATION_DEPLOYMENT.md`
**Monitoring:** `docker compose -f docker-compose.backend.yml logs -f backend`

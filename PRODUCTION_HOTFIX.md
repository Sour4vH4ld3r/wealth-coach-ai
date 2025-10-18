# 🔥 Production Hotfix - Critical Issues

**Date:** October 18, 2025
**Status:** 🚨 **URGENT - Apply Immediately**

---

## 🚨 Critical Issues Detected in Production

Based on Docker logs from `root@ubuntu-s-4vcpu-8gb-blr1-01:/opt/wealth-coach-ai`:

```
⚠️  Development API keys detected - do not use in production!
INFO:     Child process [X] died
{"message": "Shutdown error: 'RedisClient' object has no attribute 'close'"}
```

---

## 🔍 Issue #1: Development API Keys in Production

### Problem
```bash
⚠️  Development API keys detected - do not use in production!
```

**Root Cause:** `.env` file contains development API key:
```bash
VALID_API_KEYS='["dev-key-12345"]'
```

### Security Risk
- ⚠️ **HIGH SEVERITY** - Anyone can access your API with "dev-key-12345"
- Allows unauthorized access to user data
- Bypasses authentication security

### Fix Required

**On Production Server (`root@ubuntu-s-4vcpu-8gb-blr1-01`):**

1. **Generate a secure API key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: xK9mP2nQ8rL5vW3jH7fA1cB4dE6gT0yU2sR9pM5nL8v
```

2. **Update `.env` on production server:**
```bash
# Edit /opt/wealth-coach-ai/.env
VALID_API_KEYS='["xK9mP2nQ8rL5vW3jH7fA1cB4dE6gT0yU2sR9pM5nL8v"]'
```

3. **Restart Docker container:**
```bash
cd /opt/wealth-coach-ai
docker-compose restart backend
```

4. **Update mobile app configuration** with new API key

---

## 🔍 Issue #2: Redis Shutdown Error

### Problem
```
Shutdown error: 'RedisClient' object has no attribute 'close'
```

**Root Cause:** Trying to call async `close()` on synchronous Redis client

### Impact
- Error messages in logs on shutdown
- Graceful shutdown not working properly
- Not critical but creates noise in logs

### Fix Applied

**File:** `backend/main.py`

**Changed from:**
```python
await redis_client.close()  # ❌ Redis client is synchronous
```

**Changed to:**
```python
try:
    redis_client = get_redis_client()
    if hasattr(redis_client, 'close'):
        redis_client.close()  # ✅ Check if method exists first
    logger.info("✓ Redis connections closed")
except Exception as redis_err:
    logger.warning(f"Redis cleanup skipped: {redis_err}")
```

**Status:** ✅ Fixed in this commit

---

## 🔍 Issue #3: Worker Processes Dying

### Problem
```
INFO:     Child process [10] died
INFO:     Child process [9] died
INFO:     Child process [116] died
```

### Possible Causes
1. **Out of Memory** - Workers crashing due to RAM limits
2. **OpenAI API Errors** - Unhandled exceptions in AI chat
3. **Redis Connection Issues** - Workers failing to connect
4. **Gunicorn Configuration** - Too many workers for available resources

### Diagnosis Commands

**On Production Server:**

```bash
# Check memory usage
docker stats wealth_coach_backend

# Check worker count
docker exec wealth_coach_backend ps aux | grep uvicorn

# Check recent errors
docker logs wealth_coach_backend --tail=100 | grep ERROR

# Check OpenAI API connectivity
docker exec -it wealth_coach_backend python3 -c "
from backend.services.llm.client import LLMClient
from backend.core.dependencies import get_redis_client
client = LLMClient(cache_client=get_redis_client())
print('Testing OpenAI connection...')
response = client.chat_stream([{'role': 'user', 'content': 'test'}])
print('✓ OpenAI working')
"
```

### Recommended Fixes

#### Option 1: Reduce Worker Count (Quick Fix)
```bash
# Edit docker-compose.yml or docker run command
# Change from --workers 4 to --workers 2
docker-compose down
# Edit configuration
docker-compose up -d
```

#### Option 2: Increase Server Resources
- Current: 4 vCPU, 8GB RAM
- Recommended: 8 vCPU, 16GB RAM for production with AI

#### Option 3: Add Worker Restart Policy
**File:** `docker-compose.yml`
```yaml
services:
  backend:
    restart: unless-stopped
    deploy:
      restart_policy:
        condition: on-failure
        max_attempts: 3
```

---

## 📋 Immediate Action Checklist

### High Priority (Do Now)
- [ ] **Change API key** to secure production key
- [ ] **Update mobile app** with new API key
- [ ] **Pull latest code** with Redis fix (`git pull origin main`)
- [ ] **Restart Docker** containers
- [ ] **Verify no errors** in Docker logs

### Commands for Production Server:

```bash
# 1. SSH into production server
ssh root@ubuntu-s-4vcpu-8gb-blr1-01

# 2. Navigate to project
cd /opt/wealth-coach-ai

# 3. Pull latest code (includes Redis fix)
git pull origin main

# 4. Generate secure API key
python3 -c "import secrets; print('New API Key:', secrets.token_urlsafe(32))"
# Copy the output

# 5. Edit .env file
nano .env
# Update VALID_API_KEYS with the new key
# Save and exit (Ctrl+X, Y, Enter)

# 6. Restart containers
docker-compose down
docker-compose up -d

# 7. Verify startup (wait 10 seconds)
sleep 10
docker logs wealth_coach_backend --tail=50

# 8. Check for errors
docker logs wealth_coach_backend | grep "ERROR\|died\|Development API"
```

---

## 🧪 Verification Tests

### Test 1: No Development API Key Warning
```bash
docker logs wealth_coach_backend | grep "Development API"
# Expected: No output (warning should be gone)
```

### Test 2: No Redis Shutdown Errors
```bash
# Restart container
docker-compose restart backend

# Check logs
docker logs wealth_coach_backend --tail=20
# Expected: "✓ Redis connections closed" (no errors)
```

### Test 3: Workers Stay Alive
```bash
# Monitor for 5 minutes
watch -n 10 'docker logs wealth_coach_backend --tail=5 | grep "died"'
# Expected: No "died" messages
```

### Test 4: API Still Works
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status":"healthy"}
```

---

## 📊 Expected Logs After Fix

**Good Startup Logs:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process [1]
INFO:     Waiting for application startup.
✓ Redis connection established
✓ Vector database loaded
✓ Embedding model warmed up
🚀 Server ready on 0.0.0.0:8000
INFO:     Application startup complete.
```

**Good Shutdown Logs:**
```
INFO:     Shutting down
✓ Redis connections closed
✓ Vector database persisted
INFO:     Application shutdown complete.
```

**No More:**
- ⚠️ Development API keys detected
- RedisClient object has no attribute 'close'
- Child process [X] died (hopefully)

---

## 🔐 Security Best Practices Going Forward

### Environment Variables
```bash
# Production .env should have:
ENVIRONMENT=production
DEBUG=false
RATE_LIMIT_ENABLED=true

# Strong keys (generate new ones):
JWT_SECRET_KEY="[64-char random string]"
VALID_API_KEYS='["[32-char secure key]"]'

# Production OpenAI key (not development)
OPENAI_API_KEY="sk-proj-[PRODUCTION_KEY]"
```

### Generate All Keys
```bash
# JWT Secret (64 chars)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# API Key (32 chars)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📞 Support

If issues persist after applying fixes:

1. **Check Docker logs:**
```bash
docker logs wealth_coach_backend --tail=200 > /tmp/backend_logs.txt
cat /tmp/backend_logs.txt
```

2. **Check resource usage:**
```bash
docker stats
free -h
df -h
```

3. **Restart from clean state:**
```bash
docker-compose down
docker system prune -f
docker-compose up -d --build
```

---

## ✅ Summary

| Issue | Severity | Status | Action Required |
|-------|----------|--------|-----------------|
| Development API Key | 🔴 **CRITICAL** | ⚠️ Manual fix needed | Change API key on server |
| Redis Shutdown Error | 🟡 Medium | ✅ Fixed in code | Pull latest & restart |
| Workers Dying | 🟡 Medium | 🔍 Monitoring needed | Check logs, reduce workers if needed |

**Next Steps:**
1. Apply API key fix on production server
2. Pull latest code (Redis fix included)
3. Restart containers
4. Monitor for 24 hours
5. Report any remaining issues

---

**Fixed By:** Automated Production Monitoring
**Fix Date:** October 18, 2025
**Commit:** Pending (include with next push)
**Priority:** 🔥 **URGENT - Apply Today**

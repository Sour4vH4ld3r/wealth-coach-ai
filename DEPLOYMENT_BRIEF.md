# Wealth Coach AI - Deployment Brief

**Date:** November 1, 2025
**Status:** ⚠️ BLOCKED - Application fails to start due to configuration issue
**Severity:** HIGH - Service unavailable

---

## 🎯 Current Status

### What's Working ✅

1. **Docker Infrastructure**
   - Docker Compose configuration is correct
   - Container builds successfully (7.97GB image)
   - Container shows as "healthy" in Docker status
   - Network and volumes configured properly
   - Healthcheck passes (but misleading - see issue #3)

2. **Environment Setup**
   - PostgreSQL (Supabase) credentials configured
   - Redis (Upstash) credentials configured
   - OpenAI API key configured
   - JWT secrets configured
   - All environment variables inject correctly via docker-compose

3. **Code Structure**
   - Backend application exists at `/app/backend/main.py`
   - All Python dependencies installed in image
   - Dockerfile.prod properly configured with multi-stage build
   - Non-root user (appuser:1000) configured correctly

4. **.dockerignore Configuration**
   - Successfully prevents `.env` files from being baked into image
   - `.env` now mounted as read-only volume at runtime
   - Security best practice implemented

---

## ❌ Critical Issues Preventing Startup

### Issue #1: CORS_ORIGINS JSON Parsing Error

**Error:**
```
pydantic_settings.sources.SettingsError: error parsing value for field "CORS_ORIGINS"
from source "DotEnvSettingsSource"
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Root Cause:**
- The Settings class in `/app/backend/core/config.py` has:
  ```python
  model_config = SettingsConfigDict(
      env_file=".env",
      env_file_encoding="utf-8",
  )
  ```
- Pydantic attempts to read CORS_ORIGINS from the `.env` file
- The value is malformed or has duplicate/empty entries
- JSON parsing fails before the application can start

**Evidence:**
```bash
# Container sees this:
CORS_ORIGINS=["http://localhost:3000"]  # From environment variable

# But .env file likely has:
CORS_ORIGINS=             # Empty or malformed line
CORS_ORIGINS=["..."]      # Duplicate entry
```

**Location:** `/root/opt/wealth-coach-ai/.env` line ~205

---

### Issue #2: Gunicorn Workers Fail to Boot

**Error:**
```
gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>
Worker (pid:XXX) exited with code 3
```

**Root Cause:**
- Workers crash during import of `backend.main:app`
- Caused by Issue #1 - Settings() initialization fails
- No workers start, so no application runs
- Healthcheck passes because it only checks if container is running, not if app is serving

**Evidence:**
```bash
# No gunicorn process running:
$ docker exec backend pgrep gunicorn
# (no output)

# PID 1 is grep (healthcheck), not gunicorn:
$ ls -la /proc/1/exe
lrwxrwxrwx 1 appuser appuser 0 /proc/1/exe -> /usr/bin/grep
```

---

### Issue #3: Misleading Health Status

**Problem:**
- Docker shows container as "healthy"
- Service does not respond on port 8000
- No logs generated

**Root Cause:**
- Healthcheck command: `curl -f http://localhost:8000/health`
- Container's main process exits immediately
- Healthcheck never actually runs against the app
- Docker reports healthy based on container existence, not app availability

**Evidence:**
```bash
$ curl http://localhost:8000/health
curl: (56) Recv failure: Connection reset by peer

$ docker ps
STATUS: Up 2 minutes (healthy)  # MISLEADING!
```

---

## 🔧 Solution Path

### Immediate Fix Required

**Option A: Fix .env File (Recommended)**
```bash
# 1. Remove all CORS_ORIGINS entries
sed -i '/^CORS_ORIGINS=/d' /root/opt/wealth-coach-ai/.env

# 2. Add single clean entry
echo 'CORS_ORIGINS=["*"]' >> /root/opt/wealth-coach-ai/.env

# 3. Verify no duplicates or empty lines
grep -n "CORS" /root/opt/wealth-coach-ai/.env

# 4. Restart
cd /root/opt/wealth-coach-ai
docker compose -f docker-compose.backend.yml restart

# 5. Test
docker compose -f docker-compose.backend.yml exec backend python -c "from backend.main import app; print('SUCCESS')"
```

**Option B: Modify Settings Class**
```python
# In /app/backend/core/config.py, change:
model_config = SettingsConfigDict(
    env_file=None,  # Disable .env file reading
    env_file_encoding="utf-8",
)
```
Then rely solely on environment variables from docker-compose.

---

### Alternative Workaround

**Remove CORS_ORIGINS validator temporarily:**

Edit `/app/backend/core/config.py`:
```python
# Comment out or modify the validator:
@field_validator("CORS_ORIGINS", mode="before")
@classmethod
def parse_cors_origins(cls, v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except:
            return ["*"]  # Fallback to allow all
    return v
```

---

## 📊 Deployment Configuration

### Files Modified During Troubleshooting

1. ✅ **/.dockerignore** - Created to prevent .env from being baked into image
2. ✅ **/docker-compose.backend.yml** - Added `.env` mount as read-only volume
3. ⚠️ **/.env** - Multiple CORS_ORIGINS entries causing conflict
4. 🗑️ **/.env.production** - Removed (had old `CORS_ORIGINS=*` value)

### Current Docker Compose Configuration

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
    volumes:
      - ./.env:/app/.env:ro  # Mounted at runtime
      - ./data/knowledge_base:/app/data/knowledge_base:ro
      - huggingface_cache:/home/appuser/.cache
    env_file:
      - .env  # Also injected as environment variables
```

---

## 🧪 Verification Commands

### Check if Service is Running
```bash
# Container status
docker compose -f docker-compose.backend.yml ps

# Test import
docker compose -f docker-compose.backend.yml exec backend \
  python -c "from backend.main import app; print('SUCCESS')"

# Check health endpoint
curl http://localhost:8000/health

# View logs
docker compose -f docker-compose.backend.yml logs backend
```

### Debug CORS_ORIGINS
```bash
# Check what container sees
docker compose -f docker-compose.backend.yml exec backend \
  cat /app/.env | grep CORS

# Check environment variable
docker compose -f docker-compose.backend.yml exec backend \
  env | grep CORS_ORIGINS
```

---

## 📝 Recommendations

### For Production Deployment

1. **Fix Settings Class:** Modify Pydantic settings to use environment variables only, not .env file
2. **Improve Healthcheck:** Make it actually verify the application responds:
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health", "||", "exit", "1"]
     interval: 30s
     timeout: 10s
     retries: 3
     start_period: 60s
   ```

3. **Add Startup Probe:** Separate from healthcheck to handle long startup times
4. **Implement Proper Logging:** Currently no logs are visible
5. **Remove Duplicate Config:** Either use `env_file` OR environment variables, not both

### Security Notes

- ✅ `.env` files now excluded from Docker image
- ✅ Non-root user configured
- ⚠️ API keys in `.env` - ensure file permissions: `chmod 600 .env`
- ⚠️ CORS currently set to `["*"]` - restrict to actual domains in production

---

## 🔗 Key File Locations

- **Application:** `/root/opt/wealth-coach-ai/`
- **Environment:** `/root/opt/wealth-coach-ai/.env`
- **Docker Compose:** `/root/opt/wealth-coach-ai/docker-compose.backend.yml`
- **Dockerfile:** `/root/opt/wealth-coach-ai/Dockerfile.prod`
- **Settings:** `/app/backend/core/config.py` (inside container)
- **Main App:** `/app/backend/main.py` (inside container)

---

## 📞 Next Steps for Deployment Team

1. **Immediate:** Fix CORS_ORIGINS in `.env` file (remove duplicates/empty lines)
2. **Short-term:** Test with the fix above and verify service starts
3. **Medium-term:** Refactor Settings class to not read `.env` file directly
4. **Long-term:** Implement proper CI/CD with automated testing

---

**Last Updated:** 2025-11-01 11:34 UTC
**Contact:** DevOps Platform Engineer (Alex - infra-devops-platform agent)

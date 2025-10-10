# Upstash Redis Setup Guide - Wealth Warriors

## Why Redis?

Redis is used for:
- ✅ **Caching LLM responses** (save 80-90% on API costs!)
- ✅ **Session management** (user sessions)
- ✅ **Rate limiting** (prevent abuse)
- ✅ **Query caching** (faster responses)

**Redis doesn't need "database creation"** - it's a key-value cache that just works!

---

## Current Status

❌ **Local Redis**: Not installed/running
✅ **Solution**: Use Upstash Redis (cloud, free tier)

---

## Upstash Redis Setup

### 1. Create Upstash Account

1. Go to https://console.upstash.com/
2. Sign up with GitHub/Google or email
3. Verify email (if needed)

### 2. Create Redis Database

1. Click **"Create Database"**
2. Configure:
   - **Name**: `wealth-warriors-redis`
   - **Type**: Regional (faster, free tier)
   - **Region**: Choose closest to you (e.g., Asia-Pacific, US-East, EU)
   - **Primary Region**: Auto-selected
   - **Read Regions**: None (not needed for free tier)
   - **TLS (SSL)**: ✅ Enabled (recommended)
   - **Eviction**: allkeys-lru (recommended)

3. Click **"Create"**

**Free Tier Limits:**
- ✅ 10,000 commands/day
- ✅ 256 MB storage
- ✅ TLS/SSL included
- ✅ No credit card required

### 3. Get Connection String

After database creation:

1. Click on your database name
2. Scroll to **"Connect your database"** section
3. You'll see several connection options

#### Option A: Redis URL (Recommended)

Copy the **UPSTASH_REDIS_REST_URL**:
```
https://redis-xxxxx-xxxxx.upstash.io
```

Or traditional Redis URL:
```
rediss://default:YOUR_PASSWORD@redis-xxxxx.upstash.io:6379
```

**Note:**
- `rediss://` = Secure connection (TLS/SSL) ✅ Recommended
- `redis://` = Insecure connection (not recommended)

#### Option B: REST API (Alternative)

Upstash also provides REST API:
```
https://redis-xxxxx-xxxxx.upstash.io
```

With token:
```
YOUR_UPSTASH_REDIS_REST_TOKEN
```

---

## Update Your .env File

### Option 1: Traditional Redis Connection (Recommended for this project)

Update line 65 in `/Users/souravhalder/Downloads/wealthWarriors/.env`:

```env
# CACHING (Redis) - Upstash Cloud
REDIS_URL="rediss://default:YOUR_PASSWORD@redis-xxxxx.upstash.io:6379"
REDIS_PASSWORD=""  # Already in URL
REDIS_MAX_CONNECTIONS=50
```

**Example:**
```env
REDIS_URL="rediss://default:AYgFAAIjcDE1YzkwNTg4OGU0MjY0NDc0YjllODQ@redis-12345.upstash.io:6379"
```

### Option 2: Environment Variable Method

Or you can use these individual fields:

```env
REDIS_HOST="redis-xxxxx.upstash.io"
REDIS_PORT=6379
REDIS_PASSWORD="YOUR_PASSWORD"
REDIS_USE_TLS=true
```

---

## Test Connection

### Quick Test

```bash
# Test Redis connection
python test_redis.py
```

**Expected Output:**
```
======================================================================
Redis Connection Test
======================================================================

🔗 Redis URL: rediss://default:***@redis-xxxxx.upstash.io:...
📡 Connecting to Redis...
🏓 Testing PING...
✅ PING successful!

💾 Testing SET/GET...
✅ SET/GET successful!
   Stored: Hello from Wealth Warriors!
   Retrieved: Hello from Wealth Warriors!

📊 Redis Info:
   Version: 7.2.0
   Uptime: 1234567 seconds
   Connected clients: 3
   Used memory: 1.2M

======================================================================
✅ Redis is fully configured and working!
======================================================================
```

### Manual Python Test

```bash
source venv/bin/activate
python
```

```python
from backend.core.config import settings
import redis

# Connect
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Test
r.ping()  # Should return True

# Set/Get
r.set("test", "Hello Upstash!")
r.get("test")  # Should return 'Hello Upstash!'

# Clean up
r.delete("test")
```

---

## Verify in Upstash Dashboard

1. Go to https://console.upstash.com/
2. Click on your database
3. Go to **"Data Browser"** tab
4. You should see keys created by your app:
   - `wealth_coach:query:*` (cached queries)
   - `wealth_coach:embedding:*` (cached embeddings)
   - `wealth_coach:session:*` (user sessions)

---

## Update Docker Compose (Optional)

If using Docker, you **don't need local Redis container** anymore:

Comment out the Redis service in `docker-compose.yml`:

```yaml
# =============================================================================
# Redis Cache Service (Comment out when using Upstash)
# =============================================================================
# redis:
#   image: redis:7-alpine
#   container_name: wealth_coach_redis
#   ...
```

Update backend service dependencies:

```yaml
backend:
  ...
  depends_on:
    # - redis  # Remove this when using Upstash
    - chromadb
```

---

## Cache Configuration

Your `.env` cache settings (already configured):

```env
CACHE_ENABLED=true                    # Enable caching
CACHE_TTL=3600                        # Default: 1 hour
QUERY_CACHE_TTL=7200                  # LLM responses: 2 hours
EMBEDDING_CACHE_TTL=86400             # Embeddings: 24 hours
CACHE_HIT_RATE_TARGET=0.9            # Target 90% cache hits
```

**Cost Savings:**
- 90% cache hit rate = 90% savings on OpenAI API calls
- Example: $10/month → $1/month just by caching!

---

## Test Full Stack

### Start Backend (with Upstash Redis)

```bash
./start.sh
```

### Test API with Caching

```bash
# First request (no cache)
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{"message": "What is a 401k?"}'

# Second request (from cache) ⚡
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{"message": "What is a 401k?"}'
```

**Response metadata shows caching:**
```json
{
  "response": "...",
  "cached": true,  ⬅️ Second request is cached!
  "response_time": "0.05s"  ⬅️ Much faster!
}
```

---

## Monitoring Redis Usage

### Check Cache Statistics

```bash
# Via API
curl http://localhost:8000/api/v1/metrics | python -m json.tool
```

### View in Upstash Dashboard

1. Go to https://console.upstash.com/
2. Click on your database
3. View:
   - **Daily Commands** (free tier: 10,000/day)
   - **Storage Used** (free tier: 256 MB)
   - **Throughput** (requests per second)

---

## Comparison: Local vs Upstash Redis

| Feature | Local Redis | Upstash Redis |
|---------|-------------|---------------|
| **Setup** | Install on Mac | No setup |
| **Cost** | Free (local) | Free tier: 10k cmds/day |
| **Persistence** | Manual | Automatic |
| **Backups** | None | Automatic |
| **Access** | Local only | From anywhere |
| **Monitoring** | Manual | Built-in dashboard |
| **Scaling** | Manual | Automatic |
| **SSL/TLS** | Configure yourself | Included |
| **Uptime** | Your Mac | 99.9% SLA |

---

## Troubleshooting

### Issue: Connection Timeout

**Solution:**
```env
# Check TLS setting
REDIS_URL="rediss://..."  # Use 'rediss' with double 's'

# Or try without TLS (not recommended)
REDIS_URL="redis://..."
```

### Issue: Authentication Failed

**Solution:**
```bash
# Verify password in Upstash dashboard
# Copy entire connection string exactly as shown
```

### Issue: Too Many Commands (Free Tier Limit)

**Solution:**
```env
# Increase cache TTL to reduce commands
QUERY_CACHE_TTL=14400  # 4 hours instead of 2
EMBEDDING_CACHE_TTL=172800  # 2 days instead of 1
```

### Issue: "Connection refused"

**Solution:**
```bash
# Make sure using Upstash URL, not localhost
# Check: REDIS_URL="rediss://...@upstash.io:6379"
# Not:   REDIS_URL="redis://localhost:6379"
```

---

## Rate Limits (Free Tier)

**Daily Limits:**
- ✅ 10,000 commands per day
- ✅ 256 MB max storage

**Typical Usage (Wealth Warriors):**
- ~5-10 commands per user request
- 1000 users/day = ~10,000 commands ✅ Perfect fit!

**If you exceed:**
- Upgrade to Pro: $0.20 per 100k commands
- Or implement smarter caching

---

## Next Steps

1. ✅ Create Upstash Redis database
2. ✅ Copy connection string
3. ✅ Update `.env` file (line 65)
4. ✅ Test connection: `python test_redis.py`
5. ✅ Start backend: `./start.sh`
6. ✅ Monitor cache hits in Upstash dashboard

---

## Quick Reference

| Task | Command |
|------|---------|
| Test Redis | `python test_redis.py` |
| View current config | `grep REDIS_URL .env` |
| Start backend | `./start.sh` |
| Check cache stats | `curl localhost:8000/api/v1/metrics` |
| Upstash dashboard | https://console.upstash.com/ |

---

**✅ Upstash Redis = Free, Fast, Reliable caching for your AI assistant!**

**Cost Savings:**
Without caching: $50/month OpenAI costs
With 90% cache hits: $5/month OpenAI costs
**Savings: $45/month** 💰

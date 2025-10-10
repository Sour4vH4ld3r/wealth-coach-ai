# Fix: Redis Read-Only Credential Issue

## Problem

❌ Current credential: `default_ro` (Read-Only)
✅ Need: `default` (Read-Write)

**Error:**
```
redis.exceptions.NoPermissionError: this user has no permissions to run the 'set' command
```

---

## Solution: Get Read-Write Credentials

### Option 1: Use Default Credentials (Recommended)

1. Go to https://console.upstash.com/
2. Click on your database: **deep-condor-11053**
3. Scroll to **"Connect your database"** section
4. Look for connection string WITHOUT `_ro` suffix
5. Copy the one that says **"UPSTASH_REDIS_REST_URL"** or just **"Redis URL"**

**Look for this format:**
```
rediss://default:YOUR_PASSWORD@deep-condor-11053.upstash.io:6379
```

**NOT this (has _ro):**
```
rediss://default_ro:YOUR_PASSWORD@deep-condor-11053.upstash.io:6379
```

---

### Option 2: Create New Read-Write User

1. In Upstash dashboard, go to your database
2. Click **"Data Browser"** tab
3. Go to **"Access Control"** or **"Users"** section
4. Create new user with **Read + Write** permissions
5. Copy the new connection string

---

## Update Your .env File

Replace line 65 in `.env` with the **read-write** credentials:

```env
# OLD (Read-Only - doesn't work)
REDIS_URL="rediss://default_ro:AistAAIgcDLw30pIqWGsHhFIEaBs8MoXeWIxqjLdsQ4fBUaNJ5a73A@deep-condor-11053.upstash.io:6379"

# NEW (Read-Write - works!)
REDIS_URL="rediss://default:YOUR_NEW_PASSWORD@deep-condor-11053.upstash.io:6379"
```

---

## Test Again

After updating `.env`:

```bash
source venv/bin/activate && python test_redis.py
```

**Expected Output:**
```
✅ PING successful!
✅ SET/GET successful!
✅ Redis is fully configured and working!
```

---

## Quick Check

The connection string should:
- ✅ Start with `rediss://` (with double 's' for SSL)
- ✅ Have `default:` (NOT `default_ro:`)
- ✅ End with `@deep-condor-11053.upstash.io:6379`

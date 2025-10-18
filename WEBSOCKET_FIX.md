# 🔧 WebSocket Connection Fix - Production

**Domain:** api.wealthwarriorshub.in
**Issue:** WebSocket connections getting **403 Forbidden**
**Status:** 🔴 **CRITICAL - Fix Required**

---

## 🔍 Diagnosis Results

### ✅ Working Endpoints
```
✅ https://api.wealthwarriorshub.in/               - Status 200
✅ https://api.wealthwarriorshub.in/api/v1/health  - Status 200
✅ https://api.wealthwarriorshub.in/docs           - Status 200
```

### ❌ Broken Endpoint
```
❌ wss://api.wealthwarriorshub.in/ws/chat?token=... - Status 403 Forbidden
```

**Root Cause:** Nginx is blocking WebSocket upgrade requests

---

## 🚨 The Problem

Your Nginx configuration is **missing WebSocket support**. When a client tries to upgrade from HTTP to WebSocket protocol, Nginx returns 403 Forbidden.

**Error:** `Connection failed with status code: 403`

**Why This Happens:**
- Nginx doesn't recognize WebSocket upgrade headers
- Missing `Upgrade` and `Connection` proxy headers
- WebSocket path `/ws/` not configured for protocol upgrade

---

## ✅ The Solution

Update Nginx configuration to support WebSocket connections with proper upgrade headers.

---

## 📋 Fix Instructions for Production Server

### Step 1: SSH into Production Server

```bash
ssh root@ubuntu-s-4vcpu-8gb-blr1-01
cd /opt/wealth-coach-ai
```

### Step 2: Backup Current Nginx Config

```bash
# Find current config
sudo ls -la /etc/nginx/sites-enabled/

# Backup existing config
sudo cp /etc/nginx/sites-enabled/wealth-coach-ai /etc/nginx/sites-enabled/wealth-coach-ai.backup-$(date +%Y%m%d)

# Or if config has different name
sudo cp /etc/nginx/sites-enabled/api.wealthwarriorshub.in /etc/nginx/sites-enabled/api.wealthwarriorshub.in.backup-$(date +%Y%m%d)
```

### Step 3: Update Nginx Configuration

**Option A: Edit Existing Config**

```bash
# Edit the config file
sudo nano /etc/nginx/sites-enabled/wealth-coach-ai
```

**Add/Update WebSocket location block:**

```nginx
# WebSocket configuration - CRITICAL FOR wss://
location /ws/ {
    proxy_pass http://127.0.0.1:8000;

    # WebSocket upgrade headers - REQUIRED
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Standard proxy headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket timeouts
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_connect_timeout 60s;

    # Disable buffering for WebSocket
    proxy_buffering off;

    # Allow longer query strings (for JWT tokens)
    large_client_header_buffers 4 32k;
}
```

**Option B: Use Provided Config**

```bash
# Pull latest code (includes nginx.conf)
cd /opt/wealth-coach-ai
git pull origin main

# Copy new config
sudo cp nginx.conf /etc/nginx/sites-available/wealth-coach-ai

# Create symlink if needed
sudo ln -sf /etc/nginx/sites-available/wealth-coach-ai /etc/nginx/sites-enabled/wealth-coach-ai
```

### Step 4: Test Nginx Configuration

```bash
# Test config syntax
sudo nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 5: Reload Nginx

```bash
# Reload without downtime
sudo systemctl reload nginx

# Or restart if needed
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### Step 6: Verify WebSocket is Working

```bash
# From your local machine, run:
cd /Users/souravhalder/Downloads/wealthWarriors
source venv/bin/activate
python3 scripts/test_production_websocket.py

# Expected output:
# ✅ WebSocket connected successfully!
# ✅ Received complete response
# ✅ WebSocket test PASSED!
```

---

## 🔑 Critical Configuration Details

### Required Headers for WebSocket

```nginx
proxy_http_version 1.1;                          # Use HTTP/1.1
proxy_set_header Upgrade $http_upgrade;          # Forward upgrade header
proxy_set_header Connection "upgrade";           # Set connection to upgrade
```

**Without these 3 lines, WebSocket will NOT work!**

### Why Each Setting Matters

| Setting | Purpose |
|---------|---------|
| `proxy_http_version 1.1` | WebSocket requires HTTP/1.1 (HTTP/2 doesn't support upgrade) |
| `Upgrade $http_upgrade` | Tells backend to upgrade protocol to WebSocket |
| `Connection "upgrade"` | Maintains persistent connection for WebSocket |
| `proxy_read_timeout 86400s` | Keep connection alive for 24 hours |
| `proxy_buffering off` | Disable buffering for real-time streaming |
| `large_client_header_buffers` | Allow long JWT tokens in query string |

---

## 🧪 Testing Checklist

After applying the fix, test these:

### 1. Test WebSocket Connection
```bash
# From local machine
python3 scripts/test_production_websocket.py
```

**Expected:**
```
✅ WebSocket connected successfully!
✅ Received: {"type": "connected", "message": "..."}
✅ WebSocket test PASSED!
```

### 2. Test from Mobile App

**React Native:**
```javascript
const ws = new WebSocket('wss://api.wealthwarriorshub.in/ws/chat?token=' + authToken);

ws.onopen = () => {
  console.log('✅ Connected to production WebSocket');
};

ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error);
};
```

### 3. Check Nginx Logs

```bash
# Watch access logs
sudo tail -f /var/log/nginx/wealth-coach-access.log

# Watch error logs
sudo tail -f /var/log/nginx/wealth-coach-error.log
```

**Good log entry:**
```
GET /ws/chat?token=... HTTP/1.1" 101 - (101 = Switching Protocols ✅)
```

**Bad log entry:**
```
GET /ws/chat?token=... HTTP/1.1" 403 - (403 = Forbidden ❌)
```

---

## 📱 Mobile App Configuration

### Correct WebSocket URL

```javascript
// ✅ CORRECT - Use wss:// for secure WebSocket
const WS_URL = 'wss://api.wealthwarriorshub.in/ws/chat';

// ❌ WRONG - Don't use https:// for WebSocket
const WS_URL = 'https://api.wealthwarriorshub.in/ws/chat'; // This will fail!
```

### React Native Example

```javascript
import { useEffect, useRef, useState } from 'react';

export const useAIChat = (authToken) => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(
        `wss://api.wealthwarriorshub.in/ws/chat?token=${authToken}`
      );

      ws.onopen = () => {
        console.log('✅ Connected to AI chat');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📨 Message:', data);
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('🔌 Disconnected');
        setIsConnected(false);

        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [authToken]);

  return { isConnected, ws: wsRef.current };
};
```

---

## 🔍 Troubleshooting

### Issue 1: Still Getting 403 After Config Update

**Check:**
```bash
# Verify Nginx reloaded
sudo systemctl status nginx

# Check config is active
sudo nginx -T | grep -A 20 "location /ws/"

# Should show the Upgrade headers
```

**Fix:**
```bash
# Hard restart Nginx
sudo systemctl restart nginx
```

### Issue 2: Connection Timeout

**Check:**
```bash
# Verify backend is running
docker ps | grep backend

# Check backend logs
docker logs wealth_coach_backend --tail=50

# Test backend directly (bypass Nginx)
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost:8000/ws/chat?token=test
```

### Issue 3: SSL/TLS Certificate Issues

**Check:**
```bash
# Verify SSL cert is valid
sudo certbot certificates

# Renew if expired
sudo certbot renew

# Reload Nginx
sudo systemctl reload nginx
```

### Issue 4: Token Authentication Failing

**Check:**
```bash
# Generate fresh token
curl -X POST https://api.wealthwarriorshub.in/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"mobile_number": "YOUR_MOBILE", "otp": "YOUR_OTP"}'

# Use the access_token from response
```

---

## 📊 Expected vs Actual Behavior

### Before Fix
```
Request:  wss://api.wealthwarriorshub.in/ws/chat?token=...
Response: HTTP 403 Forbidden ❌
Result:   Connection failed
```

### After Fix
```
Request:  wss://api.wealthwarriorshub.in/ws/chat?token=...
Response: HTTP 101 Switching Protocols ✅
Result:   WebSocket connected successfully!
```

---

## 🔐 Security Considerations

### WebSocket Security Headers

Already included in the nginx.conf:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

### Rate Limiting

Consider adding rate limiting for WebSocket connections:

```nginx
limit_req_zone $binary_remote_addr zone=websocket:10m rate=10r/m;

location /ws/ {
    limit_req zone=websocket burst=5;
    # ... rest of config
}
```

---

## 📝 Quick Reference

### Protocol Usage
- `http://` - Regular HTTP (insecure)
- `https://` - HTTP with TLS/SSL (secure)
- `ws://` - WebSocket (insecure)
- `wss://` - WebSocket with TLS/SSL (secure) ✅ **Use this**

### Port Mapping
- Port 80 → HTTP → Redirects to HTTPS
- Port 443 → HTTPS + WSS (both on same port)

### Connection Flow
```
Mobile App → wss://api.wealthwarriorshub.in/ws/chat
           → Nginx (Port 443, SSL)
           → WebSocket Upgrade Headers
           → Backend (Port 8000)
           → FastAPI WebSocket Handler
           → Connection Established ✅
```

---

## ✅ Verification Commands

Run these to confirm everything works:

```bash
# 1. Nginx config is valid
sudo nginx -t

# 2. Nginx is running
sudo systemctl status nginx

# 3. Backend is running
docker ps | grep backend

# 4. WebSocket test passes
python3 scripts/test_production_websocket.py

# 5. Check for errors
sudo tail -50 /var/log/nginx/wealth-coach-error.log
```

---

## 🎯 Summary

**Problem:** WebSocket connections getting 403 Forbidden

**Root Cause:** Nginx missing WebSocket upgrade headers

**Solution:** Update Nginx config with proper WebSocket support

**Critical Lines:**
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

**Mobile App URL:** `wss://api.wealthwarriorshub.in/ws/chat?token=${token}`

**Test Command:** `python3 scripts/test_production_websocket.py`

---

**Fix Priority:** 🔴 **URGENT - Apply immediately**
**Estimated Time:** 5 minutes
**Downtime:** None (nginx reload is graceful)

---

**Created:** October 18, 2025
**Last Updated:** October 18, 2025

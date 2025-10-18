# 🔧 Fix Nginx Configuration Error

**Error Found:**
```
"large_client_header_buffers" directive is not allowed here in /etc/nginx/sites-enabled/api.wealthwarriorshub.in:68
```

**Problem:** The `large_client_header_buffers` directive was placed inside a `location` block, but it can only be used in `http`, `server`, or `http` contexts.

---

## ✅ Quick Fix on Production Server

You're already SSH'd into the server, so run these commands:

### Step 1: Edit the Config File

```bash
# You're already in /opt/wealth-coach-ai
# Pull the fixed config
git pull origin main

# Edit the Nginx config
sudo nano /etc/nginx/sites-enabled/api.wealthwarriorshub.in
```

### Step 2: Find and Move the Line

**Find line 68** (or search for `large_client_header_buffers`):

Press `Ctrl+W` to search, type `large_client_header_buffers`, press Enter.

**It probably looks like this:**

```nginx
location /ws/ {
    # ... other settings ...

    # Allow longer query strings (for JWT tokens)
    large_client_header_buffers 4 32k;  # ← DELETE THIS LINE FROM HERE
}
```

**Delete that line** from the location block (press `Ctrl+K` to cut the line).

### Step 3: Add It to Server Block

**Scroll up** to find the `server {` block (press `Ctrl+W`, type `server_name api.wealthwarriorshub.in`, press Enter).

**Add the line AFTER the security headers** and BEFORE the location blocks:

```nginx
server {
    server_name api.wealthwarriorshub.in;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Allow longer query strings (for JWT tokens) - ADD THIS LINE HERE
    large_client_header_buffers 4 32k;

    # Logging
    access_log /var/log/nginx/api.wealthwarriorshub.in.access.log;
    error_log /var/log/nginx/api.wealthwarriorshub.in.error.log;

    # WebSocket configuration
    location /ws/ {
        # ... (no large_client_header_buffers here anymore)
    }
}
```

### Step 4: Save and Exit

- Press `Ctrl+X` to exit
- Press `Y` to confirm save
- Press `Enter` to confirm filename

### Step 5: Test the Config

```bash
sudo nginx -t
```

**Expected output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 6: Reload Nginx

```bash
sudo systemctl reload nginx
```

**Expected output:** (no output = success!)

### Step 7: Verify It's Running

```bash
sudo systemctl status nginx
```

**Expected:** `active (running)` in green

---

## 📋 Alternative: Replace Entire Config

If editing is confusing, just replace the whole file:

```bash
# On production server (/opt/wealth-coach-ai)
git pull origin main

# Backup current config
sudo cp /etc/nginx/sites-enabled/api.wealthwarriorshub.in \
  /etc/nginx/sites-enabled/api.wealthwarriorshub.in.backup-broken

# Copy fixed config
sudo cp nginx-fixed.conf /etc/nginx/sites-enabled/api.wealthwarriorshub.in

# Test config
sudo nginx -t

# If test passes, reload
sudo systemctl reload nginx
```

---

## ✅ After Fix - Test WebSocket

From your **local machine** (Mac):

```bash
cd /Users/souravhalder/Downloads/wealthWarriors
source venv/bin/activate
python3 scripts/test_production_websocket.py
```

**Expected:**
```
✅ WebSocket connected successfully!
✅ Received complete response
✅ WebSocket test PASSED!
```

---

## 🔍 Understanding the Error

**Wrong (Inside location block):**
```nginx
location /ws/ {
    large_client_header_buffers 4 32k;  # ❌ NOT ALLOWED HERE
}
```

**Correct (In server block):**
```nginx
server {
    server_name api.wealthwarriorshub.in;
    large_client_header_buffers 4 32k;  # ✅ ALLOWED HERE

    location /ws/ {
        # No large_client_header_buffers here
    }
}
```

The `large_client_header_buffers` directive sets buffer sizes for the entire server, not per-location, so it must be at the server level.

---

## 📝 Summary

1. **Problem:** `large_client_header_buffers` in wrong place (line 68)
2. **Fix:** Move it from `location /ws/` block to `server` block
3. **Test:** `sudo nginx -t`
4. **Apply:** `sudo systemctl reload nginx`
5. **Verify:** Run WebSocket test from local machine

---

**Current Status:** You're at Step 1 (fixing the config file)

**Next:** Edit the file or use the fixed version, then test and reload

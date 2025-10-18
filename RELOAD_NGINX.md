# 🔄 Reload Nginx to Apply WebSocket Fix

**Status:** Config updated ✅, but Nginx not reloaded yet ❌

---

## 🚨 Quick Fix - Run This Now

SSH into your production server:

```bash
ssh root@ubuntu-s-4vcpu-8gb-blr1-01
```

Then run these commands:

```bash
# 1. Test Nginx configuration syntax
sudo nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

If test passes:

```bash
# 2. Reload Nginx (NO DOWNTIME - graceful reload)
sudo systemctl reload nginx

# 3. Check Nginx status
sudo systemctl status nginx

# Expected: "active (running)"
```

**That's it!** WebSocket should work now.

---

## ✅ Verify It's Working

From your **local machine** (Mac), test the connection:

```bash
cd /Users/souravhalder/Downloads/wealthWarriors
source venv/bin/activate
python3 scripts/test_production_websocket.py
```

**Expected output:**
```
✅ WebSocket connected successfully!
✅ Received complete response
✅ WebSocket test PASSED!
```

---

## 🔍 If Still Not Working

### Check 1: Verify Nginx Config Location

On production server:

```bash
# Check which config file Nginx is using
sudo nginx -T | grep "api.wealthwarriorshub.in" -A 10

# Should show your WebSocket configuration
```

### Check 2: Verify WebSocket Block is Present

```bash
# Search for WebSocket config
sudo nginx -T | grep -A 20 "location /ws/"

# Should show:
# location /ws/ {
#     proxy_http_version 1.1;
#     proxy_set_header Upgrade $http_upgrade;
#     proxy_set_header Connection "upgrade";
#     ...
# }
```

### Check 3: Check Nginx Error Logs

```bash
# Watch errors in real-time
sudo tail -f /var/log/nginx/api.wealthwarriorshub.in.error.log

# In another terminal, try connecting from mobile app
# Watch for error messages
```

### Check 4: Test Backend Directly (Bypass Nginx)

```bash
# Check if backend WebSocket works
docker logs wealth_coach_backend --tail=50 | grep -i websocket

# Test backend directly on port 8000
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/ws/chat?token=test

# Should get 101 Switching Protocols (not 403)
```

---

## 📊 Expected vs Actual

### Before Reload
```
Config: ✅ Updated with WebSocket support
Nginx:  ❌ Still using old config (not reloaded)
Result: ❌ 403 Forbidden
```

### After Reload
```
Config: ✅ Updated with WebSocket support
Nginx:  ✅ Reloaded, using new config
Result: ✅ WebSocket connects successfully
```

---

## 🔧 If You Need to Restart (Not Just Reload)

If reload doesn't work, try a full restart:

```bash
# Stop Nginx
sudo systemctl stop nginx

# Start Nginx
sudo systemctl start nginx

# Check status
sudo systemctl status nginx
```

---

## 📝 Quick Reference

| Command | What It Does | Downtime? |
|---------|--------------|-----------|
| `sudo nginx -t` | Test config syntax | No |
| `sudo systemctl reload nginx` | Apply new config | No ✅ |
| `sudo systemctl restart nginx` | Full restart | Yes (~1-2 seconds) |
| `sudo systemctl status nginx` | Check if running | No |

**Use `reload` for zero downtime!**

---

**Next Step:** Run `sudo systemctl reload nginx` on production server

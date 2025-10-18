# 🔧 WebSocket Stability - Fix Disconnections

**Issue:** WebSocket disconnects and reconnects frequently

**Possible Causes:**
1. Rate limiting counting each streaming chunk
2. Nginx timeout settings too short
3. Backend WebSocket heartbeat missing
4. Network instability

---

## 🔍 Diagnosis

Check backend logs on production:

```bash
# On production server
docker logs wealth_coach_backend --tail=100 | grep -i "websocket\|disconnect\|close\|rate"
```

Look for:
- "Rate limit exceeded" messages
- WebSocket close/disconnect messages
- Connection timeout errors

---

## ✅ Fix 1: Exclude WebSockets from Rate Limiting

**On Production Server:**

Edit `/opt/wealth-coach-ai/.env`:

```bash
# Add WebSocket exclusion (if not already present)
WS_RATE_LIMIT_ENABLED=false  # Disable rate limiting for WebSocket

# Or increase WebSocket-specific limits
WS_MAX_MESSAGES_PER_MINUTE=1000  # Much higher for streaming
```

Then restart backend:

```bash
cd /opt/wealth-coach-ai
docker-compose restart backend
```

---

## ✅ Fix 2: Increase Nginx WebSocket Timeouts

**Current Nginx Config has:**
```nginx
proxy_read_timeout 86400s;  # 24 hours
proxy_send_timeout 86400s;  # 24 hours
```

These are already very high! But let's also add keepalive:

**Edit Nginx config:**

```bash
sudo nano /etc/nginx/sites-enabled/api.wealthwarriorshub.in
```

**Find the `/ws/` location block and add:**

```nginx
location /ws/ {
    proxy_pass http://172.28.0.2:8000;

    # WebSocket upgrade headers
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Standard proxy headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket timeouts (already have these)
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_connect_timeout 60s;

    # Disable buffering
    proxy_buffering off;

    # ADD THESE LINES for keepalive:
    proxy_socket_keepalive on;
    keepalive_timeout 86400s;
}
```

Then reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## ✅ Fix 3: Backend WebSocket Heartbeat

Check if backend sends ping/pong frames. In `backend/api/websocket/chat_ws.py`:

The connection manager should have a heartbeat mechanism. If not, the client should send periodic pings.

---

## 🧪 Test Connection Stability

**From your local machine:**

```bash
cd /Users/souravhalder/Downloads/wealthWarriors
source venv/bin/activate

# Run extended stability test (stays connected for 5 minutes)
python3 scripts/test_websocket_stability.py
```

I'll create this test script for you.

---

## 📊 Monitor in Real-Time

**On production server:**

```bash
# Terminal 1 - Watch WebSocket connections
watch -n 2 'docker logs wealth_coach_backend --tail=20 | grep -i websocket'

# Terminal 2 - Watch rate limiting
watch -n 2 'docker logs wealth_coach_backend --tail=20 | grep -i "rate limit"'

# Terminal 3 - Watch for errors
docker logs wealth_coach_backend -f | grep -i "error\|exception"
```

---

## 🔧 Quick Fix Summary

**If it's rate limiting:**
```bash
# On production server
cd /opt/wealth-coach-ai
echo "WS_RATE_LIMIT_ENABLED=false" >> .env
docker-compose restart backend
```

**If it's timeout:**
```bash
# Already have long timeouts in Nginx
# Check backend logs for connection close reasons
docker logs wealth_coach_backend --tail=100
```

**If it's network:**
```bash
# Check if it's stable when testing from production server itself
docker exec -it wealth_coach_backend curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:8000/ws/chat?token=YOUR_TOKEN
```

---

## 🎯 Most Likely Issue

Based on your description (disconnects then reconnects), it's probably:

1. **Rate limiter killing the connection** after 20 messages in a minute
2. **Backend restarting** workers periodically
3. **Network instability** between mobile app and server

**Quick test:** Disable rate limiting and see if it still happens:

```bash
# On production server
cd /opt/wealth-coach-ai
nano .env

# Find RATE_LIMIT_ENABLED and set to false
RATE_LIMIT_ENABLED=false

# Save and restart
docker-compose restart backend
```

Then test if WebSocket stays connected longer.

---

## 📱 Mobile App Best Practices

In your React Native app, implement **auto-reconnect**:

```javascript
const useAIChat = (authToken) => {
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(
        `wss://api.wealthwarriorshub.in/ws/chat?token=${authToken}`
      );

      ws.onclose = () => {
        console.log('WebSocket closed, reconnecting...');

        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connect();
        }, delay);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onopen = () => {
        console.log('WebSocket connected');
        setReconnectAttempts(0); // Reset on successful connection
      };
    };

    connect();
  }, [authToken, reconnectAttempts]);
};
```

This way, even if it disconnects, it will auto-reconnect!

---

**Try disabling rate limiting first and let me know if that fixes it!** 🔧

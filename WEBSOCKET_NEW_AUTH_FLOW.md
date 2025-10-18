# 🔒 New WebSocket Authentication Flow

## What Changed?

The WebSocket connection now uses **message-based authentication** instead of passing tokens in the URL. This is more secure and follows industry best practices.

---

## ✅ Benefits

1. **🔒 Security:** Token not visible in logs, URLs, or network monitoring
2. **⚡ Performance:** User profile loaded ONCE on connection (not per message)
3. **🧠 Conversation Memory:** AI remembers last 10 messages in conversation
4. **💾 Smart Caching:** Cache includes conversation context for better hits

---

## 🔄 New Connection Flow

### Step 1: Connect to WebSocket

```javascript
// Connect WITHOUT token in URL
const ws = new WebSocket('wss://api.wealthwarriorshub.in/ws/chat');
```

### Step 2: Send Authentication Message

```javascript
ws.onopen = () => {
  // Send authentication as first message
  ws.send(JSON.stringify({
    type: "authenticate",
    token: yourAccessToken
  }));
};
```

### Step 3: Wait for Connection Confirmation

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'connected') {
    console.log('✅ Authenticated and ready to chat!');
    // Now you can send messages
  }
};
```

### Step 4: Send Chat Messages

```javascript
// After authentication, send messages normally
ws.send(JSON.stringify({
  type: "message",
  content: "What is compound interest?"
}));
```

---

## 📱 React Native Example (Updated)

```typescript
// useAIChat.ts - Updated for new auth flow

import { useState, useEffect, useRef } from 'react';

export const useAIChat = (authToken: string | null) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!authToken) return;

    // Step 1: Connect WITHOUT token in URL
    const ws = new WebSocket('wss://api.wealthwarriorshub.in/ws/chat');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('📡 WebSocket connected');
      setIsConnected(true);

      // Step 2: Send authentication message
      ws.send(JSON.stringify({
        type: "authenticate",
        token: authToken
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'connected':
          console.log('✅ Authenticated!');
          setIsAuthenticated(true);
          break;

        case 'response':
          // Handle AI response (same as before)
          setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.sender === 'ai' && !lastMsg.done) {
              // Update existing message
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...lastMsg,
                content: data.content,
                done: data.done,
                cached: data.cached  // NEW: Know if response was cached
              };
              return updated;
            } else {
              // New message
              return [...prev, {
                id: Date.now().toString(),
                sender: 'ai',
                content: data.content,
                done: data.done,
                cached: data.cached
              }];
            }
          });
          break;

        case 'error':
          console.error('❌ Error:', data.message);
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      setIsAuthenticated(false);
    };

    ws.onclose = (event) => {
      console.log('Disconnected:', event.code, event.reason);
      setIsConnected(false);
      setIsAuthenticated(false);

      // Reconnect logic (with exponential backoff)
      setTimeout(() => {
        if (authToken) {
          // Reconnect...
        }
      }, 2000);
    };

    return () => {
      ws.close();
    };
  }, [authToken]);

  const sendMessage = (content) => {
    if (!isAuthenticated) {
      console.error('Not authenticated yet');
      return false;
    }

    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      // Add user message to UI
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: 'user',
        content: content
      }]);

      // Send to server
      ws.send(JSON.stringify({
        type: "message",
        content: content
      }));

      return true;
    }
    return false;
  };

  return {
    messages,
    isConnected,
    isAuthenticated,  // NEW: Separate connected and authenticated states
    sendMessage
  };
};
```

---

## 🆚 Before vs After

### ❌ Before (Insecure)

```javascript
// Token in URL
const ws = new WebSocket(
  `wss://api.wealthwarriorshub.in/ws/chat?token=${token}`
);

// User profile loaded on EVERY message
// No conversation history
// No context-aware caching
```

### ✅ After (Secure & Optimized)

```javascript
// 1. Connect without token
const ws = new WebSocket('wss://api.wealthwarriorshub.in/ws/chat');

// 2. Authenticate via message
ws.send(JSON.stringify({ type: "authenticate", token: token }));

// 3. Benefits:
// - Token not in URL/logs ✅
// - User profile cached in memory ✅
// - AI remembers conversation ✅
// - Smart caching with context ✅
```

---

## 🔍 What Happens Behind the Scenes

### On Connection:
1. ✅ WebSocket accepts connection
2. ⏳ Waits for authentication message (30s timeout)
3. 🔐 Verifies JWT token
4. 📊 Loads user profile ONCE from database
5. 💾 Caches profile in memory for this session
6. ✅ Sends "connected" confirmation

### On Each Message:
1. 🧠 Retrieves cached user profile (no DB call!)
2. 📝 Adds message to conversation history (last 10 messages)
3. 🔍 Checks Redis cache with conversation context
4. 🤖 If not cached, calls OpenAI API
5. 📡 Streams response back
6. 💾 Caches response with conversation context

### On Disconnect:
1. 🧹 Cleans up session data
2. 📊 Logs session stats (message count, duration)
3. 🗑️ Removes from memory

---

## 🚨 Error Codes

| Code | Reason | Solution |
|------|--------|----------|
| 1008 | Authentication required | Send auth message after connection |
| 1008 | Token missing | Include token in auth message |
| 1008 | Authentication failed | Check token validity |
| 1008 | Invalid token | Refresh access token |
| 1008 | Authentication timeout | Send auth message within 30s |
| 1008 | Max connections reached | Close other connections |

---

## 🧪 Testing

### Test Script (Python)

```python
import asyncio
import websockets
import json

async def test_new_auth():
    uri = "wss://api.wealthwarriorshub.in/ws/chat"

    async with websockets.connect(uri) as ws:
        print("📡 Connected")

        # Step 1: Authenticate
        await ws.send(json.dumps({
            "type": "authenticate",
            "token": "YOUR_ACCESS_TOKEN"
        }))

        # Step 2: Wait for confirmation
        response = await ws.recv()
        data = json.parse(response)

        if data['type'] == 'connected':
            print("✅ Authenticated!")

            # Step 3: Send message
            await ws.send(json.dumps({
                "type": "message",
                "content": "What is compound interest?"
            }))

            # Step 4: Receive streaming response
            while True:
                response = await ws.recv()
                data = json.loads(response)

                if data['type'] == 'response':
                    print(f"AI: {data['content']}")
                    if data['done']:
                        cached = "💾 (cached)" if data.get('cached') else "🤖 (fresh)"
                        print(f"\n{cached}")
                        break

asyncio.run(test_new_auth())
```

---

## 📊 Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| DB calls per message | 1-2 | 0 | **100%** |
| Token security | ⚠️ Low | ✅ High | **Secure** |
| Conversation memory | ❌ No | ✅ Yes (10 msgs) | **Better UX** |
| Cache effectiveness | 🔶 Basic | ✅ Context-aware | **Smarter** |

---

## 🔐 Security Benefits

1. **No Token in URL:** Token never appears in:
   - Server logs
   - Nginx access logs
   - Browser history
   - Network monitoring tools

2. **Session-based:** Token verified once, connection stays authenticated

3. **Timeout Protection:** 30-second timeout for authentication prevents hanging connections

4. **Automatic Cleanup:** Session data cleared on disconnect

---

## 🚀 Migration Guide

### Step 1: Update Mobile App

Update your `useAIChat.ts` hook to use the new authentication flow (see example above).

### Step 2: Test Locally

Test the new flow with your development server.

### Step 3: Deploy Backend

The backend is already updated. Just restart the server:

```bash
# On production server
cd /opt/wealth-coach-ai
docker-compose restart backend
```

### Step 4: Deploy Mobile App

Release updated mobile app with new WebSocket authentication.

### Step 5: Monitor

Watch for authentication errors in logs:

```bash
docker logs wealth_coach_backend -f | grep -i "auth\|websocket"
```

---

## ✅ Checklist

- [x] Backend updated with new auth flow
- [ ] Mobile app updated with new auth flow
- [ ] Tested locally
- [ ] Deployed to production
- [ ] Users can connect and chat successfully
- [ ] Monitoring shows no authentication errors

---

**🎉 The WebSocket is now more secure, faster, and smarter!**

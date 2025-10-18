# 🔐 WebSocket NEW Authentication Flow - API Integration Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [What Changed](#what-changed)
3. [Integration Steps](#integration-steps)
4. [Code Examples](#code-examples)
5. [Message Format](#message-format)
6. [Error Handling](#error-handling)
7. [Testing](#testing)

---

## Overview

The **NEW WebSocket authentication** uses **message-based authentication** instead of passing the token in the URL. This provides better security and enables advanced features like conversation history and user profile caching.

### Benefits
- 🔒 **Security**: Token not exposed in URL/logs
- ⚡ **Performance**: User profile loaded once and cached
- 🧠 **Memory**: AI remembers last 10 messages in conversation
- 💾 **Caching**: Context-aware response caching (120s TTL)

---

## What Changed

### ❌ OLD Method (Deprecated)
```typescript
// Token in URL - INSECURE
const ws = new WebSocket(`wss://api.wealthwarriorshub.in/ws/chat?token=${authToken}`);

ws.onopen = () => {
  // Immediately ready to send messages
  ws.send(JSON.stringify({ type: "message", content: "Hello" }));
};
```

### ✅ NEW Method (Current)
```typescript
// No token in URL
const ws = new WebSocket('wss://api.wealthwarriorshub.in/ws/chat');

ws.onopen = () => {
  // MUST authenticate first
  ws.send(JSON.stringify({
    type: "authenticate",
    token: authToken
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'connected') {
    // NOW ready to send messages
    ws.send(JSON.stringify({ type: "message", content: "Hello" }));
  }
};
```

---

## Integration Steps

### Step 1: Update WebSocket URL
```typescript
// OLD:
const WS_URL = `wss://api.wealthwarriorshub.in/ws/chat?token=${authToken}`;

// NEW:
const WS_URL = 'wss://api.wealthwarriorshub.in/ws/chat';  // No token!
```

### Step 2: Send Authentication Message
```typescript
wsRef.current.onopen = () => {
  console.log('WebSocket connected - sending authentication...');

  // Send authentication message
  wsRef.current.send(JSON.stringify({
    type: "authenticate",
    token: authToken
  }));
};
```

### Step 3: Wait for Connection Confirmation
```typescript
wsRef.current.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case 'connected':
      console.log('✅ Authenticated:', data.message);
      setIsConnected(true);
      // NOW you can send chat messages
      break;

    case 'response':
      // Handle AI response
      handleAIResponse(data);
      break;

    case 'error':
      console.error('❌ Error:', data.message);
      break;
  }
};
```

### Step 4: Update useAIChat Hook

**File**: `useAIChat.ts` (or `useAIChat.tsx`)

```typescript
import { useState, useEffect, useRef, useCallback } from 'react';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  done?: boolean;
  timestamp: string;
}

export const useAIChat = (authToken: string | null) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!authToken) {
      console.log('No auth token provided');
      return;
    }

    // NEW: No token in URL
    const WS_URL = 'wss://api.wealthwarriorshub.in/ws/chat';

    try {
      wsRef.current = new WebSocket(WS_URL);

      wsRef.current.onopen = () => {
        console.log('✅ WebSocket Connected');
        setIsConnected(true);

        // NEW: Send authentication message
        wsRef.current?.send(JSON.stringify({
          type: 'authenticate',
          token: authToken
        }));
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'connected':
            console.log('✅ Authenticated:', data.message);
            setIsAuthenticated(true);
            break;

          case 'response':
            handleAIResponse(data);
            break;

          case 'error':
            console.error('❌ Error:', data.message);
            break;

          case 'pong':
            console.log('🏓 Pong received');
            break;
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket Error:', error);
        setIsConnected(false);
        setIsAuthenticated(false);
      };

      wsRef.current.onclose = (event) => {
        console.log('🔌 WebSocket Closed:', event.code);
        setIsConnected(false);
        setIsAuthenticated(false);

        // Auto-reconnect after 2 seconds
        setTimeout(() => connect(), 2000);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }, [authToken]);

  const handleAIResponse = (data: any) => {
    setIsTyping(!data.done);

    setMessages((prev) => {
      const lastMessage = prev[prev.length - 1];

      // Update existing AI message or create new one
      if (lastMessage?.sender === 'ai' && !lastMessage.done) {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...lastMessage,
          content: data.content,
          done: data.done,
          timestamp: data.timestamp,
        };
        return updated;
      } else {
        return [...prev, {
          id: Date.now().toString(),
          sender: 'ai',
          content: data.content,
          done: data.done,
          timestamp: data.timestamp,
        }];
      }
    });
  };

  const sendMessage = useCallback((content: string): boolean => {
    // NEW: Check both connected AND authenticated
    if (!isConnected || !isAuthenticated) {
      console.error('❌ Not connected or not authenticated');
      return false;
    }

    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket not ready');
      return false;
    }

    // Add user message to UI
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    // Send to server
    try {
      wsRef.current.send(JSON.stringify({
        type: 'message',
        content: content,
      }));
      return true;
    } catch (error) {
      console.error('❌ Failed to send:', error);
      return false;
    }
  }, [isConnected, isAuthenticated]);

  // Heartbeat
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isAuthenticated]);

  // Connect on mount
  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    messages,
    isConnected,
    isAuthenticated,  // NEW: Expose authentication status
    isTyping,
    sendMessage,
    reconnect: connect,
  };
};
```

---

## Message Format

### Client → Server

#### 1. Authentication Message (First message after connect)
```json
{
  "type": "authenticate",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 2. Chat Message
```json
{
  "type": "message",
  "content": "What is SIP?"
}
```

#### 3. Heartbeat Ping
```json
{
  "type": "ping"
}
```

---

### Server → Client

#### 1. Connection Confirmation
```json
{
  "type": "connected",
  "message": "Connected to Wealth Coach AI",
  "timestamp": "2025-10-19T00:30:00.000Z"
}
```

#### 2. AI Response (Streaming)
```json
{
  "type": "response",
  "content": "SIP stands for Systematic Investment Plan...",
  "done": false,
  "cached": false,
  "timestamp": "2025-10-19T00:30:01.234Z"
}
```

#### 3. AI Response (Final)
```json
{
  "type": "response",
  "content": "SIP stands for Systematic Investment Plan. It is a method of investing...",
  "done": true,
  "cached": false,
  "timestamp": "2025-10-19T00:30:02.567Z"
}
```

#### 4. Cached Response
```json
{
  "type": "response",
  "content": "SIP stands for Systematic Investment Plan...",
  "done": true,
  "cached": true,
  "timestamp": "2025-10-19T00:30:03.890Z"
}
```

#### 5. Error
```json
{
  "type": "error",
  "message": "Failed to generate response. Please try again."
}
```

#### 6. Pong Response
```json
{
  "type": "pong"
}
```

---

## Error Handling

### Common Close Codes

| Code | Meaning | Action |
|------|---------|--------|
| 1000 | Normal closure | No action needed |
| 1006 | Abnormal closure | Auto-reconnect |
| 1008 | Policy violation (auth failed) | Get fresh token and reconnect |
| 1011 | Internal server error | Auto-reconnect after delay |

### Authentication Errors

```typescript
wsRef.current.onclose = (event) => {
  if (event.code === 1008) {
    console.error('❌ Authentication failed');
    // Get fresh token
    await refreshToken();
    // Reconnect with new token
    connect();
  }
};
```

### Timeout Handling

```typescript
// Set timeout for authentication (5 seconds)
const authTimeout = setTimeout(() => {
  if (!isAuthenticated) {
    console.error('❌ Authentication timeout');
    wsRef.current?.close();
  }
}, 5000);

// Clear timeout when authenticated
if (data.type === 'connected') {
  clearTimeout(authTimeout);
  setIsAuthenticated(true);
}
```

---

## Testing

### Test Script

Create a test file: `testWebSocket.ts`

```typescript
const testNewAuth = async () => {
  const token = "YOUR_ACCESS_TOKEN_HERE";
  const ws = new WebSocket('wss://api.wealthwarriorshub.in/ws/chat');

  ws.onopen = () => {
    console.log('✅ Connected - sending auth...');
    ws.send(JSON.stringify({
      type: 'authenticate',
      token: token
    }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📥 Received:', data.type);

    if (data.type === 'connected') {
      console.log('✅ Authenticated!');

      // Test question
      ws.send(JSON.stringify({
        type: 'message',
        content: 'What is SIP?'
      }));
    }

    if (data.type === 'response') {
      console.log('💬 AI:', data.content);
      if (data.done) {
        console.log('✅ Response complete');
        ws.close();
      }
    }
  };

  ws.onerror = (error) => {
    console.error('❌ Error:', error);
  };

  ws.onclose = (event) => {
    console.log('🔌 Closed:', event.code);
  };
};

testNewAuth();
```

### Manual Testing Steps

1. **Get Fresh Token**
   ```bash
   curl -X POST https://api.wealthwarriorshub.in/api/v1/auth/login/mobile \
     -H "Content-Type: application/json" \
     -d '{"mobile_number": "6297369832", "otp": "123456"}'
   ```

2. **Update Token in Test Script**
   - Copy `access_token` from response
   - Update `token` variable in test script

3. **Run Test**
   ```bash
   node testWebSocket.ts
   ```

4. **Expected Output**
   ```
   ✅ Connected - sending auth...
   📥 Received: connected
   ✅ Authenticated!
   📥 Received: response
   💬 AI: SIP stands for Systematic Investment Plan...
   ✅ Response complete
   🔌 Closed: 1000
   ```

---

## Migration Checklist

- [ ] Update WebSocket URL (remove token from URL)
- [ ] Add authentication message on `onopen`
- [ ] Add `isAuthenticated` state
- [ ] Wait for `connected` message before sending chat messages
- [ ] Update error handling for auth failures
- [ ] Test with fresh token
- [ ] Test reconnection logic
- [ ] Test conversation history (ask follow-up questions)
- [ ] Test cached responses (repeat same question)

---

## Production Deployment

### Backend Status
✅ **DEPLOYED** - New authentication is live on production:
- URL: `wss://api.wealthwarriorshub.in/ws/chat`
- All 4 optimization priorities working
- Conversation history enabled (10 messages)
- User profile caching enabled

### Mobile App Update Required
🔴 **PENDING** - Mobile app still using OLD method

**Breaking Change**: OLD authentication will stop working once you deploy the updated mobile app code.

---

## Support

If you encounter issues:

1. **Check Token**: Ensure token is fresh (30 min expiry)
2. **Check Logs**: Look for authentication errors in console
3. **Test Backend**: Use Python test script to verify backend
   ```bash
   python3 scripts/test_production_new_auth.py
   ```

---

## Summary

The NEW WebSocket authentication:
- ✅ More secure (no token in URL)
- ✅ Better performance (profile cached)
- ✅ Conversation memory (10 messages)
- ✅ Smart caching (120s TTL)

Update your mobile app to use the NEW flow and enjoy these benefits! 🚀

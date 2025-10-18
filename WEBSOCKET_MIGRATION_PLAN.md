# 🚧 WebSocket Migration Plan - BREAKING CHANGE

## ⚠️ IMPORTANT

The new WebSocket implementation uses **message-based authentication** instead of URL parameters. This is a **BREAKING CHANGE** that requires coordinated deployment.

---

## 📊 What Changed?

### ❌ Old Method (Currently in Production)
```javascript
// Token in URL
const ws = new WebSocket(`wss://api.wealthwarriorshub.in/ws/chat?token=${token}`);

ws.onopen = () => {
  // Immediately ready to send messages
  ws.send(JSON.stringify({ type: "message", content: "Hello" }));
};
```

### ✅ New Method (Implemented but NOT Deployed)
```javascript
// No token in URL
const ws = new WebSocket('wss://api.wealthwarriorshub.in/ws/chat');

ws.onopen = () => {
  // MUST authenticate first
  ws.send(JSON.stringify({
    type: "authenticate",
    token: token
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

## 🎯 Benefits of New Method

1. **🔒 Security:** Token not in URL/logs
2. **⚡ Performance:** User profile loaded once (not per message)
3. **🧠 Conversation Memory:** AI remembers last 10 messages
4. **💾 Smart Caching:** Context-aware caching

---

## 📋 Migration Options

### Option 1: Big Bang (Risky)
Deploy backend and mobile app simultaneously. If anything goes wrong, users can't chat.

### Option 2: Backward Compatible (Recommended)
Support BOTH methods temporarily, then deprecate old method.

### Option 3: Gradual Rollout
Deploy to staging first, test thoroughly, then production.

---

## ✅ Recommended Approach: Backward Compatible

Update backend to support BOTH authentication methods:

```python
@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket, token: str = None):
    """Support both URL token (old) and message token (new)."""

    await websocket.accept()

    authenticated = False
    user_id = None

    # Try URL token first (backward compatibility)
    if token:
        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
            if user_id:
                authenticated = True
                # Load user profile
                user_profile = await load_user_profile(user_id)
                # Register connection
                await manager.connect(websocket, user_id, user_profile)
                # Send confirmation
                await websocket.send_json({
                    "type": "connected",
                    "message": "Connected (legacy auth)",
                    "deprecated": True  # Warn client
                })
        except:
            pass

    # If not authenticated via URL, wait for auth message (new method)
    if not authenticated:
        try:
            auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            auth_message = json.loads(auth_data)

            if auth_message.get("type") == "authenticate":
                token = auth_message.get("token")
                payload = decode_token(token)
                user_id = payload.get("user_id")

                user_profile = await load_user_profile(user_id)
                await manager.connect(websocket, user_id, user_profile)

                await websocket.send_json({
                    "type": "connected",
                    "message": "Connected to Wealth Coach AI"
                })
                authenticated = True
        except:
            await websocket.close(code=1008, reason="Authentication failed")
            return

    # Rest of the code...
```

---

## 📱 Mobile App Update Strategy

### Phase 1: Update Backend (Backward Compatible)
1. Deploy backend that supports both methods
2. Test with old mobile app - should still work
3. Monitor logs for any issues

### Phase 2: Update Mobile App
1. Update `useAIChat.ts` to use new auth method
2. Test on staging environment
3. Release to beta testers
4. Monitor for connection issues

### Phase 3: Deprecate Old Method
1. Add deprecation warning in response
2. Monitor usage of old method
3. After 90 days (or when usage <1%), remove old method

---

## 🧪 Testing Checklist

### Before Deployment
- [ ] Backend supports both auth methods
- [ ] Old mobile app still works
- [ ] New auth method works
- [ ] Conversation history works
- [ ] Redis caching works
- [ ] Rate limiting works

### After Backend Deployment
- [ ] Old mobile app connects successfully
- [ ] Test with new auth method
- [ ] Monitor error rates
- [ ] Check performance metrics

### After Mobile App Release
- [ ] New app connects successfully
- [ ] Conversation memory working
- [ ] Cached responses working
- [ ] No increase in error rates

---

## 🚀 Deployment Steps

### Step 1: Revert Backend to Backward Compatible
```bash
# Revert chat_ws.py to support both methods
# Test locally
# Deploy to production
```

### Step 2: Update Mobile App
```bash
# Update useAIChat.ts
# Test thoroughly
# Release to app stores
```

### Step 3: Monitor Migration
```bash
# Track usage of old vs new auth
# After 90 days, remove old method
```

---

## ⚠️ Current Status

### Backend
- ✅ New code written with all 4 priorities
- ❌ NOT backward compatible
- ❌ NOT deployed to production

### Mobile App
- ❌ Still using old auth method
- ❌ Not updated yet

### Production
- ✅ Still running old code
- ✅ Working fine

---

## 🎬 What to Do Next?

### Immediate Action Required
1. **DO NOT deploy current backend code** - it will break mobile app
2. **Update backend to support both methods** - backward compatible
3. **Test locally** with both old and new methods
4. **Deploy to staging** first
5. **Update mobile app** after backend is stable
6. **Gradual rollout** to production

---

## 💡 Quick Fix: Revert to Support Both

I can update the backend right now to support both authentication methods. This way:
- ✅ Old mobile app keeps working
- ✅ New auth method ready when mobile app updates
- ✅ Zero downtime migration

**Want me to implement the backward-compatible version?**

---

## 📞 Communication Plan

### To Users
- No communication needed (transparent migration)

### To Team
- "We're upgrading WebSocket security. No action needed from users."
- "Mobile app update coming in X weeks with new features."

---

## 🔍 Monitoring

### Metrics to Watch
- WebSocket connection success rate
- Authentication failure rate
- Old vs new auth method usage
- Chat message latency
- Cache hit rate

### Alerts
- Connection success rate < 95%
- Auth failure rate > 5%
- Average latency > 2 seconds

---

**Status: Waiting for decision on migration approach**

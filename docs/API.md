# Wealth Coach AI Assistant - API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### Health & Monitoring

#### GET `/health`
Quick health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

#### GET `/api/v1/health/detailed`
Detailed health check with dependency status.

**Response**:
```json
{
  "status": "healthy",
  "service": "Wealth Coach AI",
  "version": "1.0.0",
  "environment": "production",
  "dependencies": {
    "redis": {"status": "healthy"},
    "vector_db": {"status": "healthy", "document_count": 150},
    "llm": {"status": "configured", "model": "gpt-3.5-turbo"}
  }
}
```

---

### Authentication

#### POST `/api/v1/auth/register`
Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response** (201):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/api/v1/auth/login`
Authenticate user and get tokens.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/api/v1/auth/refresh`
Refresh access token using refresh token.

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

**Response** (200):
```json
{
  "access_token": "new_access_token_here",
  "refresh_token": "new_refresh_token_here",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/api/v1/auth/logout`
Logout user (invalidates tokens).

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "message": "Successfully logged out"
}
```

---

### Chat

#### POST `/api/v1/chat/message`
Send a message and receive AI-powered financial advice.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "message": "How much should I save for retirement?",
  "conversation_history": [
    {
      "role": "user",
      "content": "I'm 30 years old",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Great! Let's discuss your retirement planning.",
      "timestamp": "2024-01-15T10:00:05Z"
    }
  ],
  "use_rag": true,
  "stream": false
}
```

**Response** (200):
```json
{
  "response": "For retirement at 30, you should aim to save at least 15% of your gross income. Based on the 25x rule, if you want to spend $50,000 per year in retirement, you'll need to save approximately $1.25 million...",
  "sources": [
    {
      "source": "retirement_planning.md",
      "chunk_index": 3,
      "similarity": 0.89
    }
  ],
  "conversation_id": "conv_abc123",
  "timestamp": "2024-01-15T10:00:15Z",
  "cached": false,
  "tokens_used": 245
}
```

#### GET `/api/v1/chat/conversations`
Get user's conversation history.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `limit` (optional): Max conversations to return (default: 10)

**Response** (200):
```json
[
  {
    "conversation_id": "conv_abc123",
    "messages": [...],
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:15:00Z"
  }
]
```

#### GET `/api/v1/chat/conversations/{conversation_id}`
Get specific conversation by ID.

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "conversation_id": "conv_abc123",
  "messages": [
    {
      "role": "user",
      "content": "How do I start investing?",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Great question! Let's start with the basics...",
      "timestamp": "2024-01-15T10:00:05Z"
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:15:00Z"
}
```

#### DELETE `/api/v1/chat/conversations/{conversation_id}`
Delete a conversation.

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "message": "Conversation deleted successfully"
}
```

---

### User Management

#### GET `/api/v1/users/me`
Get current user profile.

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "user_id": "user_123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PATCH `/api/v1/users/me`
Update user profile.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "full_name": "John Smith"
}
```

**Response** (200):
```json
{
  "message": "Profile updated successfully"
}
```

#### DELETE `/api/v1/users/me`
Delete user account (GDPR compliant).

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "message": "Account deletion initiated"
}
```

---

### WebSocket

#### WS `/ws/chat?token=<jwt_token>`
Real-time chat with streaming responses.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat?token=YOUR_JWT_TOKEN');

ws.onopen = () => {
  console.log('Connected to Wealth Coach AI');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message from server:', data);
};
```

**Client → Server Message**:
```json
{
  "type": "message",
  "content": "How do I create a budget?",
  "conversation_id": "conv_abc123"
}
```

**Server → Client Streaming Response**:
```json
{
  "type": "response",
  "content": "To create a budget, start with...",
  "done": false,
  "timestamp": "2024-01-15T10:00:15Z"
}
```

**Final Message**:
```json
{
  "type": "response",
  "content": "Full response here",
  "done": true,
  "timestamp": "2024-01-15T10:00:20Z"
}
```

**Heartbeat (Client → Server)**:
```json
{
  "type": "ping"
}
```

**Heartbeat Response (Server → Client)**:
```json
{
  "type": "pong"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid input format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded: 20 requests per minute",
  "headers": {
    "Retry-After": "60",
    "X-RateLimit-Limit": "20",
    "X-RateLimit-Remaining": "0"
  }
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "request_id": "req_abc123"
}
```

---

## Rate Limits

| Endpoint Type | Per Minute | Per Hour | Per Day |
|---------------|------------|----------|---------|
| General | 20 | 200 | 1,000 |
| Chat | 10 | 100 | 500 |
| Search | 30 | 300 | 1,500 |

Rate limit headers included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## SDKs and Examples

### Python Example
```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Send chat message
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/api/v1/chat/message",
    headers=headers,
    json={"message": "How do I invest $10,000?", "use_rag": True}
)
print(response.json()["response"])
```

### JavaScript Example
```javascript
const BASE_URL = 'http://localhost:8000';

// Login
const loginResponse = await fetch(`${BASE_URL}/api/v1/auth/login`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// Send chat message
const chatResponse = await fetch(`${BASE_URL}/api/v1/chat/message`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'How do I invest $10,000?',
    use_rag: true
  })
});
const data = await chatResponse.json();
console.log(data.response);
```

---

## Interactive API Documentation

Visit `/docs` for Swagger UI interactive documentation.

Visit `/redoc` for ReDoc alternative documentation.

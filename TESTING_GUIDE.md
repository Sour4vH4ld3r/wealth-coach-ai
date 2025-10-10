# Testing Guide - React Web Interface

## Overview

A beautiful React-based web interface to test all Wealth Coach AI APIs including authentication, chat, and PostgreSQL database integration.

## Quick Start

### 1. Start the Backend API (if not already running)
```bash
# Start PostgreSQL (if not running)
brew services start postgresql@15

# Start the FastAPI backend
source venv/bin/activate
PYTHONPATH=. uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend Testing Interface
```bash
# In a new terminal
python3 serve_frontend.py
```

### 3. Open in Browser
Navigate to: **http://localhost:3001**

## Features

### ✅ Authentication Testing
- **User Registration**
  - Email validation
  - Password strength requirements (8+ chars, 1 uppercase, 1 special)
  - Duplicate email detection
  - Automatic login after registration

- **User Login**
  - Credential verification
  - JWT token generation
  - Token persistence in localStorage

### ✅ Chat Interface Testing
- **AI-Powered Chat**
  - Real-time message sending
  - Conversation history display
  - RAG-enhanced responses with source citations
  - Token usage tracking
  - Cache indicators

### ✅ PostgreSQL Integration
- All user data is persisted to PostgreSQL database
- Real-time database writes
- Session management

## What Gets Tested

1. **POST /api/v1/auth/register**
   - Creates new user account
   - Password hashing with bcrypt
   - Email uniqueness validation
   - Returns JWT access token

2. **POST /api/v1/auth/login**
   - Verifies credentials
   - Returns JWT access token
   - Checks account active status

3. **POST /api/v1/chat/message**
   - Requires authentication (Bearer token)
   - Sends message to AI
   - Retrieves RAG context
   - Returns AI response with metadata

## Testing Workflow

### Step 1: Register a New User
1. Enter your full name
2. Enter a valid email
3. Create a strong password (min 8 chars, 1 uppercase, 1 special)
4. Click "Register"
5. ✅ You'll be automatically logged in

### Step 2: Chat with AI
1. Type a financial question (e.g., "What is a 401k?")
2. Click "Send Message"
3. View the AI response with:
   - Response text
   - Token count
   - Number of sources used
   - Cache status

### Step 3: Test Conversation History
1. Send multiple messages
2. Scroll through conversation history
3. Notice how context is maintained

### Step 4: Test Logout/Login
1. Click "Logout"
2. Use the Login form
3. Enter your credentials
4. Continue chatting

## Verifying Database Integration

Check that data is being saved to PostgreSQL:

```bash
# Terminal 1: View database contents
python check_db.py

# Terminal 2: Query PostgreSQL directly
psql -d wealth_coach -c "SELECT email, full_name, created_at FROM users;"
```

## UI Features

### Design
- Beautiful gradient background
- Responsive cards layout
- Smooth animations
- Real-time status indicators
- Color-coded messages (user vs assistant)

### User Experience
- Instant visual feedback
- Error handling with clear messages
- Loading states
- Persistent login (localStorage)
- Chat history scrolling

## API Endpoints Being Tested

| Endpoint | Method | Requires Auth | Purpose |
|----------|--------|--------------|---------|
| `/api/v1/auth/register` | POST | No | Create new user account |
| `/api/v1/auth/login` | POST | No | Login and get JWT token |
| `/api/v1/chat/message` | POST | Yes | Send message and get AI response |

## Troubleshooting

### Frontend Won't Load
```bash
# Check if frontend server is running
lsof -i:3001

# Restart if needed
python3 serve_frontend.py
```

### Backend API Errors
```bash
# Check if backend is running
lsof -i:8000

# Check backend logs
# Look at the terminal where uvicorn is running
```

### PostgreSQL Connection Errors
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start if needed
brew services start postgresql@15

# Verify database exists
psql -l | grep wealth_coach
```

### CORS Errors
The frontend is configured to work with `http://localhost:8000`. Make sure the backend is running on port 8000.

## Test Scenarios

### Happy Path
1. ✅ Register new user → Success
2. ✅ Logout and login with same credentials → Success
3. ✅ Send chat message → Get AI response
4. ✅ Check database → User persisted

### Error Scenarios
1. ❌ Register with weak password → Error message
2. ❌ Register with duplicate email → Error message
3. ❌ Login with wrong password → Error message
4. ❌ Chat without authentication → 401 error
5. ❌ Send empty chat message → Validation error

## Screenshots Expected

1. **Landing Page** - Registration and Login cards
2. **Logged In** - Chat interface with user email displayed
3. **Chat in Action** - Messages being exchanged
4. **Conversation History** - Full chat thread with metadata

## Next Steps

After successful testing, you can:
1. Run the comprehensive Python test suite: `python comprehensive_test.py`
2. Check database directly: `python check_db.py`
3. View API docs: http://localhost:8000/docs
4. Build a production frontend with proper routing and state management

## Tech Stack

### Frontend
- **React 18** (via CDN)
- **Babel Standalone** (for JSX)
- Pure CSS styling
- localStorage for token persistence

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL 15** - Production database
- **SQLAlchemy** - ORM
- **bcrypt** - Password hashing
- **JWT** - Authentication tokens

## Notes

- This is a **testing/demo interface**, not production-ready
- No build step required (uses CDN for React)
- Token stored in localStorage (not secure for production)
- No routing (single page)
- No state management library

For production, consider:
- Next.js or Create React App
- Secure token storage (httpOnly cookies)
- React Router for navigation
- Redux/Zustand for state management
- TypeScript for type safety

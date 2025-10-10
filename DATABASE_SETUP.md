# Database Setup - PostgreSQL with SQLAlchemy

## Overview

The Wealth Coach AI now has full database persistence using PostgreSQL and SQLAlchemy ORM.

## ✅ What's Been Implemented

### 1. Database Models (`backend/db/models.py`)
- **User Model** - Stores user accounts with email, hashed passwords, and profile data
- **ChatSession Model** - Groups related messages by session
- **ChatMessage Model** - Individual chat messages with metadata
- **UserPreferences Model** - User settings and preferences

### 2. Database Connection (`backend/db/database.py`)
- SQLAlchemy engine and session management
- Connection pooling
- Database initialization functions
- FastAPI dependency injection support

### 3. Authentication with Database
- **Registration** - Creates new users in database
- **Login** - Verifies credentials against database
- **Duplicate Check** - Prevents duplicate email registration
- **Password Security** - Bcrypt hashing with 72-byte truncation support

### 4. Database Initialization Script (`init_db.py`)
```bash
# Create database tables
python init_db.py

# Reset database (WARNING: Deletes all data!)
python init_db.py --reset
```

## Database Location

**PostgreSQL Database**: `wealth_coach` on localhost

**Connection URL**: `postgresql://localhost/wealth_coach`

## How to Use

### Start PostgreSQL (if not running)
```bash
brew services start postgresql@15
```

### Initialize Database (First Time)
```bash
python init_db.py
```

### Start the Server
```bash
python start.sh
# or
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Test Registration
```bash
python test_registration.py
```

### Check Database Contents
```bash
python check_db.py
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    title VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES chat_sessions(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tokens_used INTEGER,
    cost VARCHAR(20),
    sources_count INTEGER DEFAULT 0,
    cached BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### User Preferences Table
```sql
CREATE TABLE user_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) UNIQUE,
    use_rag BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'en',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Switching Back to SQLite (Development)

To use SQLite instead of PostgreSQL for local development, update `.env`:

```env
DATABASE_URL=sqlite:///./data/wealth_coach.db
```

Then reinitialize the database:
```bash
# Initialize tables
python init_db.py
```

## Configuration

Edit `.env` file:

```env
# PostgreSQL (Production - Current)
DATABASE_URL="postgresql://localhost/wealth_coach"

# SQLite (Development - Alternative)
# DATABASE_URL="sqlite:///./data/wealth_coach.db"

DATABASE_ECHO=False  # Set to True to see SQL queries
```

## Features

✅ User registration with email validation
✅ Password hashing with bcrypt (fixed 72-byte issue!)
✅ Duplicate email detection
✅ User login with credential verification
✅ JWT token generation
✅ Account status checking (active/inactive)
✅ UUID primary keys
✅ Automatic timestamps (created_at, updated_at)
✅ Database initialization script
✅ SQLAlchemy ORM integration

## Next Steps (Optional)

1. **Chat History** - Update chat endpoints to save messages to database
2. **User Profiles** - Add profile endpoints to view/update user data
3. **Session Management** - Track user sessions and conversation history
4. **User Preferences** - Allow users to customize settings
5. **Admin Panel** - Create admin interface to manage users

## Testing

All registration and login tests pass:
- ✅ Password "Halder@7908" works correctly
- ✅ User data is persisted to database
- ✅ Login verifies against stored credentials
- ✅ Duplicate registration is prevented
- ✅ User ID stored in JWT tokens

## Database Tools

### View Users
```python
from backend.db.database import SessionLocal
from backend.db.models import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f"{user.email} - {user.full_name}")
db.close()
```

### Delete a User
```python
from backend.db.database import SessionLocal
from backend.db.models import User

db = SessionLocal()
user = db.query(User).filter(User.email == "example@email.com").first()
if user:
    db.delete(user)
    db.commit()
db.close()
```

## Troubleshooting

**Database locked error**: Close all database connections or restart the server

**Table doesn't exist**: Run `python init_db.py` to create tables

**Duplicate entry error**: Email already registered, use a different email

**Connection error**: Check `DATABASE_URL` in config

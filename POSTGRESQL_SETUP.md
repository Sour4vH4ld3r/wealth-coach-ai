# PostgreSQL Setup Guide - Wealth Warriors

## Current Status

✅ PostgreSQL 15 is **ALREADY RUNNING** on your Mac
✅ Service status: Started via Homebrew

## Database Configuration

Your project is configured to use:
- **Database Name**: `wealth_coach`
- **Host**: `localhost`
- **Port**: `5432` (default)
- **Connection URL**: `postgresql://localhost/wealth_coach`

Located in `.env` file (line 83):
```env
DATABASE_URL="postgresql://localhost/wealth_coach"
```

---

## Quick Start Guide

### 1. Access PostgreSQL CLI

Since `psql` is not in your PATH, use the full path:

```bash
# Option 1: Use full path
/opt/homebrew/opt/postgresql@15/bin/psql postgres

# Option 2: Add to PATH (recommended)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
psql postgres
```

### 2. Create the Database

```bash
# Connect to PostgreSQL
/opt/homebrew/opt/postgresql@15/bin/psql postgres

# Inside psql, run:
CREATE DATABASE wealth_coach;

# Verify it was created
\l

# Exit psql
\q
```

### 3. Initialize Database Tables

Run the Python initialization script:

```bash
# Make sure you're in the project root
cd /Users/souravhalder/Downloads/wealthWarriors

# Activate virtual environment (if not already active)
source venv/bin/activate

# Initialize database tables
python init_db.py
```

This creates the following tables:
- `users` - User accounts
- `chat_sessions` - Conversation sessions
- `chat_messages` - Individual messages
- `user_preferences` - User settings

### 4. Verify Database Setup

Check if tables were created:

```bash
# Connect to wealth_coach database
/opt/homebrew/opt/postgresql@15/bin/psql wealth_coach

# List all tables
\dt

# View users table structure
\d users

# Exit
\q
```

---

## Common PostgreSQL Commands

### Connection Commands

```bash
# Connect to default database
/opt/homebrew/opt/postgresql@15/bin/psql postgres

# Connect to wealth_coach database
/opt/homebrew/opt/postgresql@15/bin/psql wealth_coach

# Connect with specific user
/opt/homebrew/opt/postgresql@15/bin/psql -U postgres -d wealth_coach
```

### Database Management

```sql
-- List all databases
\l

-- Connect to a database
\c wealth_coach

-- List all tables
\dt

-- Describe a table
\d users
\d chat_sessions
\d chat_messages

-- View table data
SELECT * FROM users;
SELECT email, full_name, created_at FROM users;

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM chat_messages;

-- Delete all data (keep tables)
TRUNCATE users CASCADE;

-- Drop database (WARNING: deletes everything)
DROP DATABASE wealth_coach;
```

### User Management Queries

```sql
-- View all users
SELECT id, email, full_name, is_active, created_at FROM users;

-- Find user by email
SELECT * FROM users WHERE email = 'test@example.com';

-- Delete a specific user
DELETE FROM users WHERE email = 'test@example.com';

-- Count active users
SELECT COUNT(*) FROM users WHERE is_active = true;
```

### Chat History Queries

```sql
-- View recent chat sessions
SELECT * FROM chat_sessions ORDER BY created_at DESC LIMIT 10;

-- View messages for a session
SELECT role, content, created_at
FROM chat_messages
WHERE session_id = 'your-session-id'
ORDER BY created_at;

-- Count total messages
SELECT COUNT(*) FROM chat_messages;

-- Get message count by user
SELECT u.email, COUNT(cm.id) as message_count
FROM users u
JOIN chat_sessions cs ON u.id = cs.user_id
JOIN chat_messages cm ON cs.id = cm.session_id
GROUP BY u.email
ORDER BY message_count DESC;
```

---

## Service Management

### Check PostgreSQL Status

```bash
# Check if running
brew services list | grep postgresql

# View service info
brew services info postgresql@15
```

### Start/Stop/Restart PostgreSQL

```bash
# Stop PostgreSQL
brew services stop postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Restart PostgreSQL
brew services restart postgresql@15
```

---

## Python Database Operations

### Using the Project's Database Functions

```python
# Check database with provided script
python check_db.py

# Initialize or reset database
python init_db.py

# Reset database (deletes all data)
python init_db.py --reset
```

### Manual Python Access

```python
from backend.db.database import SessionLocal
from backend.db.models import User, ChatSession, ChatMessage

# Create a database session
db = SessionLocal()

# Query all users
users = db.query(User).all()
for user in users:
    print(f"{user.email} - {user.full_name}")

# Find specific user
user = db.query(User).filter(User.email == "test@example.com").first()
if user:
    print(f"Found: {user.full_name}")

# Create new user
new_user = User(
    email="newuser@example.com",
    hashed_password="hashed_password_here",
    full_name="New User"
)
db.add(new_user)
db.commit()

# Close session
db.close()
```

---

## Docker Setup

### Using PostgreSQL with Docker Compose

Your `docker-compose.yml` includes PostgreSQL:

```bash
# Start all services including PostgreSQL
docker-compose up -d

# Start only PostgreSQL
docker-compose up -d postgres

# Check PostgreSQL logs
docker-compose logs -f postgres

# Connect to PostgreSQL in container
docker-compose exec postgres psql -U postgres -d wealth_coach

# Stop services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

---

## Environment Configuration

### .env Database Settings

```env
# PostgreSQL (Production - Currently Active)
DATABASE_URL="postgresql://localhost/wealth_coach"

# For Docker, use:
# DATABASE_URL="postgresql://postgres:postgres@postgres:5432/wealth_coach"

# SQLite (Development Alternative)
# DATABASE_URL="sqlite:///./data/wealth_coach.db"

# Optional pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

---

## Troubleshooting

### Issue: "Database does not exist"

```bash
# Create the database
/opt/homebrew/opt/postgresql@15/bin/psql postgres -c "CREATE DATABASE wealth_coach;"
```

### Issue: "Connection refused"

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start if not running
brew services start postgresql@15

# Check port availability
lsof -i :5432
```

### Issue: "Permission denied"

```bash
# Reset permissions
/opt/homebrew/opt/postgresql@15/bin/psql postgres

# Inside psql:
ALTER DATABASE wealth_coach OWNER TO postgres;
GRANT ALL PRIVILEGES ON DATABASE wealth_coach TO postgres;
```

### Issue: "Table doesn't exist"

```bash
# Initialize database
python init_db.py
```

### Issue: "psql command not found"

```bash
# Add to PATH permanently
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Or use full path
/opt/homebrew/opt/postgresql@15/bin/psql
```

---

## Testing Database Connection

### Quick Connection Test

```bash
# Test Python connection
python -c "
from backend.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print(f'✓ Connected to: {result.scalar()}')
"
```

### API Health Check

```bash
# Start backend
./start.sh

# Check database health
curl http://localhost:8000/api/v1/health/detailed | python -m json.tool
```

---

## Backup & Restore

### Backup Database

```bash
# Backup to SQL file
/opt/homebrew/opt/postgresql@15/bin/pg_dump wealth_coach > backup_$(date +%Y%m%d).sql

# Backup specific tables
/opt/homebrew/opt/postgresql@15/bin/pg_dump -t users -t chat_sessions wealth_coach > users_backup.sql
```

### Restore Database

```bash
# Restore from backup
/opt/homebrew/opt/postgresql@15/bin/psql wealth_coach < backup_20250110.sql

# Restore to new database
/opt/homebrew/opt/postgresql@15/bin/createdb wealth_coach_restored
/opt/homebrew/opt/postgresql@15/bin/psql wealth_coach_restored < backup_20250110.sql
```

---

## Next Steps

1. ✅ Create the database:
   ```bash
   /opt/homebrew/opt/postgresql@15/bin/psql postgres -c "CREATE DATABASE wealth_coach;"
   ```

2. ✅ Initialize tables:
   ```bash
   python init_db.py
   ```

3. ✅ Start the backend:
   ```bash
   ./start.sh
   ```

4. ✅ Test registration:
   ```bash
   python test_registration.py
   ```

5. ✅ Check database contents:
   ```bash
   python check_db.py
   ```

---

## Quick Reference

| Task | Command |
|------|---------|
| Connect to PostgreSQL | `/opt/homebrew/opt/postgresql@15/bin/psql postgres` |
| Connect to wealth_coach DB | `/opt/homebrew/opt/postgresql@15/bin/psql wealth_coach` |
| Create database | `CREATE DATABASE wealth_coach;` |
| Initialize tables | `python init_db.py` |
| Check database | `python check_db.py` |
| View service status | `brew services list \| grep postgresql` |
| Restart PostgreSQL | `brew services restart postgresql@15` |

---

**✅ Your PostgreSQL is ready to use!** Just create the database and initialize the tables.

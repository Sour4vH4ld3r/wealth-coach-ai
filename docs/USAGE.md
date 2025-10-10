# Wealth Coach AI Assistant - Usage Guide

This guide explains how to run and test the Wealth Coach AI Assistant using the provided scripts.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Available Scripts](#available-scripts)
- [Usage Examples](#usage-examples)
- [API Testing](#api-testing)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Option 1: Complete Demo (Recommended)

Run everything automatically - starts server and runs test queries:

```bash
./run_all.sh
```

This script will:
1. ✓ Setup Python environment
2. ✓ Check/start Redis (optional)
3. ✓ Load knowledge base
4. ✓ Start API server in background
5. ✓ Run comprehensive test queries
6. ✓ Keep server running for further testing

### Option 2: Start Server Only

Just start the API server:

```bash
./start.sh
```

The server will start with:
- 🌐 API endpoint: http://localhost:8000
- 📚 Interactive docs: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

Press `Ctrl+C` to stop the server.

---

## 📜 Available Scripts

### 1. `start.sh` - Start API Server

**Purpose**: Comprehensive server startup with all checks

**Features**:
- Checks Python virtual environment
- Installs dependencies if needed
- Checks/starts Redis (optional)
- Validates configuration
- Loads knowledge base
- Starts FastAPI server with hot reload

**Usage**:
```bash
./start.sh
```

**What it checks**:
- ✓ Python 3.11+ installed
- ✓ Virtual environment exists
- ✓ All dependencies installed
- ✓ Redis running (optional)
- ✓ .env configuration present
- ✓ Knowledge base populated

---

### 2. `test_queries.sh` - Test API with Sample Queries

**Purpose**: Run comprehensive API tests with financial questions

**Features**:
- Tests health check endpoints
- Tests authentication flow
- Runs 13+ sample financial queries
- Shows response times and metadata

**Usage**:
```bash
# Make sure server is running first!
./start.sh   # In one terminal

# Then in another terminal:
./test_queries.sh
```

**Query Categories Tested**:
1. Financial Q&A (401k, IRAs, retirement savings)
2. Budgeting & Money Management (budgets, emergency funds)
3. Investment Education (diversification, index funds)
4. Tax Optimization (HSAs, tax-advantaged accounts)

**Sample Output**:
```
Question: What is a 401k?
Testing: Basic retirement account explanation

Answer:
A 401k is an employer-sponsored retirement savings plan...

Sources used: 3
Response time: 1.2s
```

---

### 3. `run_all.sh` - Complete Automated Demo

**Purpose**: One-command complete demonstration

**Features**:
- Fully automated setup and testing
- Starts server in background
- Waits for server readiness
- Runs all test queries
- Keeps server running after tests
- Clean shutdown with Ctrl+C

**Usage**:
```bash
./run_all.sh
```

**Perfect for**:
- First-time setup and testing
- Demonstrating the system
- Quick verification after changes

---

### 4. `query.py` - Interactive Query Tool

**Purpose**: Python-based interactive chat interface

**Features**:
- Interactive chat mode
- Single query mode
- Health check mode
- Colored output
- Session tracking
- Response metadata

**Usage**:

**Interactive Mode** (continuous Q&A):
```bash
python query.py
```

**Single Query Mode**:
```bash
python query.py "What is a Roth IRA?"

# Or using -q flag:
python query.py -q "How much should I save for retirement?"
```

**Health Check**:
```bash
python query.py --health
```

**Custom API Configuration**:
```bash
python query.py --api-url http://production.example.com --api-key your-key
```

---

## 💡 Usage Examples

### Example 1: First Time Setup

```bash
# Clone and navigate to project
cd wealthWarriors

# Run complete demo (does everything)
./run_all.sh
```

### Example 2: Daily Development Workflow

```bash
# Terminal 1: Start server with hot reload
./start.sh

# Terminal 2: Interactive testing
python query.py

# Ask questions:
You: What is compound interest?
You: How do I create a budget?
You: exit
```

### Example 3: Automated Testing

```bash
# Start server in background
./run_all.sh

# Or manually:
./start.sh &
sleep 5  # Wait for startup
./test_queries.sh
```

### Example 4: Quick Single Query

```bash
# Make sure server is running
curl http://localhost:8000/health

# Quick question
python query.py "What is dollar-cost averaging?"
```

---

## 🧪 API Testing

### Using cURL

**Basic Health Check**:
```bash
curl http://localhost:8000/health
```

**Detailed Health Check**:
```bash
curl http://localhost:8000/api/v1/health/detailed | python -m json.tool
```

**Ask a Question**:
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{"message": "What is a 401k?"}'
```

**Register a User**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

### Using Python `requests`

```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "dev-key-12345"
    },
    json={"message": "What is a Roth IRA?"}
)

print(response.json()["response"])
```

### Using Interactive API Docs

1. Start server: `./start.sh`
2. Open browser: http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Fill in parameters
5. Click "Execute"

---

## 🔧 Troubleshooting

### Server Won't Start

**Problem**: Port 8000 already in use

**Solution**:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn backend.main:app --port 8001
```

### Redis Connection Error

**Problem**: `Connection refused` to Redis

**Solution**:
```bash
# Option 1: Install and start Redis
brew install redis
redis-server

# Option 2: Run without Redis (caching disabled)
# The server will work fine without Redis
```

### Module Not Found Error

**Problem**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=.

# Or use the start script which handles this:
./start.sh
```

### OpenAI API Key Issues

**Problem**: `OPENAI_API_KEY` validation error

**Solution**:
```bash
# Add your key to .env file
echo 'OPENAI_API_KEY="sk-your-key-here"' >> .env

# Or enable local fallback
echo 'ENABLE_LOCAL_FALLBACK=true' >> .env
```

### Test Queries Fail

**Problem**: `test_queries.sh` shows connection errors

**Solution**:
```bash
# Make sure server is running first
curl http://localhost:8000/health

# If not running:
./start.sh

# Then in another terminal:
./test_queries.sh
```

### Permission Denied

**Problem**: `Permission denied` when running scripts

**Solution**:
```bash
# Make scripts executable
chmod +x start.sh test_queries.sh run_all.sh query.py
```

---

## 📊 Expected Output Examples

### Successful Server Start

```
╔════════════════════════════════════════════════════════════════╗
║         Wealth Coach AI Assistant - Startup Script            ║
╚════════════════════════════════════════════════════════════════╝

[1/6] Checking Python environment...
✓ Virtual environment activated

[2/6] Checking dependencies...
✓ Dependencies already installed

[3/6] Checking Redis...
✓ Redis is already running

[4/6] Checking configuration...
✓ Configuration loaded

[5/6] Checking knowledge base...
✓ Knowledge base already populated

[6/6] Starting API server...

════════════════════════════════════════════════════════════════
🚀 Starting Wealth Coach AI Assistant API Server
════════════════════════════════════════════════════════════════

  📍 API Server:       http://localhost:8000
  📚 API Docs:         http://localhost:8000/docs
  📖 ReDoc:            http://localhost:8000/redoc
  🔍 Health Check:     http://localhost:8000/health
```

### Successful Query Response

```
Question: What is a 401k?

Answer:
A 401k is an employer-sponsored retirement savings plan that allows
employees to contribute a portion of their salary on a pre-tax basis.
The money grows tax-deferred until withdrawal in retirement...

Sources used: 3
Response time: 1.24s
```

---

## 🎯 Next Steps

1. **Explore the API**: Open http://localhost:8000/docs
2. **Load Custom Knowledge**: Add documents to `data/knowledge_base/`
3. **Test with Mobile App**: Use the API with your React Native app
4. **Deploy to Production**: Follow `docs/DEPLOYMENT.md`
5. **Monitor Performance**: Check `docs/MONITORING.md`

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Complete README**: [README.md](README.md)
- **Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Architecture Overview**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the server logs: `tail -f server.log`
2. Verify environment: `python query.py --health`
3. Review configuration: `cat .env`
4. Check dependencies: `pip list | grep fastapi`

**Need more help?** Check the troubleshooting section in the main README.

# Wealth Coach AI - Quick Reference Card

## 🚀 One-Command Start

```bash
./run_all.sh                    # Complete demo: setup + server + tests
./start.sh                      # Just start the server
python query.py                 # Interactive chat mode
```

## 📝 Common Commands

### Server Management
```bash
# Start server
./start.sh

# Start in background
nohup ./start.sh > server.log 2>&1 &

# Check if running
curl http://localhost:8000/health

# Stop server
Ctrl+C  # or kill $(lsof -ti:8000)
```

### Testing
```bash
# Run all test queries
./test_queries.sh

# Single question (CLI)
python query.py "What is a 401k?"

# Interactive mode
python query.py
```

### Quick API Calls
```bash
# Health check
curl localhost:8000/health

# Ask question
curl -X POST localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{"message": "Your question here"}'

# Register user
curl -X POST localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123!","full_name":"Test User"}'
```

## 📍 Important URLs

- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

## 🔧 Troubleshooting One-Liners

```bash
# Fix: Port already in use
kill -9 $(lsof -ti:8000)

# Fix: Module not found
source venv/bin/activate && export PYTHONPATH=.

# Fix: Missing dependencies
pip install -r requirements.txt

# Fix: Redis not running (optional - will work without it)
redis-server --daemonize yes

# Reload knowledge base
python scripts/load_knowledge.py

# Make scripts executable
chmod +x *.sh *.py
```

## 📦 Project Structure Quick View

```
wealthWarriors/
├── start.sh              # Start API server
├── test_queries.sh       # Run test queries
├── run_all.sh           # Complete demo
├── query.py             # Interactive CLI
├── backend/             # API implementation
│   ├── main.py         # FastAPI app
│   ├── api/            # REST endpoints
│   └── services/       # Business logic
├── data/               # Knowledge base & DBs
├── scripts/            # Utility scripts
└── docs/               # Documentation
```

## 🎯 Sample Questions to Try

```
What is a 401k?
How much should I save for retirement?
What is the difference between a Roth IRA and Traditional IRA?
Should I pay off debt or invest?
What is dollar-cost averaging?
How do I create a monthly budget?
What is the 50/30/20 budget rule?
What is an emergency fund?
What is diversification?
What is compound interest?
```

## 🔐 Default Configuration

- **API Key**: `dev-key-12345` (development only)
- **Port**: `8000`
- **Host**: `0.0.0.0`
- **LLM**: OpenAI GPT-3.5-turbo
- **Embedding**: sentence-transformers/all-MiniLM-L6-v2

## 📊 Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (has defaults)
PORT=8000
DEBUG=true
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_ENABLED=true
```

## 💡 Tips

1. **First time?** Run `./run_all.sh` - it does everything
2. **Development?** Use `./start.sh` for hot reload
3. **Testing API?** Use http://localhost:8000/docs (interactive)
4. **Quick question?** Use `python query.py "question"`
5. **Redis optional** - server works without it (no caching)
6. **View logs** - `tail -f server.log` or check terminal

## 🆘 Quick Help

```bash
python query.py --help          # CLI options
./start.sh                      # See startup checks
curl localhost:8000/docs        # API documentation
```

---

**Full Documentation**: See [USAGE.md](USAGE.md) and [README.md](README.md)

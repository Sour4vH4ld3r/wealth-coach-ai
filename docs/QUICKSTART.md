# Wealth Coach AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for production)
- OpenAI API key (or use local models)

---

## Option 1: Development Setup (Local)

```bash
# 1. Clone and navigate
cd wealthWarriors

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env and add your OpenAI API key
nano .env
# Set: OPENAI_API_KEY=sk-your-key-here

# 4. Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
# Choose option 1 (Development)

# 5. Activate virtual environment
source venv/bin/activate

# 6. Load financial knowledge base
python scripts/load_knowledge.py

# 7. Start the server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 8. Open API docs
# Visit: http://localhost:8000/docs
```

**That's it!** Your Wealth Coach AI is running locally.

---

## Option 2: Production Setup (Docker)

```bash
# 1. Clone and navigate
cd wealthWarriors

# 2. Configure environment
cp .env.example .env
nano .env
# Set: OPENAI_API_KEY=sk-your-key-here
# Set: JWT_SECRET_KEY=$(openssl rand -hex 32)
# Set: ENVIRONMENT=production

# 3. Start all services
docker-compose up -d

# 4. Load knowledge base
docker-compose exec backend python scripts/load_knowledge.py

# 5. Check health
curl http://localhost:8000/health

# 6. View logs
docker-compose logs -f backend
```

---

## Testing the API

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

**Response**: You'll get an `access_token`

### 2. Ask a Question
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "How much should I save for retirement?",
    "use_rag": true
  }'
```

**Response**: AI-powered financial advice with sources!

---

## Key Endpoints

- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Metrics**: `http://localhost:8000/api/v1/metrics`
- **WebSocket Chat**: `ws://localhost:8000/ws/chat?token=YOUR_TOKEN`

---

## Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys, settings) |
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Multi-container setup |
| `Dockerfile` | Backend container image |

---

## Project Structure

```
wealthWarriors/
├── backend/              # FastAPI application
│   ├── api/             # REST API endpoints
│   │   ├── v1/          # API version 1
│   │   └── websocket/   # WebSocket handlers
│   ├── core/            # Configuration & security
│   ├── services/        # Business logic
│   │   ├── rag/        # Retrieval-Augmented Generation
│   │   ├── llm/        # LLM client
│   │   └── cache/      # Redis caching
│   ├── db/             # Vector database
│   ├── middleware/     # Rate limiting, logging
│   └── utils/          # Utilities
├── data/
│   ├── knowledge_base/ # Financial documents
│   ├── vector_store/   # ChromaDB data
│   └── cache/          # Redis snapshots
├── scripts/
│   ├── setup.sh        # Setup automation
│   └── load_knowledge.py  # Knowledge base loader
├── docs/               # Documentation
├── logs/               # Application logs
└── docker-compose.yml  # Container orchestration
```

---

## Common Commands

### Development
```bash
# Activate virtual environment
source venv/bin/activate

# Start dev server with auto-reload
uvicorn backend.main:app --reload

# Run tests
pytest backend/tests/

# Format code
black backend/

# Lint code
ruff check backend/
```

### Docker
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild images
docker-compose build

# Shell into container
docker-compose exec backend bash
```

### Database
```bash
# Reload knowledge base
python scripts/load_knowledge.py --reset

# Check vector DB count
curl http://localhost:8001/api/v1/collections

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

---

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs backend

# Check if ports are in use
lsof -i :8000
lsof -i :6379

# Restart everything
docker-compose down && docker-compose up -d
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Cache not working
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# View cache keys
docker-compose exec redis redis-cli KEYS "*"
```

### Out of memory
```bash
# Check Docker stats
docker stats

# Reduce worker count in docker-compose.yml
# Change: --workers 4 → --workers 2
```

---

## Cost Optimization Tips

1. **Enable caching** (default: enabled)
   ```env
   CACHE_ENABLED=true
   CACHE_HIT_RATE_TARGET=0.9
   ```

2. **Limit token usage**
   ```env
   MAX_TOKENS_PER_REQUEST=500
   MAX_REQUESTS_PER_USER_PER_DAY=100
   ```

3. **Use local models for fallback**
   ```env
   ENABLE_LOCAL_FALLBACK=true
   ```

4. **Monitor costs**
   - Check OpenAI dashboard daily
   - Review `/api/v1/metrics` endpoint
   - Set up billing alerts

---

## Next Steps

1. ✅ **Add more financial content**
   - Place `.md`, `.pdf`, `.txt` files in `data/knowledge_base/`
   - Run: `python scripts/load_knowledge.py`

2. ✅ **Customize prompts**
   - Edit `backend/services/llm/prompts.py`
   - Adjust system prompt in `backend/api/v1/chat.py`

3. ✅ **Build mobile app**
   - API is ready for React Native
   - See `docs/API.md` for endpoints

4. ✅ **Deploy to production**
   - Follow `docs/DEPLOYMENT.md`
   - Configure SSL with Let's Encrypt
   - Set up monitoring

5. ✅ **Scale as needed**
   - Upgrade VPS ($8/month → $16/month for 8GB RAM)
   - Add load balancer for multiple instances
   - Separate Redis/ChromaDB to dedicated servers

---

## Support

- **Documentation**: Check `/docs` directory
- **API Reference**: `http://localhost:8000/docs`
- **Logs**: `docker-compose logs -f`
- **Health Check**: `http://localhost:8000/api/v1/health/detailed`

---

## Security Reminders

⚠️ **Before deploying to production**:
- [ ] Change `JWT_SECRET_KEY` from default
- [ ] Set `DEBUG=false`
- [ ] Use strong passwords
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Configure firewall (UFW)
- [ ] Set up backups
- [ ] Review rate limits
- [ ] Enable monitoring

---

**You're all set!** Start asking financial questions and building wealth. 💰

For detailed guides, see:
- `docs/API.md` - Complete API reference
- `docs/DEPLOYMENT.md` - Production deployment
- `README.md` - Full project documentation

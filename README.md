# Wealth Coach AI Assistant

A production-ready, cost-optimized RAG-based AI assistant for personal finance advice, supporting 1000+ concurrent users on <$20/month infrastructure.

## 🎯 Project Overview

**Wealth Coach** provides intelligent financial guidance through:
- Personalized budgeting advice
- Investment education and portfolio guidance
- Tax optimization strategies
- Retirement planning assistance
- Real-time financial Q&A via chat

## 🏗️ Architecture

### Backend Stack
- **API Framework**: FastAPI (async Python)
- **LLM Integration**: OpenAI GPT-3.5-turbo (cost-optimized) + Llama fallback
- **Vector Database**: ChromaDB (self-hosted, embedded)
- **Cache Layer**: Redis (query caching, session management)
- **Authentication**: JWT with refresh tokens
- **WebSocket**: Real-time chat support

### Infrastructure
- **Deployment**: Single VPS (4GB RAM, 2 vCPU)
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt (free)
- **Monitoring**: Prometheus + Grafana (optional)

### Cost Optimization Strategy
1. **Aggressive Caching**: 90% cache hit rate target
2. **Smart LLM Routing**: Fallback to smaller models for simple queries
3. **Batch Processing**: Group embeddings generation
4. **Connection Pooling**: Reuse HTTP/DB connections
5. **Rate Limiting**: Prevent abuse and control costs

## 📁 Project Structure

```
wealthWarriors/
├── backend/                    # Python FastAPI backend
│   ├── api/
│   │   ├── v1/                # API version 1 routes
│   │   │   ├── chat.py       # Chat endpoints
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── user.py       # User management
│   │   │   └── health.py     # Health checks
│   │   └── websocket/        # WebSocket handlers
│   │       └── chat_ws.py    # Real-time chat
│   ├── core/
│   │   ├── config.py         # Configuration management
│   │   ├── security.py       # Auth & encryption
│   │   └── dependencies.py   # FastAPI dependencies
│   ├── models/
│   │   ├── user.py           # User models
│   │   ├── conversation.py   # Chat history
│   │   └── document.py       # Knowledge base docs
│   ├── services/
│   │   ├── rag/
│   │   │   ├── retriever.py  # Document retrieval
│   │   │   ├── embeddings.py # Vector embeddings
│   │   │   └── reranker.py   # Result reranking
│   │   ├── llm/
│   │   │   ├── client.py     # LLM client wrapper
│   │   │   ├── prompts.py    # Prompt templates
│   │   │   └── router.py     # Model selection logic
│   │   └── cache/
│   │       ├── redis_client.py
│   │       └── cache_strategy.py
│   ├── db/
│   │   ├── vector_db.py      # ChromaDB setup
│   │   └── session.py        # DB session management
│   ├── middleware/
│   │   ├── rate_limiter.py   # Rate limiting
│   │   ├── cors.py           # CORS configuration
│   │   └── logging.py        # Request logging
│   ├── utils/
│   │   ├── logger.py         # Structured logging
│   │   ├── metrics.py        # Performance metrics
│   │   └── validators.py     # Input validation
│   └── tests/                # Unit & integration tests
├── data/
│   ├── knowledge_base/       # Financial documents (MD/PDF)
│   ├── vector_store/         # ChromaDB persistence
│   └── cache/                # Redis RDB snapshots
├── config/
│   ├── nginx.conf            # Nginx reverse proxy
│   ├── redis.conf            # Redis configuration
│   └── prometheus.yml        # Monitoring config
├── scripts/
│   ├── setup.sh              # Initial setup script
│   ├── load_knowledge.py     # Ingest financial docs
│   ├── deploy.sh             # Deployment script
│   └── backup.sh             # Data backup
├── docs/
│   ├── API.md                # API documentation
│   ├── DEPLOYMENT.md         # Deployment guide
│   ├── SECURITY.md           # Security practices
│   └── COST_OPTIMIZATION.md  # Cost saving strategies
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile                # Backend container
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- 4GB+ RAM available
- OpenAI API key (optional, can use local models)

### Installation

1. **Clone and setup environment**:
```bash
git clone <repository-url>
cd wealthWarriors
cp .env.example .env
# Edit .env with your configuration
```

2. **Install dependencies**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Start infrastructure** (Redis, ChromaDB):
```bash
docker-compose up -d redis chromadb
```

4. **Load knowledge base**:
```bash
python scripts/load_knowledge.py
```

5. **Run development server**:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API**:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Production Deployment

```bash
# Build and deploy all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

## 🔑 Configuration

Key environment variables (see `.env.example`):

```env
# LLM Configuration
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
MAX_TOKENS_PER_REQUEST=500
ENABLE_LOCAL_FALLBACK=true

# Vector Database
CHROMA_PERSIST_DIR=./data/vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Cache Configuration
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
CACHE_HIT_RATE_TARGET=0.9

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20
RATE_LIMIT_PER_DAY=500

# Security
JWT_SECRET=<generate-strong-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📊 Cost Breakdown (Monthly)

| Service | Provider | Cost |
|---------|----------|------|
| VPS (4GB RAM) | Hetzner/DO | $5-8 |
| OpenAI API | OpenAI | $5-10 |
| Domain + SSL | Free/Cheap | $0-2 |
| **Total** | | **$10-20** |

### Cost Optimization Features
- **Smart Caching**: Saves 80-90% on repeat queries
- **Token Optimization**: Compressed prompts, max 500 tokens/response
- **Batch Embeddings**: Process documents in bulk
- **Local Models**: Fallback to free models for simple queries
- **Rate Limiting**: Prevent abuse and runaway costs

## 🔒 Security Features

- ✅ JWT authentication with secure token rotation
- ✅ Rate limiting per user and IP
- ✅ Input sanitization and validation
- ✅ Encrypted data at rest (optional)
- ✅ HTTPS enforced in production
- ✅ CORS properly configured
- ✅ No PII stored in logs
- ✅ SQL injection prevention (if using SQL)

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/

# Run with coverage
pytest --cov=backend backend/tests/

# Run specific test suite
pytest backend/tests/test_rag.py
```

## 📈 Monitoring

Built-in endpoints:
- `/health` - Service health check
- `/metrics` - Prometheus metrics
- `/api/v1/stats` - Usage statistics

Optional monitoring stack:
```bash
docker-compose --profile monitoring up -d
# Access Grafana: http://localhost:3000
```

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🆘 Support

- Documentation: [/docs](/docs)
- Issues: GitHub Issues
- Email: support@wealthcoach.ai

---

**Built with ❤️ for financial empowerment**

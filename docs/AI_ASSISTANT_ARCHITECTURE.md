# AI Assistant Architecture Guide

## Overview

This document outlines the key architectural components and design decisions for building the WealthWarriors AI Assistant. Understanding these components is critical for engineers working on AI-powered applications.

---

## 1. The Brain (LLM/AI Model)

### What It Is
The "brain" is the Large Language Model (LLM) that powers intelligent responses. In WealthWarriors, we use OpenAI's GPT models through LangChain.

### Key Concepts

**Model Selection:**
- Use GPT-4 for complex reasoning and financial advice
- Use GPT-3.5-turbo for simpler queries to reduce costs
- Consider model cost, latency, and quality tradeoffs

**Prompt Engineering:**
- System prompts define AI personality and behavior
- Context injection provides relevant information to the model
- Temperature controls response creativity (0.0 = deterministic, 1.0 = creative)

**Token Management:**
- Tokens = input + output text chunks
- Monitor token usage to control API costs
- Implement token counting before API calls
- Set max_tokens limits to prevent runaway costs

**Streaming Responses:**
- Server-Sent Events (SSE) for real-time token streaming
- Improves perceived performance and user experience
- Requires async/await handling on both backend and frontend

### Implementation Notes
```python
# Example: Building system prompt with context
system_prompt = f"""
You are WealthWarriors AI, a financial advisor assistant.

Context: {retrieved_documents}
User Profile: {user_profile}
"""

# Streaming response
for chunk in llm.stream(messages):
    yield f"data: {chunk}\n\n"
```

---

## 2. Cache Layer

### What It Is
Caching stores frequently accessed data in memory for fast retrieval, reducing database queries and API calls.

### When to Cache

**Good Candidates for Caching:**
- RAG document embeddings (expensive to compute)
- Frequently asked questions and their responses
- User session data (active users)
- API responses for identical queries
- Static knowledge base content

**Bad Candidates:**
- Personalized user data that changes frequently
- Real-time financial data
- Authentication tokens (security risk)

### Cache Strategies

**1. Redis for Session Storage:**
```python
# Store user session
redis_client.setex(
    f"session:{session_id}",
    3600,  # 1 hour TTL
    json.dumps(session_data)
)
```

**2. In-Memory Cache for Embeddings:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str):
    return embedding_model.embed(text)
```

**3. Query Result Caching:**
- Cache identical questions and their answers
- Use question embeddings as cache keys
- Implement similarity threshold (e.g., > 0.95 = cache hit)

### Cache Invalidation
- Set appropriate TTL (Time To Live) based on data volatility
- Invalidate cache when source data changes
- Use cache versioning for knowledge base updates

---

## 3. Relational Database (PostgreSQL/SQLite)

### What It Is
The relational database stores structured application data: users, chat sessions, messages, profiles.

### Schema Design for AI Assistants

**Core Tables:**

**1. Users Table:**
- Stores authentication and basic user info
- Links to user_profiles for personalization

**2. User Profiles Table:**
- Financial goals, risk tolerance, income range
- Used to personalize AI responses
- Updated through onboarding flow

**3. Chat Sessions Table:**
- Groups messages into conversations
- Tracks session metadata (created_at, updated_at)
- One user → many sessions

**4. Messages Table:**
- Stores user queries and AI responses
- Links to session_id for history retrieval
- Includes role (user/assistant), content, timestamp

### Key Considerations

**Message Storage:**
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);
```

**Pagination for Chat History:**
- Use LIMIT and OFFSET for infinite scroll
- Load 10-20 messages at a time
- Query: `SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT 10 OFFSET ?`

**Indexes:**
- Index session_id for fast message retrieval
- Index user_id for session queries
- Index timestamp for chronological sorting

---

## 4. Vector Database (Embeddings Storage)

### What It Is
Vector databases store and search high-dimensional embeddings for semantic similarity matching. This powers the RAG (Retrieval-Augmented Generation) system.

### How It Works

**1. Document Embedding:**
```python
# Convert text to vector representation
text = "Emergency funds should cover 3-6 months of expenses"
embedding = embedding_model.embed(text)  # Returns [0.123, -0.456, ...]
```

**2. Similarity Search:**
```python
# Find documents similar to user query
query = "How much should I save for emergencies?"
query_embedding = embedding_model.embed(query)
results = vector_db.similarity_search(query_embedding, k=5)
```

### Vector Database Options

**Chroma (Used in WealthWarriors):**
- Lightweight, embedded vector store
- Easy to use for small to medium datasets
- Persistent storage with automatic indexing

**Other Options:**
- Pinecone: Managed, scalable cloud solution
- Weaviate: Open-source with GraphQL API
- FAISS: Facebook's similarity search library

### RAG Implementation

**Document Chunking:**
- Split large documents into 500-1000 token chunks
- Maintain context overlap between chunks
- Store metadata (source, title, date) with each chunk

**Retrieval Strategy:**
```python
# 1. Embed user query
query_embedding = embed(user_query)

# 2. Find top-k similar documents
relevant_docs = vector_db.similarity_search(
    query_embedding,
    k=5,
    filter={"category": "financial_advice"}
)

# 3. Inject into system prompt
system_prompt = f"""
Context: {relevant_docs}

User Question: {user_query}
"""

# 4. Generate response
response = llm.generate(system_prompt)
```

### Embedding Models

**OpenAI text-embedding-ada-002:**
- 1536 dimensions
- Good quality, moderate cost
- Used in WealthWarriors

**Alternatives:**
- Sentence Transformers (open-source, free)
- Cohere embeddings
- Custom fine-tuned models

---

## 5. System Integration & Data Flow

### Request Flow for AI Query

```
1. User sends message → Frontend (React)
2. Frontend → Backend API (FastAPI)
3. Backend:
   a. Authenticate user (JWT token)
   b. Load user profile from database
   c. Generate query embedding
   d. Search vector database for relevant documents (RAG)
   e. Build system prompt with context
   f. Stream LLM response via SSE
   g. Save user message + AI response to database
4. Backend → Frontend (streamed tokens)
5. Frontend displays response in real-time
```

### Data Persistence Strategy

**Write Path:**
- User message → Database (immediate)
- AI response → Database (after completion)
- Session management → Database + Cache

**Read Path:**
- Recent session → Cache first, DB fallback
- Message history → Database with pagination
- User profile → Cache for active sessions

---

## 6. Cost Optimization

### LLM API Costs
- Cache identical queries
- Use cheaper models for simple tasks
- Implement rate limiting per user
- Monitor token usage with alerts

### Database Costs
- Archive old chat sessions to cold storage
- Implement soft deletes for compliance
- Use read replicas for analytics

### Vector Database Costs
- Deduplicate embeddings before storing
- Use dimensionality reduction if needed
- Prune outdated or unused embeddings

---

## 7. Security & Privacy

### User Data Protection
- Encrypt sensitive financial data at rest
- Use HTTPS for all API communication
- Implement proper authentication (JWT)
- Never log user messages in plain text

### AI Safety
- Content filtering for inappropriate queries
- Rate limiting to prevent abuse
- System prompt injection protection
- User consent for data used in RAG

---

## 8. Monitoring & Observability

### Key Metrics to Track

**Performance:**
- LLM response latency (p50, p95, p99)
- Database query times
- Vector search latency
- Cache hit rate

**Business:**
- Active users
- Messages per session
- User retention
- Feature usage (onboarding completion rate)

**Costs:**
- LLM API costs per user/day
- Token usage trends
- Database storage growth

**Quality:**
- User feedback (thumbs up/down)
- Average conversation length
- Error rates and types

---

## 9. Best Practices for Engineers

### Development
- Test with small, representative datasets first
- Mock LLM responses in unit tests (expensive to call)
- Version control your prompts (treat them as code)
- Log prompt/response pairs for debugging

### Production
- Implement circuit breakers for external APIs
- Graceful degradation when services fail
- Feature flags for rolling out new models
- A/B testing for prompt variations

### Maintenance
- Regular knowledge base updates
- Monitor for prompt drift (model behavior changes)
- User feedback loop for continuous improvement
- Cost alerts and budget tracking

---

## 10. WealthWarriors Architecture Summary

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│  Chat UI    │
└──────┬──────┘
       │ HTTPS/SSE
       ▼
┌─────────────────────────┐
│   Backend API           │
│   (FastAPI)             │
│   - Auth                │
│   - Chat endpoints      │
│   - RAG orchestration   │
└───┬─────────┬──────────┘
    │         │
    ▼         ▼
┌────────┐  ┌──────────────┐
│Database│  │ Vector Store │
│(SQLite)│  │  (Chroma)    │
│        │  │              │
│-Users  │  │-Embeddings   │
│-Msgs   │  │-Docs         │
│-Profile│  │-Metadata     │
└────────┘  └──────────────┘
    │              │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │   LLM API    │
    │  (OpenAI)    │
    │              │
    │- GPT-4       │
    │- Embeddings  │
    └──────────────┘
```

### Component Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| Brain | OpenAI GPT-4 | Generate intelligent responses |
| Cache | Redis/LRU | Fast data retrieval, cost optimization |
| Database | SQLite/PostgreSQL | User data, chat history, sessions |
| Vector DB | Chroma | RAG document retrieval |
| Backend | FastAPI | API orchestration, business logic |
| Frontend | React 19 | User interface, streaming UI |

---

## Conclusion

Building an AI assistant requires orchestrating multiple components:

1. **Brain (LLM)** - Intelligence and language understanding
2. **Cache** - Performance and cost optimization
3. **Database** - Persistent structured data
4. **Vector DB** - Semantic search and RAG
5. **Integration** - Smooth data flow between components

Understanding these architectural layers and their tradeoffs is essential for building scalable, cost-effective, and secure AI applications.

---

**For WealthWarriors Engineers:**
- Refer to `backend/api/v1/chat.py` for RAG implementation
- See `data/knowledge_base/` for document management
- Check `backend/db/models.py` for database schema
- Review `frontend/web/frontend-web/web-test/src/pages/ChatPage.jsx` for streaming UI

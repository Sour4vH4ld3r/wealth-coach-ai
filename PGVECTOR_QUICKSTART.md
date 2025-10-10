# pgvector Quick Start Guide

## 🎯 Goal

Replace ChromaDB (local) with pgvector (Supabase cloud) for vector storage.

---

## ✅ Prerequisites

- Supabase PostgreSQL database (already set up ✅)
- Database connection working (already tested ✅)

---

## 📝 Step-by-Step Migration

### Step 1: Enable pgvector in Supabase (5 minutes)

#### Option A: Via Dashboard (Easiest)

1. Go to https://supabase.com/dashboard
2. Select your project: **qfcnomdgpcpnsibihwvm**
3. Click **"Database"** in left sidebar
4. Click **"Extensions"** tab
5. Search for **"vector"**
6. Click **"Enable"** next to pgvector
7. Wait ~30 seconds

#### Option B: Via SQL

1. In Supabase dashboard, go to **SQL Editor**
2. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Click **"Run"**

---

### Step 2: Create Vector Table (2 minutes)

1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New Query"**
3. Copy and paste entire content of: `setup_pgvector.sql`
4. Click **"Run"**
5. You should see: "pgvector setup complete! ✅"

**What this creates:**
- `documents` table with vector column (384 dimensions)
- Indexes for fast similarity search
- Helper functions for querying

---

### Step 3: Verify Setup (1 minute)

```bash
python check_pgvector_setup.py
```

**Expected output:**
```
✅ pgvector extension is ENABLED
✅ documents table EXISTS
✅ Found 3 indexes
✅ Found 3 functions
✅ pgvector is ready to use!
```

---

### Step 4: Install pgvector Package (1 minute)

```bash
source venv/bin/activate
pip install pgvector
```

Add to `requirements.txt`:
```bash
echo "pgvector==0.2.4" >> requirements.txt
```

---

### Step 5: Update Configuration (Optional)

Add to your `.env` file (for future use):

```env
# Vector Database - pgvector
USE_PGVECTOR=true  # Use pgvector instead of ChromaDB
```

---

## 🧪 Test pgvector

### Quick Test

```bash
source venv/bin/activate
python -c "
from sqlalchemy import create_engine, text
from backend.core.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    # Test vector search function
    result = conn.execute(text('SELECT count_documents()'))
    print(f'Documents in vector store: {result.scalar()}')
print('✅ pgvector is working!')
"
```

---

## 📊 Benefits

| Feature | Before (ChromaDB) | After (pgvector) |
|---------|-------------------|------------------|
| **Storage** | Local files | Supabase cloud |
| **Deployment** | Need ChromaDB service | Already deployed |
| **Backups** | Manual | Automatic |
| **Scaling** | Manual | Automatic |
| **Cost** | Free (local) | Free (Supabase) |
| **Maintenance** | You manage | Supabase manages |

---

## 🚀 Next Steps (Implementation)

After completing the setup:

1. **Create pgvector service code** (backend/services/vector_store/)
2. **Update RAG retriever** to use pgvector
3. **Load knowledge base** into pgvector
4. **Update docker-compose.yml** (remove ChromaDB)
5. **Test end-to-end**

Full implementation guide: See `MIGRATE_TO_PGVECTOR.md`

---

## ❓ Troubleshooting

### "Extension does not exist"
- Make sure you enabled pgvector in Supabase dashboard
- Or run: `CREATE EXTENSION IF NOT EXISTS vector;`

### "Table does not exist"
- Run the setup_pgvector.sql file in Supabase SQL Editor

### "Cannot connect to database"
- Check DATABASE_URL in .env
- Test: `python check_pgvector_setup.py`

---

## 📚 Resources

- **pgvector docs**: https://github.com/pgvector/pgvector
- **Supabase pgvector**: https://supabase.com/docs/guides/database/extensions/pgvector
- **Full migration guide**: `MIGRATE_TO_PGVECTOR.md`

---

**Total Setup Time**: ~10 minutes
**Difficulty**: Easy
**Result**: Fully cloud-based vector database! ☁️

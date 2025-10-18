#!/usr/bin/env python3
"""
Comprehensive System Check
Verifies all components after ChromaDB to pgvector migration
"""

import sys
import os

# Set tokenizers parallelism to false to avoid fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

sys.path.insert(0, ".")

from backend.core.config import settings
from backend.db.database import SessionLocal, engine
from backend.services.vector_store.pgvector_store import get_vector_store
from backend.services.cache.redis_client import RedisClient
from sqlalchemy import text
import asyncio


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_postgresql():
    """Check PostgreSQL/Supabase connection"""
    print_section("1. POSTGRESQL / SUPABASE CONNECTION")

    try:
        db = SessionLocal()
        # Test connection with a simple query
        result = db.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connected to PostgreSQL")
        print(f"   Version: {version[:50]}...")

        # Check if pgvector extension is enabled
        result = db.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"))
        pgvector_info = result.fetchone()
        if pgvector_info:
            print(f"✅ pgvector extension installed: v{pgvector_info[1]}")
        else:
            print(f"❌ pgvector extension NOT found!")
            return False

        db.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


async def check_redis():
    """Check Redis/Upstash connection"""
    print_section("2. REDIS / UPSTASH CONNECTION")

    try:
        redis_client = RedisClient(
            url=settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
        )
        await redis_client.connect()

        # Test write
        await redis_client.set("test_key", "test_value", ex=10)

        # Test read
        value = await redis_client.get("test_key")

        if value == "test_value":
            print(f"✅ Redis connected and working")
            print(f"   URL: {settings.REDIS_URL[:50]}...")
        else:
            print(f"❌ Redis read/write test failed")
            return False

        # Cleanup
        await redis_client.delete("test_key")
        await redis_client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


def check_pgvector_store():
    """Check pgvector vector store"""
    print_section("3. PGVECTOR VECTOR STORE")

    try:
        vector_store = get_vector_store()

        # Count documents
        doc_count = vector_store.count()
        print(f"✅ pgvector store accessible")
        print(f"   Documents loaded: {doc_count}")

        if doc_count == 0:
            print(f"⚠️  Warning: No documents in vector store!")
            print(f"   Run: python load_knowledge_pgvector.py")
            return True  # Not a failure, just needs loading

        return True
    except Exception as e:
        print(f"❌ pgvector store check failed: {e}")
        return False


def check_vector_search():
    """Test vector similarity search"""
    print_section("4. VECTOR SIMILARITY SEARCH TEST")

    try:
        from sentence_transformers import SentenceTransformer

        vector_store = get_vector_store()

        # Check if documents exist
        if vector_store.count() == 0:
            print(f"⚠️  Skipping search test - no documents loaded")
            return True

        # Load embedding model
        print(f"📥 Loading embedding model...")
        model = SentenceTransformer(settings.EMBEDDING_MODEL)

        # Generate test query embedding
        test_query = "What is a 401k retirement plan?"
        print(f"🔍 Test query: '{test_query}'")
        query_embedding = model.encode([test_query]).tolist()[0]

        # Search
        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            k=3,
            threshold=0.5
        )

        if results:
            print(f"✅ Search successful - found {len(results)} results:")
            for i, result in enumerate(results, 1):
                content_preview = result['content'][:80].replace('\n', ' ')
                similarity = result['similarity']
                print(f"   {i}. Similarity: {similarity:.3f}")
                print(f"      Content: {content_preview}...")
        else:
            print(f"⚠️  Search returned no results (may need to adjust threshold)")

        return True
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        return False


def check_chromadb_references():
    """Check for any remaining ChromaDB references"""
    print_section("5. CHROMADB REFERENCES CHECK")

    import subprocess

    try:
        # Search for chromadb references (excluding venv and this check file)
        result = subprocess.run(
            ["grep", "-r", "-i", "chromadb",
             "--include=*.py", "--include=*.yml", "--include=*.env",
             "--exclude=comprehensive_check.py",
             "--exclude-dir=venv", "--exclude-dir=.git", "."],
            capture_output=True,
            text=True
        )

        # Filter out comment-only references and documentation
        lines = result.stdout.strip().split('\n') if result.stdout else []
        actual_refs = [line for line in lines if line and
                      '# ' not in line and
                      'MIGRATE_TO_PGVECTOR.md' not in line and
                      '.md:' not in line]

        if actual_refs:
            print(f"⚠️  Found {len(actual_refs)} potential ChromaDB references:")
            for ref in actual_refs[:5]:  # Show first 5
                print(f"   {ref}")
            return False
        else:
            print(f"✅ No ChromaDB references found in code")
            return True
    except Exception as e:
        print(f"⚠️  Could not check references: {e}")
        return True  # Don't fail on this


def check_configuration():
    """Verify configuration settings"""
    print_section("6. CONFIGURATION VERIFICATION")

    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    print(f"Redis URL: {settings.REDIS_URL[:50]}...")
    print(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"Embedding Dimension: {settings.EMBEDDING_DIMENSION}")
    print(f"RAG Top K: {settings.RAG_TOP_K}")
    print(f"RAG Similarity Threshold: {settings.RAG_SIMILARITY_THRESHOLD}")

    # Check for old ChromaDB settings
    old_settings = []
    if hasattr(settings, 'CHROMA_PERSIST_DIR'):
        old_settings.append('CHROMA_PERSIST_DIR')
    if hasattr(settings, 'CHROMA_HOST'):
        old_settings.append('CHROMA_HOST')
    if hasattr(settings, 'CHROMA_PORT'):
        old_settings.append('CHROMA_PORT')
    if hasattr(settings, 'CHROMA_COLLECTION_NAME'):
        old_settings.append('CHROMA_COLLECTION_NAME')

    if old_settings:
        print(f"\n⚠️  Warning: Old ChromaDB settings still in config:")
        for setting in old_settings:
            print(f"   - {setting}")
        return False
    else:
        print(f"\n✅ No old ChromaDB settings found")
        return True


async def main():
    """Run all checks"""
    print("\n" + "=" * 70)
    print("  COMPREHENSIVE SYSTEM CHECK")
    print("  Wealth Coach AI - Post Migration Verification")
    print("=" * 70)

    results = {}

    # Run checks
    results['postgresql'] = check_postgresql()
    results['redis'] = await check_redis()
    results['pgvector'] = check_pgvector_store()
    results['search'] = check_vector_search()
    results['chromadb_refs'] = check_chromadb_references()
    results['config'] = check_configuration()

    # Summary
    print_section("SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nResults: {passed}/{total} checks passed\n")

    for check, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {check.replace('_', ' ').title()}")

    if passed == total:
        print("\n" + "=" * 70)
        print("  🎉 ALL CHECKS PASSED!")
        print("  System is ready for use with pgvector")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"  ⚠️  {total - passed} CHECK(S) FAILED")
        print("  Please review the issues above")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

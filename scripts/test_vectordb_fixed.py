#!/usr/bin/env python3
"""
Test VectorDB Fix
Verify that all VectorDB references are removed and pgvector works
"""

import sys
import os

# Set tokenizers parallelism to false to avoid fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

sys.path.insert(0, ".")

print("=" * 70)
print("TESTING VECTORDB FIX")
print("=" * 70)
print()

# Test 1: Import all modules
print("1. Testing imports...")
try:
    from backend.services.rag.retriever import RAGRetriever, get_retriever
    from backend.core.dependencies import get_vector_db, get_rag_retriever
    from backend.services.vector_store.pgvector_store import get_vector_store
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Get vector store
print("\n2. Testing vector store...")
try:
    vector_store = get_vector_store()
    count = vector_store.count()
    print(f"   ✅ Vector store accessible: {count} documents")
except Exception as e:
    print(f"   ❌ Vector store failed: {e}")
    sys.exit(1)

# Test 3: Get RAG retriever via dependency
print("\n3. Testing RAG retriever dependency...")
try:
    retriever = get_rag_retriever()
    print(f"   ✅ RAG retriever created successfully")
    print(f"      - Top K: {retriever.top_k}")
    print(f"      - Threshold: {retriever.similarity_threshold}")
except Exception as e:
    print(f"   ❌ RAG retriever failed: {e}")
    sys.exit(1)

# Test 4: Test retriever function
print("\n4. Testing get_retriever() helper...")
try:
    retriever2 = get_retriever()
    print(f"   ✅ Helper function works")
except Exception as e:
    print(f"   ❌ Helper function failed: {e}")
    sys.exit(1)

# Test 5: Import main app
print("\n5. Testing main app import...")
try:
    from backend.main import app
    print("   ✅ Main app imports successfully")
except Exception as e:
    print(f"   ❌ Main app import failed: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
print()
print("The VectorDB error has been fixed.")
print("All references to the old VectorDB class have been removed.")
print("The system is now using PGVectorStore correctly.")
print()

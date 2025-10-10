#!/usr/bin/env python3
"""
Load Knowledge Base into pgvector
Migrates financial knowledge documents to Supabase pgvector
"""

import sys
import os
import glob
from pathlib import Path

# Set tokenizers parallelism to false to avoid fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from sentence_transformers import SentenceTransformer

sys.path.insert(0, ".")

from backend.services.vector_store.pgvector_store import get_vector_store
from backend.core.config import settings


def load_embedding_model():
    """Load the embedding model"""
    print(f"📥 Loading embedding model: {settings.EMBEDDING_MODEL}")
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    print("✅ Model loaded")
    return model


def load_markdown_files(directory: str):
    """Load all markdown files from knowledge base"""
    documents = []
    metadatas = []

    md_files = glob.glob(f"{directory}/**/*.md", recursive=True)

    print(f"📁 Found {len(md_files)} markdown files")

    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into chunks (by paragraphs)
            chunks = content.split('\n\n')
            for i, chunk in enumerate(chunks):
                chunk_text = chunk.strip()
                if chunk_text and len(chunk_text) > 50:  # Skip very small chunks
                    documents.append(chunk_text)
                    metadatas.append({
                        "source": Path(file_path).name,
                        "file_path": str(file_path),
                        "chunk_index": i
                    })
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")

    return documents, metadatas


def generate_embeddings(model, texts, batch_size=32):
    """Generate embeddings for texts"""
    print(f"🔄 Generating embeddings for {len(texts)} text chunks...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    print("✅ Embeddings generated")
    return embeddings.tolist()


def main():
    print("=" * 70)
    print("LOADING KNOWLEDGE BASE INTO PGVECTOR (SUPABASE)")
    print("=" * 70)
    print()

    # Initialize vector store
    vector_store = get_vector_store()

    # Check current document count
    current_count = vector_store.count()
    print(f"📊 Current documents in pgvector: {current_count}")

    if current_count > 0:
        response = input(f"\n⚠️  Delete {current_count} existing documents? (yes/no): ")
        if response.lower() == 'yes':
            print("🗑️  Deleting existing documents...")
            vector_store.delete_all()
            print("✅ Cleared")
        else:
            print("Keeping existing documents")
    print()

    # Load embedding model
    model = load_embedding_model()
    print()

    # Load documents
    kb_path = settings.KNOWLEDGE_BASE_PATH
    print(f"📂 Loading documents from: {kb_path}")
    documents, metadatas = load_markdown_files(kb_path)
    print(f"📄 Loaded {len(documents)} document chunks")
    print()

    if not documents:
        print("❌ No documents found!")
        return

    # Generate embeddings
    embeddings = generate_embeddings(model, documents, batch_size=32)
    print()

    # Add to vector store
    print("💾 Adding documents to pgvector...")
    doc_ids = vector_store.add_documents(
        texts=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print(f"✅ Added {len(doc_ids)} documents")
    print()

    # Verify
    final_count = vector_store.count()
    print(f"📊 Total documents in pgvector: {final_count}")
    print()

    # Test search
    print("🔍 Testing similarity search...")
    test_embedding = model.encode(["What is a 401k?"]).tolist()[0]
    results = vector_store.similarity_search(
        query_embedding=test_embedding,
        k=3,
        threshold=0.5
    )

    if results:
        print(f"✅ Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            content_preview = result['content'][:100].replace('\n', ' ')
            print(f"   {i}. {content_preview}... (similarity: {result['similarity']:.3f})")
    else:
        print("⚠️  No results found (this might be okay if threshold is high)")

    print()
    print("=" * 70)
    print("✅ KNOWLEDGE BASE LOADED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - pgvector is now your vector database")
    print("  - All vectors are stored in Supabase cloud PostgreSQL")
    print("  - RAG queries will use pgvector for semantic search")
    print()


if __name__ == "__main__":
    main()

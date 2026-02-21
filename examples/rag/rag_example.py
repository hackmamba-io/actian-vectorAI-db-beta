#!/usr/bin/env python3
############################################################
#
# Copyright (C) 2025-2026 - Actian Corp.
#
############################################################
"""End-to-End RAG (Retrieval-Augmented Generation) Example.

This example demonstrates how to build a complete RAG application using
Actian VectorAI DB. Perfect for developers new to vector databases who want
to understand how it integrates into a real AI application.

What this example shows:
1. Document loading and text chunking
2. Generating embeddings with a real model (sentence-transformers)
3. Storing document chunks in VectorAI DB
4. Processing user queries
5. Retrieving relevant context
6. Generating answers using the retrieved context

Requirements:
    pip install sentence-transformers openai

Usage:
    # With OpenAI (requires OPENAI_API_KEY env variable)
    python examples/rag/rag_example.py

    # With local LLM (no API key needed)
    python examples/rag/rag_example.py --local

    # Custom server address
    python examples/rag/rag_example.py --server localhost:50051
"""

import sys
import uuid
import os
import argparse
from typing import List, Dict, Any
from cortex import CortexClient, DistanceMetric

# Check dependencies
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ Error: sentence-transformers not installed")
    print("Install with: pip install sentence-transformers")
    sys.exit(1)


# Sample knowledge base - In a real application, you'd load this from files
KNOWLEDGE_BASE = """
# Actian VectorAI DB Overview

Actian VectorAI DB is a high-performance vector database designed for AI applications.
It provides persistent storage, gRPC transport, and supports both sync and async operations.

## Key Features

The database offers several important features including async and sync clients with full
async/await support, persistent storage for production-grade data persistence, and a 
type-safe Filter DSL with a fluent API for payload filtering.

## Getting Started

To get started with Actian VectorAI DB, you need to first pull the Docker image and start
the container. The database runs on port 50051 by default. You can use docker compose up
to start it easily.

## Distance Metrics

Actian VectorAI DB supports three distance metrics: COSINE for cosine similarity which is
recommended for normalized vectors, EUCLIDEAN for L2 distance, and DOT for dot product
similarity calculations.

## Python Client

The Python client provides a simple interface to interact with the database. You can create
collections, insert vectors with payloads, perform similarity search, and use filtered
search with the Filter DSL. The client supports both synchronous and asynchronous operations.

## HNSW Algorithm

The database uses the HNSW (Hierarchical Navigable Small World) algorithm for approximate
nearest neighbor search. You can configure HNSW parameters like hnsw_m for edges per node,
hnsw_ef_construct for build-time neighbors, and hnsw_ef_search for search-time neighbors.

## Use Cases

Vector databases like Actian VectorAI DB are perfect for semantic search, recommendation
systems, document retrieval, question answering systems, and retrieval-augmented generation
applications. They enable AI applications to efficiently find relevant information based
on semantic similarity rather than exact keyword matching.

## Performance Considerations

For best performance, normalize your vectors when using cosine similarity, use batch upsert
for inserting multiple vectors, and tune HNSW parameters based on your accuracy and speed
requirements. The database provides persistent storage with transactional safety.
"""


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks for better context preservation.

    Args:
        text: The text to chunk
        chunk_size: Approximate size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of chunks with metadata
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    full_text = "\n\n".join(paragraphs)

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(full_text):
        end = start + chunk_size

        if end < len(full_text):
            # Try to break at a word boundary
            space_idx = full_text.rfind(' ', start, end)
            if space_idx > start:
                end = space_idx
        else:
            end = len(full_text)

        chunk_text_str = full_text[start:end].strip()
        if chunk_text_str:
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text_str,
                "char_count": len(chunk_text_str),
            })
            chunk_id += 1

        start = end - overlap if end < len(full_text) else len(full_text)

    return chunks


def generate_answer_local(query: str, context: str) -> str:
    """
    Generate an answer using retrieved context (local/mock version).
    In a real application, you'd use a local LLM or API.
    """
    return f"""Based on the retrieved context, here's what I found about your query:

Query: {query}

Relevant Information:
{context}

Note: This is using a simple context retrieval. For full answer generation, 
integrate with an LLM like OpenAI GPT, Anthropic Claude, or a local model."""


def generate_answer_openai(query: str, context: str, api_key: str) -> str:
    """
    Generate an answer using OpenAI's API.
    """
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Be concise and accurate."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer based on the context above:"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
    except ImportError:
        return "❌ OpenAI package not installed. Install with: pip install openai"
    except Exception as e:
        return f"❌ Error calling OpenAI API: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="RAG Example with Actian VectorAI DB")
    parser.add_argument("--server", default="localhost:50051", help="Server address")
    parser.add_argument("--local", action="store_true", help="Use local mode (no LLM API)")
    args = parser.parse_args()
    
    SERVER = args.server
    USE_LOCAL = args.local
    COLLECTION = f"rag_demo_{uuid.uuid4().hex[:8]}"
    
    print("=" * 70)
    print("🚀 End-to-End RAG Example with Actian VectorAI DB")
    print("=" * 70)
    
    # Initialize embedding model
    print("\n📥 Step 1: Loading embedding model...")
    print("   (This may take a moment on first run)")
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast model
    DIMENSION = 384  # Dimension for all-MiniLM-L6-v2
    print("   ✓ Model loaded: all-MiniLM-L6-v2 (384 dimensions)")
    
    # Connect to database
    print(f"\n🔌 Step 2: Connecting to VectorAI DB at {SERVER}...")
    with CortexClient(SERVER) as client:
        version, _ = client.health_check()
        print(f"   ✓ Connected to {version}")
        
        # Create collection
        print(f"\n💾 Step 3: Creating collection '{COLLECTION}'...")
        client.create_collection(
            name=COLLECTION,
            dimension=DIMENSION,
            distance_metric=DistanceMetric.COSINE,
            hnsw_ef_search=100,  # Higher value for better accuracy
        )
        print("   ✓ Collection created with COSINE similarity")
        
        # Chunk the documents
        print("\n📄 Step 4: Processing and chunking documents...")
        chunks = chunk_text(KNOWLEDGE_BASE)
        print(f"   ✓ Created {len(chunks)} text chunks")
        
        # Generate embeddings and store
        print("\n🧠 Step 5: Generating embeddings and storing in database...")
        print("   (This may take a moment...)")
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = model.encode(texts, show_progress_bar=False)
        
        # Prepare data for batch upsert
        ids = list(range(len(chunks)))
        vectors = [emb.tolist() for emb in embeddings]
        payloads = chunks  # Store chunk metadata
        
        client.batch_upsert(COLLECTION, ids, vectors, payloads)
        print(f"   ✓ Stored {len(chunks)} document chunks with embeddings")
        
        # Verify storage
        count = client.count(COLLECTION)
        print(f"   ✓ Verified: {count} vectors in database")
        
        # Now let's do RAG queries!
        print("\n" + "=" * 70)
        print("🔍 RAG Query Examples")
        print("=" * 70)
        
        queries = [
            "What are the key features of Actian VectorAI DB?",
            "How do I get started with the database?",
            "What distance metrics are supported?",
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'─' * 70}")
            print(f"Query {i}: {query}")
            print('─' * 70)
            
            # Step 1: Embed the query
            print("\n  1️⃣  Embedding query...")
            query_embedding = model.encode([query])[0].tolist()
            
            # Step 2: Retrieve relevant chunks
            print("  2️⃣  Retrieving relevant context from VectorAI DB...")
            results = client.search(COLLECTION, query_embedding, top_k=3)
            
            print(f"     Found {len(results)} relevant chunks:")
            result_ids = [result.id for result in results]
            fetched = client.get_many(COLLECTION, result_ids)
            context_pieces = []
            for j, (result, (_, payload)) in enumerate(zip(results, fetched), 1):
                context_pieces.append(payload["text"])
                print(f"       • Chunk {j} (similarity: {result.score:.4f})")
            
            # Step 3: Generate answer
            print("  3️⃣  Generating answer...")
            context = "\n\n".join(context_pieces)
            
            if USE_LOCAL:
                answer = generate_answer_local(query, context)
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    answer = generate_answer_openai(query, context, api_key)
                else:
                    print("     ⚠️  OPENAI_API_KEY not set, using local mode")
                    answer = generate_answer_local(query, context)
            
            print(f"\n  📝 Answer:\n")
            for line in answer.split('\n'):
                print(f"     {line}")
        
        # Cleanup
        print("\n" + "=" * 70)
        print("🧹 Cleanup")
        print("=" * 70)
        client.delete_collection(COLLECTION)
        print(f"✓ Collection '{COLLECTION}' deleted")
    
    print("\n" + "=" * 70)
    print("✅ RAG Example Completed Successfully!")
    print("=" * 70)
    print("\n💡 Key Takeaways:")
    print("   • Documents are chunked and embedded into vectors")
    print("   • Vectors are stored in VectorAI DB with metadata")
    print("   • User queries are embedded using the same model")
    print("   • Similar vectors are retrieved via semantic search")
    print("   • Retrieved context is used to generate accurate answers")
    print("\n🎯 This is how VectorAI DB integrates into AI applications!")
    print("=" * 70)


if __name__ == "__main__":
    main()

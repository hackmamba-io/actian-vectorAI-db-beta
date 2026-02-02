#!/usr/bin/env python3
############################################################
#
# Copyright (C) 2025 - Actian Corp.
#
############################################################

"""Cortex Semantic Search Example.

Demonstrates building a semantic search application with:
- Text embeddings (simulated)
- Payload filtering
- Scroll/pagination

Usage:
    python examples/semantic_search.py [server_address]
"""

import sys
import uuid
import numpy as np
from cortex import CortexClient, DistanceMetric
from cortex.filters import Filter, Field

# Configuration
SERVER = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
# Use unique name to avoid  file conflicts
COLLECTION = f"documents_{uuid.uuid4().hex[:8]}"
DIMENSION = 384  # Typical for small embedding models


# Sample documents (in real app, these would be embedded with a model)
DOCUMENTS = [
    {"title": "Introduction to Machine Learning", "category": "AI", "year": 2023},
    {"title": "Deep Learning Fundamentals", "category": "AI", "year": 2023},
    {"title": "Natural Language Processing", "category": "AI", "year": 2022},
    {"title": "Computer Vision Techniques", "category": "AI", "year": 2023},
    {"title": "Database Design Patterns", "category": "Database", "year": 2022},
    {"title": "SQL Performance Optimization", "category": "Database", "year": 2021},
    {"title": "NoSQL Data Modeling", "category": "Database", "year": 2023},
    {"title": "Vector Database Architecture", "category": "Database", "year": 2024},
    {"title": "Web Development with React", "category": "Web", "year": 2023},
    {"title": "Backend API Design", "category": "Web", "year": 2022},
    {"title": "Cloud Native Applications", "category": "Cloud", "year": 2023},
    {"title": "Kubernetes Best Practices", "category": "Cloud", "year": 2024},
    {"title": "Security in Modern Applications", "category": "Security", "year": 2023},
    {"title": "Authentication and Authorization", "category": "Security", "year": 2022},
    {"title": "Data Privacy and Compliance", "category": "Security", "year": 2024},
]


def simulate_embedding(text: str, dim: int = DIMENSION) -> list[float]:
    """Simulate text embedding (in real app, use a model like sentence-transformers)."""
    np.random.seed(hash(text) % 2**32)
    vec = np.random.randn(dim).astype(np.float32)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()


def main():
    print("=" * 60)
    print("Cortex Semantic Search Example")
    print("=" * 60)
    
    with CortexClient(SERVER) as client:
        version, _ = client.health_check()
        print(f"\n✓ Connected to {version}")
        
        # Create collection
        print(f"\n1. Creating document collection...")
        client.create_collection(
            name=COLLECTION,
            dimension=DIMENSION,
            distance_metric=DistanceMetric.COSINE,
        )
        
        # Index documents
        print(f"\n2. Indexing {len(DOCUMENTS)} documents...")
        ids = list(range(len(DOCUMENTS)))
        vectors = [simulate_embedding(doc["title"]) for doc in DOCUMENTS]
        
        client.batch_upsert(COLLECTION, ids, vectors, DOCUMENTS)
        print(f"   ✓ Indexed {len(DOCUMENTS)} documents")
        
        # Basic search
        print("\n" + "-" * 40)
        query = "machine learning models"
        print(f"Query: '{query}'")
        query_vec = simulate_embedding(query)
        
        results = client.search(COLLECTION, query_vec, top_k=5)
        print("\nTop 5 results:")
        for i, r in enumerate(results):
            vec, payload = client.get(COLLECTION, r.id)
            print(f"  {i+1}. {payload['title']} ({payload['category']}, {payload['year']}) - Score: {r.score:.4f}")
        
        # Category-specific search
        print("\n" + "-" * 40)
        print("Query: 'database' filtered by category='Database'")
        
        query_vec = simulate_embedding("database")
        f = Filter().must(Field("category").eq("Database"))
        
        results = client.search_filtered(COLLECTION, query_vec, f, top_k=3)
        print(f"\nDatabase documents ({len(results)} results):")
        for i, r in enumerate(results):
            vec, payload = client.get(COLLECTION, r.id)
            print(f"  {i+1}. {payload['title']} ({payload['year']})")
        
        # Scroll all documents
        print("\n" + "-" * 40)
        print("Scrolling all documents by category:")
        
        categories = {}
        next_cursor = None
        while True:
            records, next_cursor = client.scroll(COLLECTION, limit=10, cursor=next_cursor)
            for record in records:
                cat = record.payload.get("category", "Unknown") if record.payload else "Unknown"
                categories[cat] = categories.get(cat, 0) + 1
            if next_cursor is None:
                break
        
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} documents")
        
        # Cleanup
        print("\n3. Cleanup...")
        client.delete_collection(COLLECTION)
        print(f"   ✓ Collection deleted")
    
    print("\n" + "=" * 60)
    print("✓ Semantic Search Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

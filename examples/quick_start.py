#!/usr/bin/env python3
############################################################
#
# Copyright (C) 2025 - Actian Corp.
#
############################################################

"""Cortex Quick Start Example.

Demonstrates basic Cortex client usage .
This is the recommended starting point for new users.

Usage:
    python examples/quick_start.py [server_address]
    
Example:
    python examples/quick_start.py localhost:50051
"""

import sys
import uuid
import numpy as np
from cortex import CortexClient, DistanceMetric

# Configuration
SERVER = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
# Use unique name to avoid  file conflicts (TODO: server-side fix)
COLLECTION = f"quick_start_{uuid.uuid4().hex[:8]}"
DIMENSION = 128
NUM_VECTORS = 100


def main():
    print("=" * 60)
    print("Cortex Quick Start Example")
    print("=" * 60)
    
    # Connect to Cortex
    with CortexClient(SERVER) as client:
        # Health check
        version, uptime = client.health_check()
        print(f"\n✓ Connected to {version}")
        
        # Create collection with production-grade 
        print(f"\n1. Creating collection '{COLLECTION}'...")
        client.create_collection(
            name=COLLECTION,
            dimension=DIMENSION,
            distance_metric=DistanceMetric.COSINE,
        )
        print(f"   ✓ Collection created ")
        
        # Insert vectors with payloads
        print(f"\n2. Inserting {NUM_VECTORS} vectors...")
        ids = list(range(NUM_VECTORS))
        vectors = [np.random.randn(DIMENSION).astype(np.float32).tolist() 
                   for _ in range(NUM_VECTORS)]
        payloads = [
            {
                "id": i,
                "category": "electronics" if i % 3 == 0 else "clothing" if i % 3 == 1 else "food",
                "price": float(i * 10 + np.random.rand() * 100),
                "in_stock": i % 2 == 0,
            }
            for i in range(NUM_VECTORS)
        ]
        
        client.batch_upsert(COLLECTION, ids, vectors, payloads)
        print(f"   ✓ Inserted {NUM_VECTORS} vectors")
        
        # Verify count
        count = client.count(COLLECTION)
        print(f"\n3. Vector count: {count}")
        
        # Search
        print("\n4. Searching for similar vectors...")
        query = np.random.randn(DIMENSION).astype(np.float32).tolist()
        results = client.search(COLLECTION, query, top_k=5)
        
        print(f"   Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"   [{i+1}] ID: {result.id}, Score: {result.score:.4f}")
        
        # Get vector with payload
        print("\n5. Retrieving vector details...")
        vec, payload = client.get(COLLECTION, results[0].id)
        print(f"   Top result payload: {payload}")
        
        # Scroll through all vectors
        print("\n6. Scrolling through vectors...")
        records, next_cursor = client.scroll(COLLECTION, limit=10)
        print(f"   Retrieved {len(records)} records, next_cursor: {next_cursor}")
        
        # Cleanup
        print("\n7. Cleanup...")
        client.delete_collection(COLLECTION)
        print(f"   ✓ Collection deleted")
        
    print("\n" + "=" * 60)
    print("✓ Quick Start Example Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

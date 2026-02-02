#!/usr/bin/env python3
############################################################
#
# Copyright (C) 2025 - Actian Corp.
#
############################################################

"""Cortex Async Client Example.

Demonstrates async/await usage with AsyncCortexClient.
Suitable for high-performance applications and async frameworks.

Usage:
    python examples/async_example.py [server_address]
"""

import sys
import uuid
import asyncio
import numpy as np
from cortex import AsyncCortexClient, DistanceMetric

# Configuration
SERVER = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
# Use unique name to avoid  file conflicts
COLLECTION = f"async_demo_{uuid.uuid4().hex[:8]}"
DIMENSION = 128
NUM_VECTORS = 200


async def main():
    print("=" * 60)
    print("Cortex Async Client Example")
    print("=" * 60)
    
    async with AsyncCortexClient(SERVER) as client:
        # Health check
        version, uptime = await client.health_check()
        print(f"\n✓ Connected to {version}")
        
        # Create collection
        print(f"\n1. Creating collection '{COLLECTION}'...")
        await client.create_collection(
            name=COLLECTION,
            dimension=DIMENSION,
            distance_metric=DistanceMetric.EUCLIDEAN,
        )
        print(f"   ✓ Collection created")
        
        # Batch insert
        print(f"\n2. Inserting {NUM_VECTORS} vectors...")
        ids = list(range(NUM_VECTORS))
        vectors = [np.random.randn(DIMENSION).astype(np.float32).tolist() 
                   for _ in range(NUM_VECTORS)]
        payloads = [{"id": i, "category": f"cat_{i % 5}"} for i in range(NUM_VECTORS)]
        
        await client.batch_upsert(COLLECTION, ids, vectors, payloads)
        print(f"   ✓ Batch insert complete")
        
        # Count
        count = await client.count(COLLECTION)
        print(f"\n3. Vector count: {count}")
        
        # Parallel searches (async advantage!)
        print("\n4. Running 5 parallel searches...")
        queries = [np.random.randn(DIMENSION).astype(np.float32).tolist() 
                   for _ in range(5)]
        
        # Execute searches in parallel
        search_tasks = [
            client.search(COLLECTION, q, top_k=3) 
            for q in queries
        ]
        results_list = await asyncio.gather(*search_tasks)
        
        for i, results in enumerate(results_list):
            print(f"   Query {i+1}: {len(results)} results, top score: {results[0].score:.4f}")
        
        # Get multiple vectors
        print("\n5. Getting multiple vectors...")
        results = await client.get_many(COLLECTION, [0, 10, 20, 30])
        valid = sum(1 for v, p in results if v is not None)
        print(f"   Retrieved {valid}/4 vectors")
        
        # Scroll
        print("\n6. Async scroll...")
        records, next_off = await client.scroll(COLLECTION, limit=20)
        print(f"   Scrolled {len(records)} records")
        
        # Stats
        stats = await client.get_stats(COLLECTION)
        print(f"\n7. Collection stats: {stats.total_vectors} vectors")
        
        # Cleanup
        print("\n8. Cleanup...")
        await client.delete_collection(COLLECTION)
        print(f"   ✓ Collection deleted")
    
    print("\n" + "=" * 60)
    print("✓ Async Example Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

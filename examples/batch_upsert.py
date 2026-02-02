#!/usr/bin/env python3
"""
////////////////////////////////////////////////////////////
//
// Copyright (C) 2025 - Actian Corp.
//
////////////////////////////////////////////////////////////

Batch upsert example for high-throughput vector insertion.

This example shows:
- Creating a collection 
- Batch inserting vectors efficiently
- Measuring throughput performance
- Verifying the insertion

Usage:
    python batch_upsert.py [server_address]
    
    server_address: Cortex server address (default: localhost:50051)
"""

import asyncio
import sys
import time
import numpy as np
from cortex import AsyncCortexClient


async def main(server: str = "localhost:50051"):
    """Batch upsert example with performance measurement."""
    
    async with AsyncCortexClient(server, enable_smart_batching=False) as client:
        version, _ = await client.health_check()
        print(f"Connected to Cortex {version}")

        collection_name = "batch_example"
        dimension = 768        # Standard embedding dimension
        num_vectors = 10000

        # Clean up any existing collection
        try:
            await client.delete_collection(collection_name)
        except Exception:
            pass

        # Create collection 
        print(f"\nCreating collection '{collection_name}'...")
        await client.create_collection(
            collection_name,
            dimension=dimension,
            distance_metric="EUCLIDEAN",
            hnsw_m=32,
            hnsw_ef_construct=256,
            hnsw_ef_search=1000,
        )

        # Generate batch data
        print(f"\nPreparing {num_vectors} vectors...")
        ids = list(range(num_vectors))
        vectors = [np.random.rand(dimension).tolist() for _ in range(num_vectors)]
        payloads = [{"index": i, "batch": i // 100} for i in range(num_vectors)]

        # Batch upsert with timing using server-side batching
        print("Batch upserting with server-side batching...")
        start = time.time()
        
        # Use batch_upsert - server handles chunking internally
        try:
            await asyncio.wait_for(
                client.batch_upsert(collection_name, ids, vectors, payloads),
                timeout=120.0
            )
            upserted = num_vectors
        except asyncio.TimeoutError:
            print("Batch upsert timed out!")
            return
            
        elapsed = time.time() - start

        print(f"Inserted {num_vectors} vectors in {elapsed:.2f}s")
        print(f"Throughput: {num_vectors / elapsed:.0f} vectors/sec")

        # Flush to ensure data is persisted
        await client.flush(collection_name)

        # Verify count
        count = await client.get_vector_count(collection_name)
        print(f"\nVector count: {count}")

        # Get collection stats
        stats = await client.get_stats(collection_name)
        print(f"Stats: total={stats.total_vectors}, indexed={stats.indexed_vectors}")

        # Test search performance
        print("\nTesting search performance...")
        search_times = []
        for _ in range(10):
            query = np.random.rand(dimension).tolist()
            start = time.time()
            results = await client.search(collection_name, query, top_k=10)
            search_times.append(time.time() - start)
        
        avg_search_time = sum(search_times) / len(search_times)
        print(f"Average search time: {avg_search_time*1000:.2f}ms")

        # Clean up
        await client.delete_collection(collection_name)
        print("\nExample completed!")


if __name__ == "__main__":
    server_addr = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    asyncio.run(main(server_addr))

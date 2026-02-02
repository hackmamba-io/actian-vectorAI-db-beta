#!/usr/bin/env python3
"""
////////////////////////////////////////////////////////////
//
// Copyright (C) 2025 - Actian Corp.
//
////////////////////////////////////////////////////////////

Simple example demonstrating basic Cortex client usage.

This example shows:
- Creating a collection 
- Inserting vectors with payloads
- Searching for similar vectors
- Cleaning up

Usage:
    python simple.py [server_address]
    
    server_address: Cortex server address (default: localhost:50051)
"""

import asyncio
import sys
import numpy as np
from cortex import AsyncCortexClient


async def main(server: str = "localhost:50051"):
    """Simple example of Cortex client usage."""
    
    # Connect to Cortex server
    async with AsyncCortexClient(server, enable_smart_batching=False) as client:
        # Check server health
        version, uptime = await client.health_check()
        print(f"Connected to Cortex {version}, uptime: {uptime}s")

        collection_name = "example_collection"
        dimension = 128

        # Clean up any existing collection
        try:
            await client.delete_collection(collection_name)
        except Exception:
            pass

        # Create a collection 
        print(f"\n1. Creating collection '{collection_name}'...")
        await client.create_collection(
            collection_name,
            dimension=dimension,
            distance_metric="EUCLIDEAN",
            hnsw_m=32,
            hnsw_ef_construct=256,
            hnsw_ef_search=1000,
        )
        print("   Collection created!")

        # Insert vectors
        print("\n2. Inserting vectors...")
        for i in range(10):
            vector = np.random.rand(dimension).tolist()
            payload = {"index": i, "label": f"item_{i}"}
            await client.upsert(collection_name, id=i, vector=vector, payload=payload)
        print("   Inserted 10 vectors!")

        # Check count
        count = await client.get_vector_count(collection_name)
        print(f"\n3. Vector count: {count}")

        # Search for similar vectors
        print("\n4. Searching for similar vectors...")
        query = np.random.rand(dimension).tolist()
        results = await client.search(collection_name, query, top_k=5)

        print(f"   Found {len(results)} results:")
        for result in results:
            print(f"   - ID: {result.id}, Score: {result.score:.4f}")

        # Clean up
        print("\n5. Cleaning up...")
        await client.delete_collection(collection_name)
        print("   Collection deleted!")

        print("\n" + "=" * 50)
        print("Example completed successfully!")


if __name__ == "__main__":
    server_addr = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    asyncio.run(main(server_addr))

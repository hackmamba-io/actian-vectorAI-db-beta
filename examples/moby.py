#!/usr/bin/env python3
############################################################
#
# Copyright (C) 2025 - Actian Corp.
#
############################################################
"""Moby Dick Example.

Demonstrates basic Cortex client usage .

Usage:
    python examples/moby.py

"""

import sys
import ast
import numpy as np
from cortex import CortexClient, DistanceMetric

# Configuration
SERVER = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
COLLECTION = "MOBY_DICK_COLLECTION"
DIMENSION = 384
NUM_VECTORS = 1749


def main():
    print("=" * 60)
    print("Moby Dick book - Some sample sentence vectors")
    print("=" * 60)

    # Connect to Cortex
    with CortexClient(SERVER) as client:
        # Health check
        # version, uptime = client.health_check()
        print("Client health: " + str(client.health_check()))

        # Check if collection already exists and recreate if it exists.
        if client.collection_exists(name=COLLECTION):
            # Re-create collection with production-grade
            print(f"\n1. Re-creating collection '{COLLECTION}'...")
            client.recreate_collection(
                name=COLLECTION,
                dimension=DIMENSION,
                distance_metric=DistanceMetric.COSINE,
            )
            print(f"   ✓ Collection recreated ")
        else:
            # Create collection if collection does not exist.
            print(f"\n1. Creating collection '{COLLECTION}'...")
            client.create_collection(
                name=COLLECTION,
                dimension=DIMENSION,
                distance_metric=DistanceMetric.COSINE,
            )
            print(f"   ✓ Collection created ")

        # Start inserting vectors.
        with open("./examples/vectors/moby_vectors1.txt", 'r', encoding='utf-8') as f:
            count = client.count(COLLECTION) + 1
            for line in f:
                vector_data = {
                    "id": count,
                    'book_name': "Moby Dick",
                }

                client.upsert(COLLECTION, id=count, vector=ast.literal_eval(line), payload=vector_data)
                count = count + 1
                # Show progress
                if count % 100 == 0:
                    print(f"- Inserted {count} vectors")

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

        # Close Collection:
        print("\n7. Close collection...")
        client.close_collection(COLLECTION)
        print(f"   ✓ Collection closed")


    print("\n" + "=" * 60)
    print("✓ Moby Dick Example Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

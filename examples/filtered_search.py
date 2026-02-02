#!/usr/bin/env python3
"""
////////////////////////////////////////////////////////////
//
// Copyright (C) 2025 - Actian Corp.
//
////////////////////////////////////////////////////////////

Filtered search example demonstrating the Filter DSL.

This example shows:
- Creating a collection 
- Inserting vectors with rich payload data
- Using the Filter DSL for filtered search
- Combining must, should, and must_not conditions
- Retrieving payload and vectors with search results
- Using JSON string filters as an alternative

Usage:
    python filtered_search.py [server_address]
    
    server_address: Cortex server address (default: localhost:50051)
"""

import asyncio
import sys
import json
import numpy as np
from cortex import AsyncCortexClient
from cortex.filters import Filter, Field


async def main(server: str = "localhost:50051"):
    """Filtered search example with various filter conditions."""
    
    async with AsyncCortexClient(server, enable_smart_batching=False) as client:
        version, _ = await client.health_check()
        print(f"Connected to Cortex {version}")

        collection_name = "filter_example"
        dimension = 128

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

        # Insert vectors with rich payloads
        print("\nInserting vectors with payloads...")
        categories = ["electronics", "books", "clothing", "food", "toys"]
        for i in range(50):
            vector = np.random.rand(dimension).tolist()
            payload = {
                "category": categories[i % len(categories)],
                "price": 10 + (i * 5),
                "in_stock": i % 3 != 0,
                "rating": 3.0 + (i % 3),
                "doc_id": f"doc-{i:04d}",
            }
            await client.upsert(collection_name, id=i, vector=vector, payload=payload)
        print("Inserted 50 vectors!")

        # Build query vector
        query_vector = np.random.rand(dimension).tolist()

        # Build and demonstrate filters
        print("\n" + "=" * 60)
        print("FILTERED SEARCH EXAMPLES")
        print("=" * 60)

        # Example 1: Simple equality filter with payload
        print("\n1. Electronics only (with payload):")
        filter1 = Filter().must(Field("category").eq("electronics"))
        print(f"   Filter: {filter1}")  # Uses new __str__ method
        results = await client.search(
            collection_name,
            query_vector,
            top_k=5,
            filter=filter1,
            with_payload=True,  # Get payload with results
        )
        print(f"   Found {len(results)} results:")
        for r in results:
            if r.payload:
                print(f"      ID: {r.id}, Score: {r.score:.4f}, Category: {r.payload.get('category')}")

        # Example 2: Range filter
        print("\n2. Price < $100:")
        filter2 = Filter().must(Field("price").lt(100))
        results = await client.search(
            collection_name,
            query_vector,
            top_k=5,
            filter=filter2,
            with_payload=True,
        )
        print(f"   Found {len(results)} results")
        for r in results:
            if r.payload:
                print(f"      ID: {r.id}, Price: ${r.payload.get('price')}")

        # Example 3: Combined filter
        print("\n3. Electronics with price < $100 and in stock:")
        filter3 = (
            Filter()
            .must(Field("category").eq("electronics"))
            .must(Field("price").lt(100))
            .must(Field("in_stock").eq(True))
        )
        results = await client.search(
            collection_name,
            query_vector,
            top_k=5,
            filter=filter3,
            with_payload=True,
        )
        print(f"   Found {len(results)} results")

        # Example 4: With vectors returned
        print("\n4. Search with vectors returned:")
        filter4 = Filter().must(Field("category").eq("books"))
        results = await client.search(
            collection_name,
            query_vector,
            top_k=3,
            filter=filter4,
            with_payload=True,
            with_vectors=True,  # Get vectors with results
        )
        print(f"   Found {len(results)} results:")
        for r in results:
            if r.vector:
                print(f"      ID: {r.id}, Vector dim: {len(r.vector)}, First 3: {r.vector[:3]}")

        # Example 5: Using JSON string filter (alternative to Filter object)
        print("\n5. Using JSON string filter:")
        json_filter = '{"category": "toys"}'
        results = await client.search(
            collection_name,
            query_vector,
            top_k=5,
            filter=json_filter,  # Pass JSON string directly
            with_payload=True,
        )
        print(f"   Filter JSON: {json_filter}")
        print(f"   Found {len(results)} results")

        # Example 6: Filter by specific doc_id (UUID-like string)
        print("\n6. Filter by specific doc_id:")
        target_doc_id = "doc-0010"
        filter6 = Filter().must(Field("doc_id").eq(target_doc_id))
        results = await client.search(
            collection_name,
            query_vector,
            top_k=5,
            filter=filter6,
            with_payload=True,
        )
        print(f"   Looking for doc_id: {target_doc_id}")
        print(f"   Found {len(results)} results")
        for r in results:
            if r.payload:
                print(f"      Found: {r.payload.get('doc_id')}")

        # Example 7: Must not clause
        print("\n7. Not out of stock:")
        filter7 = Filter().must_not(Field("in_stock").eq(False))
        results = await client.search(
            collection_name,
            query_vector,
            top_k=5,
            filter=filter7,
            with_payload=True,
        )
        print(f"   Found {len(results)} results")

        # Example 8: Empty filter (no filtering)
        print("\n8. Empty filter (search all):")
        empty_filter = Filter()
        print(f"   Filter is empty: {empty_filter.is_empty()}")
        print(f"   Filter bool: {bool(empty_filter)}")  # False for empty
        results = await client.search(
            collection_name,
            query_vector,
            top_k=5,
            filter=empty_filter,
        )
        print(f"   Found {len(results)} results (no filtering)")

        # Show filter DSL features
        print("\n" + "=" * 60)
        print("FILTER DSL FEATURES")
        print("=" * 60)

        # Complex filter with all clause types
        complex_filter = (
            Filter()
            .must(Field("category").eq("electronics"))
            .must(Field("price").range(gte=50, lte=200))
            .should(Field("rating").gte(4.0))
            .must_not(Field("in_stock").eq(False))
        )
        
        print("\nComplex filter:")
        print(f"   repr():     {repr(complex_filter)}")
        print(f"   str():      {complex_filter}")
        print(f"   is_empty(): {complex_filter.is_empty()}")
        print(f"   bool():     {bool(complex_filter)}")
        
        print("\n   JSON (compact):")
        print(f"   {complex_filter.to_json()}")
        
        print("\n   Dict:")
        import pprint
        pprint.pprint(complex_filter.to_dict(), indent=6)

        # Filter copy
        print("\n   Filter copy:")
        copied = complex_filter.copy()
        print(f"   Original: {repr(complex_filter)}")
        print(f"   Copied:   {repr(copied)}")

        # Clean up
        await client.delete_collection(collection_name)
        print("\n" + "=" * 60)
        print("Example completed!")


if __name__ == "__main__":
    server_addr = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    asyncio.run(main(server_addr))


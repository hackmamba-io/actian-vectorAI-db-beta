#!/usr/bin/env python3
"""Query and Describe API example for Cortex Python client.

Demonstrates query and describe methods that have been implemented in Cortex:
- query() - Filter/ID based retrieval (like SQL SELECT)
- describe_collection() - Get collection metadata
- get_collection_stats() - Collection statistics
- has_collection() - Check collection exists
- drop_collection() - Delete collection 
"""

from cortex import CortexClient
import random

def main():
    print("=" * 60)
    print("Query and Describe API Example")
    print("=" * 60)
    
    with CortexClient("localhost:50051") as client:
        collection_name = "query_example"
        dimension = 128
        
        # Cleanup first
        if client.has_collection(collection_name):
            client.delete_collection(collection_name)
        
        # 1. Create collection
        print("\n1. Creating collection...")
        client.create_collection(collection_name, dimension)
        print(f"   ✓ Collection '{collection_name}' created")
        
        # 2. Insert data
        print("\n2. Inserting data...")
        data = []
        for i in range(10):
            vector = [random.random() for _ in range(dimension)]
            payload = {
                "name": f"product_{i}",
                "category": "electronics" if i % 2 == 0 else "clothing",
                "price": 100 + i * 10,
                "in_stock": i % 3 != 0
            }
            client.upsert(collection_name, i, vector, payload)
            data.append({"id": i, **payload})
        print(f"   ✓ Inserted {len(data)} entities")
        
        # 3. Describe collection
        print("\n3. describe_collection()...")
        info = client.describe_collection(collection_name)
        print(f"   Name: {info['name']}")
        print(f"   Status: {info['status']}")
        print(f"   Vectors: {info['vectors_count']}")
        print(f"   Storage: {info['storage_bytes']} bytes")
        
        # 4. Query by IDs
        print("\n4. query(ids=[0, 1, 2])...")
        results = client.query(collection_name, ids=[0, 1, 2])
        print(f"   Got {len(results)} entities:")
        for r in results:
            print(f"   - id={r.get('id')}, name={r.get('name')}, category={r.get('category')}")
        
        # 5. Query with limit (paginated retrieval)
        print("\n5. query(limit=5)...")
        results = client.query(collection_name, limit=5)
        print(f"   Got {len(results)} entities:")
        for r in results:
            print(f"   - id={r.get('id')}, name={r.get('name')}")
        
        # 6. Query with vectors
        print("\n6. query(ids=[0], with_vectors=True)...")
        results = client.query(collection_name, ids=[0], with_vectors=True)
        if results and "vector" in results[0]:
            vec = results[0]["vector"]
            print(f"   ✓ Got vector with {len(vec)} dimensions: [{vec[0]:.4f}, {vec[1]:.4f}, ...]")
        else:
            print("   Note: with_vectors requires server support")
        
        # 7. Search (vector similarity)
        print("\n7. search()...")
        query_vector = [random.random() for _ in range(dimension)]
        search_results = client.search(collection_name, query_vector, top_k=3)
        print(f"   Top 3 results:")
        for r in search_results:
            print(f"   - id={r.id}, score={r.score:.4f}")
        
        # 8. Delete by IDs
        print("\n8. Deleting by ID...")
        client.delete(collection_name, 9)
        print("   ✓ Deleted entity with id=9")
        
        # 9. Drop collection 
        print("\n9. Dropping collection...")
        client.delete_collection(collection_name)
        print(f"   ✓ Collection '{collection_name}' dropped")
        
        # Verify
        exists = client.has_collection(collection_name)
        print(f"   ✓ has_collection: {exists}")
    
    print("\n" + "=" * 60)
    print("✓ -Compatible API Example Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

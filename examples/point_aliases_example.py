"""
Point Aliases Example -  API

This example demonstrates how to use Cortex with production 
compatible method names for seamless migration.

 Compatibility:
- upsert_points → batch_upsert
- retrieve → get_many
- scroll → paginated get_many

 Compatibility:
- insert → upsert
- compact → optimize
- query → search with filter

Run: python examples/point_aliases_example.py
"""

import os
import sys
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cortex import CortexClient, Filter, Field

# Configuration
SERVER = os.getenv("CORTEX_SERVER", "localhost:50051")
COLLECTION = "point_aliases_demo"
DIM = 128


def main():
    print("=" * 60)
    print("Cortex Point Aliases Example")
    print("Demonstrating  API")
    print("=" * 60)
    
    with CortexClient(SERVER) as client:
        # Health check
        version, uptime = client.health_check()
        print(f"\nConnected to Cortex {version}, uptime: {uptime}s")
        
        # Cleanup existing collection
        if client.has_collection(COLLECTION):
            client.delete_collection(COLLECTION)
        
        # Create collection
        client.create_collection(COLLECTION, DIM)
        print(f"\n1. Created collection '{COLLECTION}'")
        
        # ============================================================
        # : insert (alias for upsert)
        # ============================================================
        print("\n2. Using  'insert' (alias for upsert)...")
        
        # Generate sample vectors with payloads
        np.random.seed(42)
        vectors = np.random.rand(10, DIM).astype(np.float32).tolist()
        payloads = [
            {"category": "electronics", "price": 299.99, "in_stock": True},
            {"category": "electronics", "price": 599.99, "in_stock": True},
            {"category": "clothing", "price": 49.99, "in_stock": True},
            {"category": "clothing", "price": 79.99, "in_stock": False},
            {"category": "food", "price": 9.99, "in_stock": True},
            {"category": "food", "price": 4.99, "in_stock": True},
            {"category": "books", "price": 19.99, "in_stock": False},
            {"category": "books", "price": 24.99, "in_stock": True},
            {"category": "toys", "price": 39.99, "in_stock": True},
            {"category": "toys", "price": 59.99, "in_stock": False},
        ]
        
        # Insert single item ()
        client.insert(COLLECTION, 0, vectors[0], payloads[0])
        print("   Inserted 1 item using 'insert'")
        
        # ============================================================
        # : upsert_points (alias for batch_upsert)
        # ============================================================
        print("\n3. Using  'upsert_points' (alias for batch_upsert)...")
        
        ids = list(range(1, 10))
        client.upsert_points(COLLECTION, ids, vectors[1:], payloads[1:])
        print(f"   Inserted {len(ids)} items using 'upsert_points'")
        
        # Verify count ()
        count = client.count(COLLECTION)
        print(f"\n4. Collection count (using 'count' alias): {count}")
        
        # ============================================================
        # : retrieve (alias for get_many)
        # ============================================================
        print("\n5. Using  'retrieve' (alias for get_many)...")
        
        results = client.retrieve(COLLECTION, [0, 1, 2])
        print(f"   Retrieved {len(results)} points")
        for vec, payload in results[:2]:
            print(f"   - Category: {payload.get('category')}, Price: ${payload.get('price')}")
        
        # ============================================================
        # Search with filter (common API)
        # NOTE: Filter search requires server-side implementation.
        # Currently returns empty results due to storage driver limitation.
        # ============================================================
        print("\n6. Searching (filter support pending server implementation)...")
        
        # Basic search without filter - WORKS
        query_vec = vectors[0]
        results = client.search(COLLECTION, query_vec, top_k=5)
        print(f"   Basic search found {len(results)} results:")
        for result in results[:3]:
            print(f"   - ID: {result.id}, Score: {result.score:.4f}")
        
        # Filter search - pending server implementation
        print("   Note: Filter search pending server-side storage driver update")

        
        # ============================================================
        # Scroll through all items ()
        # ============================================================
        print("\n7. Using 'scroll' to paginate all vectors...")
        
        all_items = client.scroll(COLLECTION, limit=5)
        print(f"   Scrolled first page: {len(all_items)} items")
        
        # ============================================================
        # Compact ( alias for optimize)
        # ============================================================
        print("\n8.  'compact' (alias for optimize)...")
        try:
            client.compact(COLLECTION)
            print("   Collection compacted!")
        except Exception as e:
            print(f"   Note: compact not supported on this server ({e})")
        
        # ============================================================
        # Cleanup
        # ============================================================
        print("\n9. Cleanup...")
        client.delete_collection(COLLECTION)
        print(f"   Collection '{COLLECTION}' deleted")
        
        print("\n" + "=" * 60)
        print("Point Aliases Example Complete!")
        print("=" * 60)


if __name__ == "__main__":
    main()

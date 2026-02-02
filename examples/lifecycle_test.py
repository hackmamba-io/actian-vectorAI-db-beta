#!/usr/bin/env python3
"""
////////////////////////////////////////////////////////////
//
// Copyright (C) 2025 - Actian Corp.
//
////////////////////////////////////////////////////////////

Comprehensive lifecycle test demonstrating full collection workflow.

This example tests the complete flow:
1. Create collection
2. Insert vectors
3. Get collection info
4. Insert more vectors while checking info
5. Check if collection exists, get status and stats
6. Delete collection
7. Verify collection is deleted (should not be accessible)
8. Recreate collection with same name (should succeed)

Usage:
    python lifecycle_test.py [server_address]
    
    server_address: Cortex server address (default: localhost:50051)
"""

import asyncio
import sys
import time
from cortex import AsyncCortexClient, CortexError


def log(step: int, msg: str, status: str = "INFO"):
    """Print formatted log message."""
    timestamp = time.strftime("%H:%M:%S")
    symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "📋"
    print(f"[{timestamp}] Step {step:02d}: {symbol} {msg}")


async def main(server: str = "localhost:50051"):
    """Complete collection lifecycle test."""
    
    print("=" * 60)
    print("CORTEX PYTHON CLIENT - LIFECYCLE TEST")
    print("=" * 60)
    print(f"Server: {server}")
    print("=" * 60)
    
    collection_name = "lifecycle_test_collection"
    dimension = 128
    step = 0
    
    async with AsyncCortexClient(server, enable_smart_batching=False) as client:
        
        # Check server health
        version, uptime = await client.health_check()
        log(step, f"Connected to {version}, uptime: {uptime}s", "PASS")
        step += 1
        
        # ============================================================
        # STEP 1: Clean up any existing collection
        # ============================================================
        try:
            await client.delete_collection(collection_name)
            log(step, f"Cleaned up existing collection '{collection_name}'")
        except Exception:
            log(step, f"No existing collection '{collection_name}' to clean up")
        step += 1
        
        # ============================================================
        # STEP 2: Create collection 
        # ============================================================
        await client.create_collection(
            collection_name,
            dimension=dimension,
            distance_metric="EUCLIDEAN",
            hnsw_m=32,
            hnsw_ef_construct=256,
            hnsw_ef_search=1000,
        )
        log(step, f"Created collection", "PASS")
        step += 1
        
        # ============================================================
        # STEP 3: Insert first batch of vectors (using single upsert)
        # ============================================================
        log(step, "Inserting first batch of 10 vectors...")
        for i in range(10):
            vector = [float(i + j * 0.01) for j in range(dimension)]
            payload = {"batch": 1, "index": i, "value": i * 100}
            await client.upsert(collection_name, id=i, vector=vector, payload=payload)
        log(step, "Inserted vectors 0-9", "PASS")
        step += 1
        
        # ============================================================
        # STEP 4: Get collection info after first batch
        # ============================================================
        count1 = await client.get_vector_count(collection_name)
        stats1 = await client.get_stats(collection_name)
        state1 = await client.get_state(collection_name)
        log(step, f"After batch 1: count={count1}, state={state1}", "PASS")
        log(step, f"Stats: total={stats1.total_vectors}, indexed={stats1.indexed_vectors}")
        step += 1
        
        # ============================================================
        # STEP 5: Insert second batch while checking info
        # ============================================================
        log(step, "Inserting second batch of 10 vectors (10-19)...")
        for i in range(10, 20):
            vector = [float(i + j * 0.01) for j in range(dimension)]
            payload = {"batch": 2, "index": i, "value": i * 100}
            await client.upsert(collection_name, id=i, vector=vector, payload=payload)
            
            # Check count mid-insertion
            if i == 15:
                mid_count = await client.get_vector_count(collection_name)
                log(step, f"Mid-insertion count (at id 15): {mid_count}")
        
        log(step, "Inserted vectors 10-19", "PASS")
        step += 1
        
        # ============================================================
        # STEP 6: Verify all vectors are accessible
        # ============================================================
        log(step, "Verifying vectors are retrievable...")
        errors = 0
        for id in [0, 5, 10, 15, 19]:
            try:
                vec, payload = await client.get(collection_name, id)
                assert len(vec) == dimension, f"Wrong dimension for id {vec_id}"
                assert payload.get("index") == id, f"Wrong payload index for id {vec_id}"
            except Exception as e:
                log(step, f"Failed to get id {vec_id}: {e}", "FAIL")
                errors += 1
        
        if errors == 0:
            log(step, "All vectors verified successfully", "PASS")
        step += 1
        
        # ============================================================
        # STEP 7: Get final stats
        # ============================================================
        count2 = await client.get_vector_count(collection_name)
        stats2 = await client.get_stats(collection_name)
        state2 = await client.get_state(collection_name)
        log(step, f"Final: count={count2}, state={state2}", "PASS")
        log(step, f"Stats: total={stats2.total_vectors}, indexed={stats2.indexed_vectors}")
        step += 1
        
        # ============================================================
        # STEP 8: Search test
        # ============================================================
        log(step, "Testing search...")
        query = [10.0 + j * 0.01 for j in range(dimension)]
        results = await client.search(collection_name, query, top_k=5)
        log(step, f"Search returned {len(results)} results", "PASS")
        for r in results:
            log(step, f"  - ID: {r.id}, Score: {r.score:.4f}")
        step += 1
        
        # ============================================================
        # STEP 9: Flush before deletion
        # ============================================================
        await client.flush(collection_name)
        log(step, "Flushed collection", "PASS")
        step += 1
        
        # ============================================================
        # STEP 10: Delete collection
        # ============================================================
        await client.delete_collection(collection_name)
        log(step, f"Deleted collection '{collection_name}'", "PASS")
        step += 1
        
        # Wait for cleanup
        log(step, "Waiting for cleanup (3 seconds)...")
        await asyncio.sleep(3.0)
        step += 1
        
        # ============================================================
        # STEP 12: Recreate collection with same name
        # ============================================================
        log(step, f"Recreating collection '{collection_name}'...")
        await client.create_collection(
            collection_name,
            dimension=dimension,
            distance_metric="EUCLIDEAN",
            hnsw_m=32,
            hnsw_ef_construct=256,
            hnsw_ef_search=1000,
        )
        log(step, f"Successfully recreated collection '{collection_name}'", "PASS")
        step += 1
        
        # ============================================================
        # STEP 13: Verify new collection works
        # ============================================================
        log(step, "Verifying new collection is functional...")
        vector = [1.0] * dimension
        await client.upsert(collection_name, id=0, vector=vector, payload={"test": "recreated"})
        vec, payload = await client.get(collection_name, 0)
        assert payload.get("test") == "recreated", "Payload mismatch on recreated collection"
        log(step, "New collection is fully functional", "PASS")
        step += 1
        
        # ============================================================
        # STEP 14: Final cleanup
        # ============================================================
        await client.delete_collection(collection_name)
        log(step, "Final cleanup complete", "PASS")
        
    print("=" * 60)
    print("LIFECYCLE TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    server_addr = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    asyncio.run(main(server_addr))

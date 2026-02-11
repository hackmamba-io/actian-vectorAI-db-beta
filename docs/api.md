# Actian VectorAI DB Python client API reference

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0--beta-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/License-Proprietary-red" alt="License">
</p>

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Client Initialization](#client-initialization)
- [API Reference](#api-reference)
  - [Connection](#connection)
  - [Collection Management](#collection-management)
  - [Vector Operations](#vector-operations)
  - [Search Operations](#search-operations)
  - [Query & Scroll](#query--scroll)
  - [Statistics & Monitoring](#statistics--monitoring)
  - [Maintenance Operations](#maintenance-operations)
- [Filter DSL](#filter-dsl)
- [Models Reference](#models-reference)
- [Error Handling](#error-handling)
- [Async Client](#async-client)
- [Best Practices](#best-practices)
- [Complete Method Reference](#complete-method-reference)
- [Server Limitations & Not Yet Available](#server-limitations--not-yet-available)

---

## Requirements

- Python 3.10+
- numpy 2.2+
- grpcio 1.68+
- pydantic 2.10+

## Installation

```bash
pip install actiancortex-0.1.0b1-py3-none-any.whl
```

---

## Quickstart

### Sync client

```python
from cortex import CortexClient, DistanceMetric

with CortexClient("localhost:50051") as client:
    # Check server connection
    version, uptime = client.health_check()
    print(f"Connected to {version}")
    # Output: Connected to VDSS 1.0.0 / VDE 1.0.0
    
    # Create collection
    client.create_collection(
        name="products",
        dimension=128,
        distance_metric=DistanceMetric.COSINE,
    )
    
    # Insert vectors
    client.upsert(
        "products",
        id=0,
        vector=[0.1]*128,
        payload={"name": "Widget", "price": 29.99}
    )
    
    # Batch insert
    client.batch_upsert(
        "products",
        ids=[1, 2, 3],
        vectors=[[0.2]*128, [0.3]*128, [0.4]*128],
        payloads=[{"i": 1}, {"i": 2}, {"i": 3}]
    )
    
    # Search
    results = client.search("products", query=[0.1]*128, top_k=5, with_payload=True)
    for r in results:
        print(f"ID: {r.id}, Score: {r.score:.4f}, Payload: {r.payload}")
    # Output:
    # ID: 0, Score: 1.0000, Payload: {'name': 'Widget', 'price': 29.99}
    # ID: 1, Score: 1.0000, Payload: {'i': 1}
    # ID: 2, Score: 1.0000, Payload: {'i': 2}
    
    # Get vector count
    count = client.count("products")
    print(f"Total vectors: {count}")
    # Output: Total vectors: 4
    
    # Cleanup
    client.delete_collection("products")
```

### Async client

```python
import asyncio
from cortex import AsyncCortexClient

async def main():
    async with AsyncCortexClient("localhost:50051") as client:
        version, _ = await client.health_check()
        print(f"Connected to {version}")
        
        await client.create_collection("vectors", dimension=128)
        await client.upsert("vectors", id=0, vector=[0.1]*128)
        
        results = await client.search("vectors", query=[0.1]*128, top_k=5)
        print(f"Found {len(results)} results")
        
        await client.delete_collection("vectors")

asyncio.run(main())
```

---

## Initialize client

### CortexClient (sync)

```python
from cortex import CortexClient

client = CortexClient(
    address="localhost:50051",      # Server address (required)
    api_key=None,                   # API key for authentication
    pool_size=3,                    # gRPC channel pool size
    enable_smart_batching=False,    # Auto-batch upserts (disabled for sync)
    batch_size=100,                 # Max items per batch
    batch_timeout_ms=100,           # Max wait before flush
    timeout=None,                   # Default operation timeout
)
```

### AsyncCortexClient (async)

```python
from cortex import AsyncCortexClient

client = AsyncCortexClient(
    address="localhost:50051",
    api_key=None,
    pool_size=3,
    enable_smart_batching=True,     # Enabled by default for async
    batch_size=100,
    batch_timeout_ms=100,
    timeout=None,
)
```

---

## API reference

### Connection

#### `connect()`

Establish connection to the VectorAI DB server.

```python
client.connect()
```

| Parameter | Type | Description |
|-----------|------|-------------|
| (none) | - | - |

**Returns:** `None`

**Note:** Called automatically when using context manager.

---

#### `close()`

Close connection and clean up resources.

```python
client.close()
```

| Parameter | Type | Description |
|-----------|------|-------------|
| (none) | - | - |

**Returns:** `None`

**Note:** Called automatically when using context manager.

---

#### `health_check()`

Check server health and get version info.

```python
version, uptime = client.health_check()
```

| Parameter | Type | Description |
|-----------|------|-------------|
| (none) | - | - |

**Returns:** `tuple[str, int]`

| Return | Type | Description |
|--------|------|-------------|
| version | str | Server version string |
| uptime | int | Server uptime in seconds |

**Example:**
```python
>>> version, uptime = client.health_check()
>>> print(f"Version: {version}, Uptime: {uptime}s")
Version: VDSS 1.0.0 / VDE 1.0.0, Uptime: 0s
```

---

### Collection management

#### `create_collection()`

Create a new vector collection.

```python
client.create_collection(
    name="products",
    dimension=128,
    distance_metric=DistanceMetric.COSINE,
    hnsw_m=16,
    hnsw_ef_construct=200,
    hnsw_ef_search=50,
    config_json=None
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | required | Collection name |
| `dimension` | int | required | Vector dimension |
| `distance_metric` | DistanceMetric \| str | COSINE | Distance metric |
| `hnsw_m` | int | 16 | HNSW edges per node |
| `hnsw_ef_construct` | int | 200 | Build-time neighbors |
| `hnsw_ef_search` | int | 50 | Search-time neighbors |
| `config_json` | str | None | Driver-specific config |

**Returns:** `None`

**Example:**
```python
>>> client.create_collection("embeddings", dimension=768)
>>> client.create_collection(
...     "products",
...     dimension=128,
...     distance_metric=DistanceMetric.EUCLIDEAN,
...     hnsw_m=32,
...     hnsw_ef_construct=256
... )
```

---

#### `delete_collection()`

Delete a collection and all its data.

```python
client.delete_collection(name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Collection name |

**Returns:** `None`

---

#### `has_collection()`

Check if a collection exists.

```python
exists = client.has_collection(name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Collection name |

**Returns:** `bool`

**Example:**
```python
>>> client.has_collection("products")
True
>>> client.has_collection("nonexistent")
False
```

---

#### `open_collection()`

Open an existing collection for operations.

```python
client.open_collection(name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Collection name |

**Returns:** `None`

---

#### `close_collection()`

Close a collection.

```python
client.close_collection(name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Collection name |

**Returns:** `None`

---

#### `recreate_collection()`

Delete if exists, then create new collection.

```python
client.recreate_collection(
    name="products",
    dimension=128,
    distance_metric=DistanceMetric.COSINE
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | required | Collection name |
| `dimension` | int | required | Vector dimension |
| `distance_metric` | DistanceMetric | COSINE | Distance metric |
| `hnsw_m` | int | 16 | HNSW M parameter |
| `hnsw_ef_construct` | int | 200 | Build neighbors |
| `hnsw_ef_search` | int | 50 | Search neighbors |

**Returns:** `None`

---

#### `get_or_create_collection()`

Create collection if it doesn't exist (idempotent).

```python
created = client.get_or_create_collection(
    name="products",
    dimension=128,
    distance_metric=DistanceMetric.COSINE
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | required | Collection name |
| `dimension` | int | required | Vector dimension |
| `distance_metric` | DistanceMetric | COSINE | Distance metric |

**Returns:** `bool` - True if created, False if already existed

**Example:**
```python
>>> created = client.get_or_create_collection("products", dimension=128)
>>> print(f"Created: {created}")
Created: True
>>> created = client.get_or_create_collection("products", dimension=128)
>>> print(f"Created: {created}")
Created: False
```

---

#### `describe_collection()`

Get detailed collection information.

```python
info = client.describe_collection(collection_name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |

**Returns:** `dict`

**Example:**
```python
>>> info = client.describe_collection("products")
>>> print(info)
{
    'name': 'products',
    'status': 'READY',
    'vectors_count': 1000,
    'indexed_vectors_count': 1000,
    'dimension': 128,
    'distance_metric': 'COSINE'
}
```

---

### Vector 0perations

#### `upsert()`

Insert or update a single vector.

```python
client.upsert(
    collection_name="products",
    id=0,
    vector=[0.1, 0.2, 0.3, ...],
    payload={"name": "Widget", "price": 29.99}
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Target collection |
| `id` | int | Vector ID |
| `vector` | list[float] \| np.ndarray | Vector data |
| `payload` | dict | Optional metadata |

**Returns:** `None` - upserts are immediately consistent and visible to subsequent operations

**Example:**
```python
>>> client.upsert("products", id=42, vector=[0.1]*128, payload={"name": "Item"})
>>> # Verify insertion
>>> vector, payload = client.get("products", id=42)
>>> print(payload)
{'name': 'Item'}
```

---

#### `batch_upsert()`

Insert or update multiple vectors efficiently.

```python
client.batch_upsert(
    collection_name="products",
    ids=[1, 2, 3],
    vectors=[[0.1]*128, [0.2]*128, [0.3]*128],
    payloads=[{"i": 1}, {"i": 2}, {"i": 3}]
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Target collection |
| `ids` | list[int] | Vector IDs |
| `vectors` | list[list[float]] | Vector data |
| `payloads` | list[dict] | Optional metadata list |

**Returns:** `None`

**Example:**
```python
>>> # Insert 1000 vectors
>>> ids = list(range(1000))
>>> vectors = [[0.1 + i*0.001]*128 for i in range(1000)]
>>> payloads = [{"index": i} for i in range(1000)]
>>> client.batch_upsert("products", ids, vectors, payloads)
>>> print(client.count("products"))
1000
```

---

#### `get()`

Retrieve a vector by ID.

```python
vector, payload = client.get(collection_name="products", id=0)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |
| `id` | int | Vector ID |

**Returns:** `tuple[list[float], dict | None]`

**Example:**
```python
>>> vector, payload = client.get("products", id=0)
>>> print(f"Vector dims: {len(vector)}")
Vector dims: 128
>>> print(f"Payload: {payload}")
Payload: {'name': 'Widget', 'price': 29.99}
```

---

#### `get_many()`

Retrieve multiple vectors by their IDs.

```python
results = client.get_many(
    collection_name="products",
    ids=[0, 1, 2],
    with_vectors=True,
    with_payload=True
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection_name` | str | required | Collection |
| `ids` | list[int] | required | Vector IDs |
| `with_vectors` | bool | True | Include vectors |
| `with_payload` | bool | True | Include payloads |

**Returns:** `list[tuple[list[float] | None, dict | None]]`

**Example:**
```python
>>> results = client.get_many("products", ids=[0, 1, 2])
>>> for vec, payload in results:
...     print(f"Vector: {vec[:3]}..., Payload: {payload}")
Vector: [0.1, 0.1, 0.1]..., Payload: {'name': 'Widget'}
Vector: [0.2, 0.2, 0.2]..., Payload: {'i': 1}
Vector: [0.3, 0.3, 0.3]..., Payload: {'i': 2}
```

---

#### `delete()`

Delete a vector by ID.

```python
client.delete(collection_name="products", id=0)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |
| `id` | int | Vector ID |

**Returns:** `None`

---

#### `batch_delete()`

Delete multiple vectors by IDs.

```python
client.batch_delete(collection_name="products", ids=[1, 2, 3])
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |
| `ids` | list[int] | Vector IDs to delete |

**Returns:** `None`

---

### Search operations

#### `search()`

Search for similar vectors with optional filtering.

```python
results = client.search(
    collection_name="products",
    query=[0.1, 0.2, 0.3, ...],
    top_k=10,
    filter=None,
    with_payload=True,
    with_vectors=False
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection_name` | str | required | Collection |
| `query` | list[float] \| np.ndarray | required | Query vector |
| `top_k` | int | 10 | Number of results |
| `filter` | Filter \| str | None | Filter expression |
| `with_payload` | bool | False | Include payload |
| `with_vectors` | bool | False | Include vectors |

**Returns:** `list[SearchResult]`

**Example:**
```python
>>> results = client.search("products", query=[0.1]*128, top_k=3, with_payload=True)
>>> for r in results:
...     print(f"id={r.id}, score={r.score:.4f}, payload={r.payload}")
id=0, score=1.0000, payload={'name': 'Widget', 'price': 29.99}
id=1, score=1.0000, payload={'i': 1}
id=2, score=1.0000, payload={'i': 2}
```

---

#### `search()` with filter

Apply payload filters during search.

```python
from cortex import Filter, Field

# Create filter
filter = (
    Filter()
    .must(Field("category").eq("electronics"))
    .must(Field("price").lte(100))
)

results = client.search(
    "products",
    query=[0.1]*128,
    top_k=10,
    filter=filter,
    with_payload=True
)
```

**Example:**
```python
>>> filter = Filter().must(Field("category").eq("electronics"))
>>> print(filter.to_json())
{"category": "electronics"}
>>> results = client.search("products", [0.1]*4, top_k=10, filter=filter)
>>> print(f"Found {len(results)} electronics items")
Found 3 electronics items
```

---

#### `search_filtered()`

Convenience method for filtered search.

```python
results = client.search_filtered(
    collection_name="products",
    query=[0.1]*128,
    filter=Filter().must(Field("category").eq("electronics")),
    top_k=10
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection |
| `query` | list[float] | Query vector |
| `filter` | Filter \| str | Filter (required) |
| `top_k` | int | Number of results |

**Returns:** `list[SearchResult]`

---

### Query and scroll

#### `count()`

Get vector count in collection.

```python
count = client.count(collection_name="products", exact=True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection_name` | str | required | Collection |
| `exact` | bool | True | Exact count |

**Returns:** `int`

**Example:**
```python
>>> client.count("products")
4
```

---

#### `get_vector_count()`

Alias for `count()`.

```python
count = client.get_vector_count(collection_name="products")
```

**Returns:** `int`

---

#### `scroll()`

Paginate through all vectors in a collection.

```python
records, next_cursor = client.scroll(
    collection_name="products",
    limit=100,
    cursor=None,
    with_vectors=False,
    with_payload=True
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection_name` | str | required | Collection |
| `limit` | int | 100 | Records per page |
| `cursor` | int | None | Starting ID (None = start) |
| `with_vectors` | bool | False | Include vectors |
| `with_payload` | bool | True | Include payloads |

**Returns:** `tuple[list[PointRecord], int | None]`

| Return | Type | Description |
|--------|------|-------------|
| records | list[PointRecord] | Retrieved records |
| next_cursor | int \| None | Next page cursor (None if done) |

**Example (iterate all):**
```python
>>> cursor = None
>>> all_records = []
>>> while True:
...     records, cursor = client.scroll("products", limit=100, cursor=cursor)
...     all_records.extend(records)
...     print(f"Retrieved {len(records)} records, cursor={cursor}")
...     if cursor is None:
...         break
Retrieved 4 records, cursor=None
>>> print(f"Total: {len(all_records)}")
Total: 4
```

---

#### `query()`

Retrieve entries by filter or IDs (no vector query).

```python
results = client.query(
    collection_name="products",
    filter=Filter().must(Field("category").eq("electronics")),
    ids=None,
    limit=100,
    skip=0,
    with_vectors=False
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection_name` | str | required | Collection |
| `filter` | Filter \| str | None | Filter expression |
| `ids` | list[int] | None | Specific IDs |
| `limit` | int | 100 | Max results |
| `skip` | int | 0 | Skip count |
| `with_vectors` | bool | False | Include vectors |

**Returns:** `list[PointRecord]`

**Example:**
```python
>>> # Query by IDs
>>> records = client.query("products", ids=[0, 1, 2])
>>> print(f"Found {len(records)} records")
Found 3 records

>>> # Query by filter
>>> f = Filter().must(Field("price").lte(50))
>>> records = client.query("products", filter=f, limit=10)
>>> for r in records:
...     print(r.payload)
```

---

### Statistics and monitoring

#### `get_stats()`

Get collection statistics.

```python
stats = client.get_stats(collection_name="products", safe=True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection_name` | str | required | Collection |
| `safe` | bool | True | Return None on error |

**Returns:** `CollectionStats | None`

**Example:**
```python
>>> stats = client.get_stats("products")
>>> print(f"Total: {stats.total_vectors}")
Total: 4
>>> print(f"Indexed: {stats.indexed_vectors}")
Indexed: 4
```

> [!NOTE]
> `storage_bytes`, `index_memory_bytes`, and `deleted_vectors` currently return 0.
> These metrics are not yet fully implemented in the server.

---

#### `get_state()`

Get collection state.

```python
state = client.get_state(collection_name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |

**Returns:** `CollectionState` (READY, LOADING, REBUILDING, ERROR)

**Example:**
```python
>>> state = client.get_state("products")
>>> print(state)
CollectionState.READY
```

> [!NOTE]
> The server currently always returns `READY`. Dynamic state tracking is not yet implemented.

---

### Maintenance Operations

#### `flush()`

Flush pending writes to storage.

```python
client.flush(collection_name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |

**Returns:** `None`

---

#### `save_snapshot()`

Save a snapshot of the collection.

```python
client.save_snapshot(collection_name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |

**Returns:** `None`

---

#### `load_snapshot()`

Load a previously saved snapshot.

```python
client.load_snapshot(collection_name="products")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `collection_name` | str | Collection name |

**Returns:** `None`

---

## Filter DSL

The Filter DSL provides a type-safe way to build filter expressions.

```python
from cortex import Filter, Field

# Import
from cortex.filters import Filter, Field  # Alternative import
```

### Operators

| Method | JSON Output | Description |
|--------|-------------|-------------|
| `Field("x").eq(val)` | `{"x": val}` | Equals |
| `Field("x").ne(val)` | `{"x": {"$ne": val}}` | Not equals |
| `Field("x").gt(val)` | `{"x": {"$gt": val}}` | Greater than |
| `Field("x").gte(val)` | `{"x": {"$gte": val}}` | Greater or equal |
| `Field("x").lt(val)` | `{"x": {"$lt": val}}` | Less than |
| `Field("x").lte(val)` | `{"x": {"$lte": val}}` | Less or equal |
| `Field("x").is_in([...])` | `{"x": {"$in": [...]}}` | In list |
| `Field("x").not_in([...])` | `{"x": {"$nin": [...]}}` | Not in list |
| `Field("x").range(gte=a, lte=b)` | `{"x": {"$gte": a, "$lte": b}}` | Range |
| `Field("x").is_null()` | `{"x": null}` | Is null |
| `Field("x").is_not_null()` | `{"x": {"$ne": null}}` | Is not null |

### Filter methods

| Method | Description |
|--------|-------------|
| `is_empty()` | Returns `True` if filter has no conditions |
| `to_dict()` | Convert to dictionary representation |
| `to_dict_or_none()` | Returns `None` if empty, dict otherwise |
| `to_json()` | Convert to compact JSON string (empty string if no conditions) |
| `to_json_or_none()` | Returns `None` if empty, JSON string otherwise |
| `copy()` | Create an independent copy of the filter |
| `clear()` | Remove all conditions from the filter |

### Utility features

```python
# String representation for debugging
f = Filter().must(Field("x").eq(1))
print(f)       # Filter({"x":1})
print(repr(f)) # Filter(must=1)

# Truthiness checks
if filter:  # True if filter has conditions
    results = client.search(..., filter=filter)

# Check if empty
if filter.is_empty():
    print("No filter applied")

# Create a copy
f2 = filter.copy()
f2.must(Field("y").eq(2))  # Original unchanged

# Clear all conditions
filter.clear()
```

### Combining filters

#### AND (must)

All conditions must match.

```python
filter = (
    Filter()
    .must(Field("category").eq("electronics"))
    .must(Field("price").lte(100))
)
# JSON: {"$and": [{"category": "electronics"}, {"price": {"$lte": 100}}]}
```

#### OR (should)

At least one condition must match.

```python
filter = (
    Filter()
    .should(Field("brand").eq("Apple"))
    .should(Field("brand").eq("Samsung"))
)
# JSON: {"$or": [{"brand": "Apple"}, {"brand": "Samsung"}]}
```

#### NOT (must_not)

Conditions must not match.

```python
filter = (
    Filter()
    .must(Field("category").eq("electronics"))
    .must_not(Field("discontinued").eq(True))
)
# JSON: {"$and": [{"category": "electronics"}, {"discontinued": {"$ne": true}}]}
```

### Using filters

#### With filter object

```python
from cortex.filters import Filter, Field

# Build filter
filter = Filter().must(Field("category").eq("electronics"))

# Search with filter and get payload/vectors
results = await client.search(
    "products",
    query=[0.1]*128,
    top_k=20,
    filter=filter,
    with_payload=True,   # Include payload in results
    with_vectors=True,   # Include vectors in results
)

for r in results:
    print(f"ID: {r.id}, Score: {r.score}, Payload: {r.payload}")
```

#### With JSON string

```python
# Alternative: pass JSON string directly
results = await client.search(
    "products",
    query=[0.1]*128,
    top_k=20,
    filter='{"category": "electronics"}',
)
```

### Examples

```python
# Electronics under $100, not discontinued
filter = (
    Filter()
    .must(Field("category").eq("electronics"))
    .must(Field("price").range(gte=10, lte=100))
    .must_not(Field("discontinued").eq(True))
)

# Books by specific authors with rating > 4
filter = (
    Filter()
    .must(Field("category").eq("books"))
    .must(Field("author").is_in(["King", "Rowling", "Martin"]))
    .must(Field("rating").gte(4.0))
)

# Filter by UUID/doc_id
filter = Filter().must(Field("doc_id").eq("960933dd-e7a6-4e08-b7e3-fe66ab55cb28"))

# Search with filter
results = client.search(
    "products",
    query=[0.1]*128,
    top_k=20,
    filter=filter,
    with_payload=True
)
```

---

## Models reference

### SearchResult

Returned by `search()` methods.

```python
class SearchResult:
    id: int           # Vector ID
    score: float      # Similarity/distance score
    payload: dict     # Metadata (if with_payload=True)
    vector: list      # Vector data (if with_vectors=True)
    
    # Aliases
    point_id: int     # Same as id
    distance: float   # Same as score
```

**Example:**
```python
>>> result = results[0]
>>> print(f"ID: {result.id}")
ID: 0
>>> print(f"Score: {result.score}")
Score: 1.0
>>> print(f"Same as: {result.point_id}, {result.distance}")
Same as: 0, 1.0
```

---

### PointRecord

Returned by `scroll()` and `query()` methods.

```python
class PointRecord:
    id: int                    # Vector ID
    vector: list[float] | None # Vector data
    payload: dict | None       # Metadata
```

---

### PointStruct

Used for creating points.

```python
class PointStruct:
    id: int           # Vector ID
    vector: list      # Vector data
    payload: dict     # Metadata
```

---

### CollectionStats

Returned by `get_stats()`.

```python
class CollectionStats:
    total_vectors: int       # Total vectors
    indexed_vectors: int     # Indexed vectors
    deleted_vectors: int     # Deleted (tombstoned)
    storage_bytes: int       # Storage size
    index_memory_bytes: int  # Index memory
```

---

### CollectionState

Returned by `get_state()`.

```python
class CollectionState(Enum):
    READY = "READY"           # Ready for operations
    LOADING = "LOADING"       # Loading data
    REBUILDING = "REBUILDING" # Rebuilding index
    ERROR = "ERROR"           # Error state
```

---

### DistanceMetric

Used in `create_collection()`.

```python
class DistanceMetric(Enum):
    COSINE = "COSINE"       # Cosine similarity (higher = more similar)
    EUCLIDEAN = "EUCLIDEAN" # L2 distance (lower = more similar)
    DOT = "DOT"             # Dot product (higher = more similar)
```

---

## Error handling

```python
from cortex import CortexError

try:
    vector, payload = client.get("products", id=999999)
except CortexError as e:
    print(f"Cortex Error {e.code}: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### CortexError

```python
class CortexError(Exception):
    code: int      # Error code (negative = error)
    message: str   # Error message
```

---

## Async client

The async client provides the same API with `async/await` syntax.

```python
import asyncio
from cortex import AsyncCortexClient

async def main():
    async with AsyncCortexClient("localhost:50051") as client:
        # All methods are async
        await client.create_collection("demo", dimension=128)
        await client.upsert("demo", id=0, vector=[0.1]*128)
        
        results = await client.search("demo", [0.1]*128, top_k=5)
        
        await client.delete_collection("demo")

asyncio.run(main())
```

### High-throughput ingestion

For high-throughput ingestion, use `batch_upsert()` instead of individual `upsert()` calls:

```python
async with AsyncCortexClient("localhost:50051") as client:
    # Single upserts are immediate and consistent
    await client.upsert("collection", id=0, vector=[0.1]*128)
    count = await client.get_vector_count("collection")  # Returns 1 immediately
    
    # For bulk ingestion, use batch_upsert for better throughput
    ids = list(range(1000))
    vectors = [[0.1]*128 for _ in range(1000)]
    await client.batch_upsert("collection", ids, vectors)
```

> **Note:** Single `upsert()` calls use direct gRPC for immediate consistency. Use `batch_upsert()` for
> high-volume ingestion.

---

## Best practices

### Use context managers

```python
# Good - automatic cleanup
with CortexClient("localhost:50051") as client:
    ...

# Good - async version
async with AsyncCortexClient("localhost:50051") as client:
    ...
```

### Batch operations

```python
# Good - batch insert
client.batch_upsert("collection", ids, vectors, payloads)

# Avoid - individual inserts in loop
for i, v in enumerate(vectors):
    client.upsert("collection", id=i, vector=v)  # Slow!
```

### Use async for high throughput

```python
# For high-throughput scenarios, use async client with batch_upsert
async with AsyncCortexClient("localhost:50051") as client:
    await client.batch_upsert("collection", ids, vectors, payloads)
```

### Normalize vectors for COSINE

```python
import numpy as np

def normalize(v):
    return v / np.linalg.norm(v)

# Normalize before insert for COSINE distance
vector = normalize(np.array([0.1, 0.2, 0.3]))
client.upsert("collection", id=0, vector=vector.tolist())
```

### Filter early

```python
# Good - filter in search
filter = Filter().must(Field("category").eq("electronics"))
results = client.search("products", query, top_k=10, filter=filter)

# Avoid - filter after search
results = client.search("products", query, top_k=1000)
filtered = [r for r in results if r.payload["category"] == "electronics"]
```

---

## Complete method reference

### Implemented methods (25)

| Category | Method | Description |
|----------|--------|-------------|
| **Connection** | `connect()` | Connect to server |
| | `close()` | Close connection |
| | `health_check()` | Server health/version |
| **Collection** | `create_collection()` | Create new collection |
| | `delete_collection()` | Delete collection |
| | `has_collection()` | Check if exists |
| | `open_collection()` | Open collection |
| | `close_collection()` | Close collection |
| | `recreate_collection()` | Delete + create |
| | `get_or_create_collection()` | Idempotent create |
| | `describe_collection()` | Get collection info |
| **Vector** | `upsert()` | Insert/update single |
| | `batch_upsert()` | Batch insert/update |
| | `get()` | Get by ID |
| | `get_many()` | Get multiple by IDs |
| | `delete()` | Delete by ID |
| | `batch_delete()` | Batch delete |
| **Search** | `search()` | Vector similarity search |
| | `search_filtered()` | Search with filter |
| **Query** | `query()` | Query by filter/IDs |
| | `scroll()` | Paginate all vectors |
| | `count()` | Vector count |
| | `get_vector_count()` | Alias for count |
| **Stats** | `get_stats()` | Collection statistics |
| | `get_state()` | Collection state |
| **Maintenance** | `flush()` | Flush writes |
| | `save_snapshot()` | Save snapshot |
| | `load_snapshot()` | Load snapshot |

---

## Server limitations

The following methods are defined in the client API but *require server-side implementation*. Calling these methods will raise `NotImplementedError`.

> [!CAUTION]
> These methods are part of the client interface for API parity with Qdrant/Milvus but are not yet functional.

### Maintenance operations (Server Error -1)

| Method | Status | Notes |
|--------|--------|-------|
| `optimize()` | ⚠️ Server Error | RPC exists, server returns -1 |
| `compact()` | ⚠️ Server Error | Alias for optimize |
| `rebuild_index()` | ⚠️ Server Error | RPC exists, server returns -1 |

### Payload operations (not yet implemented)

| Method | Status |
|--------|--------|
| `set_payload()` | ❌ NotImplementedError |
| `delete_payload()` | ❌ NotImplementedError |
| `clear_payload()` | ❌ NotImplementedError |

### Index operations (not yet implemented)

| Method | Status |
|--------|--------|
| `create_payload_index()` | ❌ NotImplementedError |
| `delete_payload_index()` | ❌ NotImplementedError |
| `create_index()` | ❌ NotImplementedError |
| `drop_index()` | ❌ NotImplementedError |
| `list_indexes()` | ❌ NotImplementedError |
| `describe_index()` | ❌ NotImplementedError |

### Snapshot operations (Extended - not yet implemented)

| Method | Status | Notes |
|--------|--------|-------|
| `save_snapshot()` | ✅ Working | Basic save works |
| `load_snapshot()` | ✅ Working | Basic load works |
| `list_snapshots()` | ❌ NotImplementedError | Extended API |
| `create_snapshot()` | ❌ NotImplementedError | Extended API |
| `delete_snapshot()` | ❌ NotImplementedError | Extended API |
| `recover_snapshot()` | ❌ NotImplementedError | Extended API |

### Alias operations (not yet implemented)

| Method | Status |
|--------|--------|
| `create_alias()` | ❌ NotImplementedError |
| `drop_alias()` | ❌ NotImplementedError |
| `alter_alias()` | ❌ NotImplementedError |
| `list_aliases()` | ❌ NotImplementedError |
| `describe_alias()` | ❌ NotImplementedError |

### Partition operations (not yet implemented)

| Method | Status |
|--------|--------|
| `create_partition()` | ❌ NotImplementedError |
| `drop_partition()` | ❌ NotImplementedError |
| `has_partition()` | ❌ NotImplementedError |
| `list_partitions()` | ❌ NotImplementedError |
| `load_partitions()` | ❌ NotImplementedError |
| `release_partitions()` | ❌ NotImplementedError |

### Database operations (not yet implemented)

| Method | Status |
|--------|--------|
| `create_database()` | ❌ NotImplementedError |
| `drop_database()` | ❌ NotImplementedError |
| `list_databases()` | ❌ NotImplementedError |
| `use_database()` | ❌ NotImplementedError |
| `describe_database()` | ❌ NotImplementedError |

### User and role management (not yet implemented)

| Method | Status |
|--------|--------|
| `create_user()` | ❌ NotImplementedError |
| `drop_user()` | ❌ NotImplementedError |
| `list_users()` | ❌ NotImplementedError |
| `describe_user()` | ❌ NotImplementedError |
| `update_password()` | ❌ NotImplementedError |
| `create_role()` | ❌ NotImplementedError |
| `drop_role()` | ❌ NotImplementedError |
| `list_roles()` | ❌ NotImplementedError |
| `describe_role()` | ❌ NotImplementedError |
| `grant_role()` | ❌ NotImplementedError |
| `revoke_role()` | ❌ NotImplementedError |
| `grant_privilege()` | ❌ NotImplementedError |
| `revoke_privilege()` | ❌ NotImplementedError |

### Advanced search and cluster (not yet implemented)

| Method | Status |
|--------|--------|
| `hybrid_search()` | ❌ NotImplementedError |
| `cluster_status()` | ❌ NotImplementedError |

---

**© 2026 Actian Corporation. All rights reserved.**

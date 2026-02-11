<p align="center">
  <img height="100" alt="Actian" src="https://www.actian.com/wp-content/themes/hcl-actian/images/actian-logo.svg">
  &nbsp;
</p>

<p align="center">
    <b>Actian VectorAI DB</b>
</p>

# Actian VectorAI DB and Python client

The Actian VectorAI DB and Python client. Please review the [Known Issues](#-known-issues) section before deploying.

### Supported platforms

- The VectorAI DB Docker image is currently supported only on Linux/amd64 (x86_64).
- The Python client package is supported on all major platforms (Windows, macOS, and Linux).

## Features

- 🚀 **Async & Sync clients** - Full async/await support with `AsyncCortexClient`
- 🔐 **Persistent storage** - Production-grade data persistence
- 🔍 **Type-safe Filter DSL** - Fluent API for payload filtering
- ⚡ **Smart Batching** - Automatic request batching for high throughput
- 📦 **Pydantic models** - Type hints and validation throughout
- 🎯 **gRPC transport** - High-performance communication

## 📥 Docker container installation

If you don't have the .tar image, see the DockerHub version below.

Load the container archive into your container environment:

```bash
docker image load -i Actian_VectorAI_DB_Beta.tar
```

### Container ports and volumes

The container exposes port `50051` and stores its logs and persisted collections in the `/data` directory, which you should map to a host directory to persist data outside the container.

### Deploy container with Docker run

To deploy the container using `docker run`:

```bash
docker run -d --name vectoraidb -v ./data:/data -p 50051:50051 localhost/actian/vectoraidb:1.0b
```

### Deploy container with Docker compose

To deploy the container using `docker compose`, create a `docker-compose.yml` file with this service definition and start it with `docker compose up`.

```yaml
services:
  vectoraidb:
    image: localhost/actian/vectoraidb:1.0b
    container_name: vectoraidb
    ports:
      - "50051:50051"
    volumes:
      - ./data:/data
    restart: unless-stopped
    stop_grace_period: 2m
```

_Note: Collections and logs are persisted under the mounted /data directory_

### Pull from DockerHub

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) installed.

2. Clone this repository.

3. Start the database:

```bash
   docker compose up
```

   Or run in the background:

```bash
   docker compose up -d
```

  The database will be available at `localhost:50051`.

4. To stop the container:

```bash
   docker compose down
```

### Examine container logs

The VectorAI DB server writes useful informational messages and errors to its log. These logs are often the best place to start when diagnosing failed requests or unexpected behavior.

You can access the server logs in two ways:

- Use `docker logs <container-name>` to stream or inspect the container logs directly.
- Read the log file at `/data/vde.log` from the host directory you mapped to `/data` when starting the container.

## 📥 Install Python client

Install the Python client with pip:

```bash
pip install actiancortex-0.1.0b1-py3-none-any.whl
```

**_For detailed API documentation, see [docs/api.md](./docs/api.md)._**

## 🚀 Quickstart

Sync client and async client quickstarts are available.

### Sync client

```python
from cortex import CortexClient, DistanceMetric

with CortexClient("localhost:50051") as client:
    # Health check
    version, uptime = client.health_check()
    print(f"Connected to {version}")

    # Create collection
    client.create_collection(
        name="products",
        dimension=128,
        distance_metric=DistanceMetric.COSINE,
    )

    # Insert vectors
    client.upsert("products", id=0, vector=[0.1]*128, payload={"name": "Product A"})

    # Batch insert
    client.batch_upsert(
        "products",
        ids=[1, 2, 3],
        vectors=[[0.2]*128, [0.3]*128, [0.4]*128],
        payloads=[{"name": f"Product {i}"} for i in [1, 2, 3]],
    )

    # Search
    results = client.search("products", query=[0.1]*128, top_k=5)
    for r in results:
        print(f"ID: {r.id}, Score: {r.score}")

    # Cleanup
    client.delete_collection("products")
```

### Async client

```python
import asyncio
from cortex import AsyncCortexClient

async def main():
    async with AsyncCortexClient("localhost:50051") as client:
        # All methods are async
        await client.create_collection("demo", 128)
        await client.upsert("demo", id=0, vector=[0.1]*128)
        results = await client.search("demo", [0.1]*128, top_k=5)
        await client.delete_collection("demo")

asyncio.run(main())
```

## 📚 Core API

### Collection management

| Method                                      | Description              |
| ------------------------------------------- | ------------------------ |
| `create_collection(name, dimension, ...)`   | Create new collection    |
| `delete_collection(name)`                   | Delete collection        |
| `has_collection(name)`                      | Check if exists          |
| `collection_exists(name)`                   | Alias for has_collection |
| `recreate_collection(name, dimension, ...)` | Delete and recreate      |
| `open_collection(name)`                     | Open for operations      |
| `close_collection(name)`                    | Close collection         |

### Vector operations

| Method                                             | Description                 |
| -------------------------------------------------- | --------------------------- |
| `upsert(collection, id, vector, payload)`          | Insert/update single vector |
| `batch_upsert(collection, ids, vectors, payloads)` | Batch insert                |
| `get(collection, id)`                              | Get vector by ID            |
| `get_many(collection, ids)`                        | Get multiple vectors        |
| `retrieve(collection, ids)`                        | Alias for get_many          |
| `delete(collection, id)`                           | Delete vector               |
| `count(collection)`                                | Get vector count            |
| `scroll(collection, limit, cursor)`                | Paginate through vectors    |

### Search operations

| Method                                              | Description     |
| --------------------------------------------------- | --------------- |
| `search(collection, query, top_k)`                  | K-NN search     |
| `search_filtered(collection, query, filter, top_k)` | Filtered search |

### Maintenance

| Method                  | Description         |
| ----------------------- | ------------------- |
| `flush(collection)`     | Flush to disk       |
| `get_stats(collection)` | Get statistics      |
| `health_check()`        | Check server health |

## 🔍 Filter DSL

Type-safe filter building for payload queries:

```python
from cortex.filters import Filter, Field

# Simple conditions
filter = Filter().must(Field("category").eq("electronics"))

# Range conditions
filter = Filter().must(Field("price").range(gte=100, lte=500))

# Combined conditions
filter = (
    Filter()
    .must(Field("category").eq("electronics"))
    .must(Field("price").lte(500))
    .must_not(Field("deleted").eq(True))
)

# Use in search
results = client.search_filtered("products", query_vector, filter, top_k=10)
```

## 📖 Examples

```bash
# Run examples
PYTHONPATH=. .venv/bin/python examples/quick_start.py
PYTHONPATH=. .venv/bin/python examples/async_example.py
PYTHONPATH=. .venv/bin/python examples/batch_upsert.py
```

## 📊 Storage

Cortex uses persistent storage as the default backend. This provides:

- ✅ Production-grade persistence
- ✅ Transactional safety
- ✅ High-performance I/O

## 🔧 Configuration

### HNSW parameters

```python
client.create_collection(
    name="vectors",
    dimension=128,
    hnsw_m=32,              # Edges per node (default: 16)
    hnsw_ef_construct=256,  # Build-time neighbors (default: 200)
    hnsw_ef_search=100,     # Search-time neighbors (default: 50)
)
```

### Distance metrics

- `COSINE` - Cosine similarity (default, recommended for normalized vectors)
- `EUCLIDEAN` - L2 distance
- `DOT` - Dot product

## 📦 Dependencies

- `grpcio>=1.68.1` - gRPC transport
- `protobuf>=5.29.2` - Protocol buffers
- `numpy>=2.2.1` - Vector operations
- `pydantic>=2.10.4` - Data validation

## 🐞 Known issues

- CRTX-202: Closing or deleting collections while read/write operations are in progress is not supported.
- CRTX-232: scroll API uses the term cursor to indicate the offset.
- CRTX-233: get_many API does not return the vector IDs.

## 📄 License

Proprietary - Actian Corporation

---

<p align="center">
  <b>Copyright © 2025-2026 Actian Corporation. All Rights Reserved.</b>
</p>

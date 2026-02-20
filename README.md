<p align="center">
  <img height="100" alt="Actian" src="https://www.actian.com/wp-content/themes/hcl-actian/images/actian-logo.svg">
  &nbsp;
</p>

<p align="center">
    <b>Actian VectorAI DB - Hackathon Quick Start</b>
</p>

# What is VectorAI DB?

**VectorAI DB is a vector database** - a specialized database for AI applications that need to search by meaning, not just keywords.

**Think of it like this:**
- Regular database: "Find products named 'laptop'"
- Vector database: "Find products similar to 'portable computer for students'"

**Common use cases:**
- **RAG (Retrieval-Augmented Generation)**: Build ChatGPT-style chatbots with your own data
- **Semantic search**: Search by meaning ("cheap gaming laptop" finds "affordable gaming computer")
- **Recommendation engines**: "Find songs similar to this one"
- **Image search**: "Find images that look like this"
- **Anomaly detection**: "Find patterns that don't match normal behavior"

**What makes VectorAI DB different:**
- Runs on your laptop (not just cloud)
- Works offline (no internet required after setup)
- Fast (sub-40ms search)
- Production-ready (persistent storage, transactional safety)

---

## Supported Platforms

- **VectorAI DB Docker image**: Fully supported on Linux/amd64 (x86_64) and works on Apple Silicon machines using Docker Desktop
- **Python client**: Supported on all major platforms (Windows, macOS, and Linux)

---

# 5-Minute Setup

## What You Need

- **Docker** ([Install Docker](https://docs.docker.com/get-docker/))
- **Python 3.12+** ([Install Python](https://www.python.org/downloads/))
- **An embedding model** (we'll show you how below)

**Mac users with Apple Silicon:** Docker Desktop handles everything automatically

---

## Step 1: Start the Database (2 minutes)

```bash
# Clone this repo
git clone <repo-url>
cd actian-vectorai-db

# Start the database
docker compose up -d
```

**Database is now running at `localhost:50051`**

To check logs:
```bash
docker logs vectoraidb
```

To stop:
```bash
docker compose down
```

---

## Step 2: Install Python Client (1 minute)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Mac/Linux
# OR
.venv\Scripts\activate     # Windows

# Install client
pip install actiancortex-0.1.0b1-py3-none-any.whl
```

---

## Step 3: Your First Query (2 minutes)

**Important:** VectorAI DB does NOT include an embedding model. You need to bring your own.

**For hackathons, we recommend `sentence-transformers`** (free, runs locally):

```bash
pip install sentence-transformers
```

**Basic example:**

```python
from cortex import CortexClient
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

# Connect to database
with CortexClient("localhost:50051") as client:
    # Create collection
    client.create_collection(name="demo", dimension=384)
    
    # Add some data
    texts = ["I love pizza", "Pizza is delicious", "I hate broccoli"]
    embeddings = model.encode(texts)
    
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        client.upsert("demo", id=i, vector=embedding.tolist(), payload={"text": text})
    
    # Search
    query = "I enjoy eating pizza"
    query_embedding = model.encode(query)
    results = client.search("demo", query=query_embedding.tolist(), top_k=2)
    
    for result in results:
        print(f"Match: {result.payload['text']} (score: {result.score:.3f})")
    
    # Cleanup
    client.delete_collection("demo")
```

**You just performed semantic search.** The query "I enjoy eating pizza" matched "I love pizza" even though they use different words.

---

# What Can I Build?

## RAG Chatbot
Build a chatbot that answers questions about YOUR documents (PDFs, docs, web pages).

**Example:** "Build a chatbot that knows everything about my university's course catalog"

**How it works:**
1. Split documents into chunks
2. Convert chunks to embeddings
3. Store in VectorAI DB
4. When user asks question → search for relevant chunks → send to LLM

---

## Smart Search Engine
Search by meaning, not keywords.

**Example:** "Search recipes by ingredients and cooking style"
- User searches: "quick healthy breakfast"
- Finds: "5-minute protein smoothie", "easy oatmeal bowl"

**How it works:**
1. Convert product descriptions to embeddings
2. Store in VectorAI DB
3. Search with user query embedding

---

## Recommendation System
"Find items similar to this one"

**Example:** "Music recommendation based on listening history"
- User likes: "Bohemian Rhapsody"
- Recommends: Similar songs by mood, tempo, genre

**How it works:**
1. Represent items as embeddings (audio features, user behavior, etc.)
2. Store in VectorAI DB
3. Search for nearest neighbors

---

## Anomaly Detection
Find patterns that don't match normal behavior.

**Example:** "Detect unusual network traffic or fraud patterns"

**How it works:**
1. Represent normal behavior as embeddings
2. Store in VectorAI DB
3. Compare new data → flag outliers

---

# Common Questions

## What languages are supported?

**Currently: Python only.** The official Python client (`actiancortex`) is the only supported SDK at this time.

**Using other languages?** 

Advanced users can connect via:
- **gRPC clients**
- **MCP (Model Context Protocol)** - for integration with Claude and other AI assistants

---

## What embedding models can I use?

**Local (free, runs on your laptop):**
- `sentence-transformers` - Recommended for hackathons (easy setup)
- OpenAI embeddings - Requires API key

**Example:**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
embeddings = model.encode(["your text here"])
```

**Important:** Match your collection dimension to your embedding model's output dimension!

---

## What's the difference between this and Pinecone?

| Feature | VectorAI DB | Pinecone |
|---------|-------------|----------|
| **Runs locally** | Yes | No (Cloud-only) |
| **Offline mode** | Yes | No (Requires internet) |
| **Speed** | <40ms local | Network latency |
| **Data stays on your machine** | Yes | No (Uploads to cloud) |

---

# Troubleshooting

## Port 50051 is already in use

**Error:** `Address already in use` or `port is already allocated`

**Fix:**
```bash
# Find what's using port 50051
lsof -i :50051  # Mac/Linux
netstat -ano | findstr :50051  # Windows

# Kill the process OR change the port
```

**To use a different port:**

Edit `docker-compose.yml`:
```yaml
ports:
  - "50052:50051"  # Change 50052 to any available port
```

Then connect with:
```python
client = CortexClient("localhost:50052")
```

---

## Docker container won't start

**Check Docker is running:**
```bash
docker ps
```

**View logs:**
```bash
docker logs vectoraidb
```

**Common fixes:**
- Restart Docker Desktop
- Run `docker compose down` then `docker compose up -d`
- Check you have enough disk space

---

## Dimension mismatch error

**Error:** `dimension mismatch: expected X, got Y`

**Cause:** Your embedding model dimensions don't match your collection dimension.

**Fix:**
```python
# Check your model's output dimension
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("test")
print(len(embedding))  # → 384

# Create collection with matching dimension
client.create_collection("demo", dimension=384)  # Must match!
```

---

## MacBook error (but it still works?)

**Known issue:** Some MacBooks show gRPC connection warnings but the database works anyway.

**If you see warnings but queries succeed → ignore the warnings.** This is a known issue we're fixing.

---

## Raspberry Pi doesn't work

**Known limitation:** VectorAI DB doesn't currently support Raspberry Pi.

**Workaround:** Run on your laptop and connect Pi over network (advanced).

---

## Version conflicts / package errors

**Error:** `ImportError` or `ModuleNotFoundError`

**Fix:**
```bash
# Make sure you're in virtual environment
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Reinstall clean
pip install --force-reinstall actiancortex-0.1.0b1-py3-none-any.whl
```

---

# API Quick Reference

## Collections (like database tables)

```python
# Create
client.create_collection("products", dimension=384)

# Check if exists
client.has_collection("products")  # → True/False

# Delete
client.delete_collection("products")

# Recreate (delete + create)
client.recreate_collection("products", dimension=384)
```

---

## Add Vectors

```python
# Single insert
client.upsert("products", id=0, vector=[0.1]*384, payload={"name": "Item A"})

# Batch insert (faster!)
client.batch_upsert(
    "products",
    ids=[1, 2, 3],
    vectors=[[0.2]*384, [0.3]*384, [0.4]*384],
    payloads=[{"name": f"Item {i}"} for i in range(1, 4)]
)
```

---

## Search

```python
# Simple search
results = client.search("products", query=[0.1]*384, top_k=5)

for result in results:
    print(f"ID: {result.id}, Score: {result.score}")
    print(f"Data: {result.payload}")

# Search with filters
from cortex.filters import Filter, Field

filter = Filter().must(Field("category").eq("electronics"))
results = client.search_filtered("products", query=[0.1]*384, filter=filter, top_k=5)
```

---

## Get / Delete

```python
# Get by ID
item = client.get("products", id=0)

# Get multiple
items = client.get_many("products", ids=[0, 1, 2])

# Delete
client.delete("products", id=0)

# Count vectors
count = client.count("products")
```

---

# Get Help

**Documentation:** [Full API docs](./docs/api.md)

**Examples:** Check the `examples/` folder:
- `examples/rag/` - Full RAG chatbot
- `examples/quick_start.py` - Basic usage
- `examples/semantic_search.py` - Search with filters

**Need support?** Contact us through the channels provided in your beta access email.

---

# Limits & Known Issues

**Current limitations:**
- Don't close collections while operations are in progress (will be fixed)
- Raspberry Pi not supported yet
- Some MacBooks show gRPC warnings (ignorable)

**Performance:**
- Local queries: <40ms typically
- Handles millions of vectors
- Limited by your laptop's RAM and disk

---

<p align="center">
  Copyright © 2025-2026 Actian Corporation. All Rights Reserved.
</p>

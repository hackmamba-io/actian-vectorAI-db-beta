# 🚀 End-to-End RAG Example

This example demonstrates how **Actian VectorAI DB** integrates into a complete **Retrieval-Augmented Generation (RAG)** application. Perfect for developers new to vector databases!

## 🎯 What You'll Learn

This example shows the **complete workflow** of a RAG application:

1. **📄 Document Processing** - Loading and chunking text into manageable pieces
2. **🧠 Embedding Generation** - Converting text to vectors using a real ML model
3. **💾 Vector Storage** - Storing embeddings in VectorAI DB with metadata
4. **🔍 Query Processing** - Converting user questions into embeddings
5. **🔎 Semantic Search** - Finding relevant context using vector similarity
6. **✨ Answer Generation** - Using retrieved context to generate accurate answers

## 🏗️ How It Works

```
User Query
    ↓
[1] Convert query to embedding
    ↓
[2] Search VectorAI DB for similar vectors
    ↓
[3] Retrieve relevant text chunks
    ↓
[4] Generate answer using context
    ↓
Answer to User
```

## 📦 Installation

### Prerequisites

1. **VectorAI DB Running:**
   ```bash
   docker compose up -d
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r examples/rag/requirements.txt
   ```

   Or install manually:
   ```bash
   pip install sentence-transformers openai
   ```

## 🧪 Quick Test

Before running the full example, verify your setup:

```bash
python examples/rag/test_rag.py
```

This checks:
- ✅ Python version
- ✅ VectorAI DB is running
- ✅ Dependencies installed
- ✅ Database connection works

## 🚀 Usage

### Local Mode (No API Key Required)

Run without an LLM - just demonstrates the retrieval part:

```bash
python examples/rag/rag_example.py --local
```

### With OpenAI (Recommended)

For full RAG with answer generation:

```bash
export OPENAI_API_KEY="your-api-key-here"  # Linux/macOS
# OR
set OPENAI_API_KEY=your-api-key-here       # Windows CMD
# OR  
$env:OPENAI_API_KEY="your-api-key-here"    # Windows PowerShell

python examples/rag/rag_example.py
```

### Custom Server

```bash
python examples/rag/rag_example.py --server your-host:50051
```

## 📖 Example Output

```
🚀 End-to-End RAG Example with Actian VectorAI DB
======================================================================

📥 Step 1: Loading embedding model...
   ✓ Model loaded: all-MiniLM-L6-v2 (384 dimensions)

🔌 Step 2: Connecting to VectorAI DB at localhost:50051...
   ✓ Connected to VectorAI DB v1.0

💾 Step 3: Creating collection 'rag_demo_a3f5c2e1'...
   ✓ Collection created with COSINE similarity

📄 Step 4: Processing and chunking documents...
   ✓ Created 12 text chunks

🧠 Step 5: Generating embeddings and storing in database...
   ✓ Stored 12 document chunks with embeddings
   ✓ Verified: 12 vectors in database

🔍 RAG Query Examples
======================================================================

Query 1: What are the key features of Actian VectorAI DB?
──────────────────────────────────────────────────────────────────────

  1️⃣  Embedding query...
  2️⃣  Retrieving relevant context from VectorAI DB...
     Found 3 relevant chunks:
       • Chunk 1 (similarity: 0.8542)
       • Chunk 2 (similarity: 0.7891)
       • Chunk 3 (similarity: 0.7234)
  3️⃣  Generating answer...

  📝 Answer:
     Actian VectorAI DB offers several key features including async and 
     sync clients with full async/await support, persistent storage for 
     production-grade data persistence, and a type-safe Filter DSL...
```

## 🧠 Understanding the Code

### 1. Document Chunking

```python
chunks = chunk_text(KNOWLEDGE_BASE)
# Splits long documents into overlapping chunks
# Preserves context at chunk boundaries
```

### 2. Embedding Generation

```python
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)
# Converts text to 384-dimensional vectors
```

### 3. Storing in VectorAI DB

```python
client.batch_upsert(COLLECTION, ids, vectors, payloads)
# Efficiently stores all vectors with metadata
```

### 4. Semantic Search

```python
query_embedding = model.encode([query])[0]
results = client.search(COLLECTION, query_embedding, top_k=3)
# Finds most similar vectors using cosine similarity
```

### 5. Context Retrieval & Answer Generation

```python
context_pieces = []
for result in results:
    _, payload = client.get(COLLECTION, result.id)
    context_pieces.append(payload["text"])
context = "\n\n".join(context_pieces)
answer = generate_answer_local(query, context)  # or generate_answer_openai()
```

## 💡 Real-World Applications

This pattern is used in:

- 📚 **Documentation Search** - Find relevant docs to answer user questions
- 🤖 **Customer Support Bots** - Answer questions using company knowledge base
- 📰 **Content Recommendations** - Find similar articles or products
- 🔬 **Research Tools** - Search scientific papers by semantic meaning
- 💼 **Enterprise Search** - Search internal documents by intent, not keywords

## 🎓 Why Vector Databases?

Traditional databases use **exact matching**:
```
Query: "How to start the database?"
Match: WHERE text = "How to start the database?"  ❌ No results
```

Vector databases use **semantic similarity**:
```
Query: "How to start the database?"
Finds: "To get started with Actian VectorAI DB..."  ✅ Relevant match!
```

## 🔧 Customization Tips

### Use Your Own Documents

Replace the `KNOWLEDGE_BASE` string with your own content:

```python
# Load from file
with open("my_docs.txt") as f:
    KNOWLEDGE_BASE = f.read()

# Load from multiple files
documents = []
for file in ["doc1.txt", "doc2.txt", "doc3.txt"]:
    with open(file) as f:
        documents.append(f.read())
KNOWLEDGE_BASE = "\n\n".join(documents)
```

### Try Different Embedding Models

```python
# Larger, more accurate model (768 dimensions)
model = SentenceTransformer('all-mpnet-base-v2')

# Multilingual model
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

### Adjust Chunk Size

```python
# Smaller chunks (more precise)
chunks = chunk_text(text, chunk_size=100, overlap=20)

# Larger chunks (more context)
chunks = chunk_text(text, chunk_size=500, overlap=100)
```

### Tune Search Parameters

```python
# Retrieve more context
results = client.search(COLLECTION, query_embedding, top_k=5)

# Better accuracy (slower)
client.create_collection(
    name=COLLECTION,
    dimension=DIMENSION,
    hnsw_ef_search=200  # Higher = more accurate
)
```

## 🤔 Common Questions

**Q: Do I need OpenAI?**  
A: No! Run with `--local` flag to see how the retrieval works. You can integrate any LLM (Anthropic, local models, etc.)

**Q: Why use embeddings?**  
A: Embeddings capture semantic meaning, allowing you to find relevant information even with different wording.

**Q: How big can my knowledge base be?**  
A: VectorAI DB can handle millions of vectors. The example uses a small KB for demonstration.

**Q: Can I use this in production?**  
A: Yes! VectorAI DB provides persistent storage and production-grade performance. Scale up your document corpus and you're good to go.

**Q: What about real-time updates?**  
A: Use `client.upsert()` to add/update documents in real-time as your knowledge base grows.

## 📚 Next Steps

1. **Try it with your own documents** - Replace the sample knowledge base
2. **Integrate with your LLM** - Swap OpenAI for Claude, Llama, etc.
3. **Add a web interface** - Build a simple Flask/FastAPI frontend
4. **Implement filters** - Use the Filter DSL to narrow search by metadata
5. **Scale up** - Load thousands of documents and test performance

## 🆘 Troubleshooting

**"Connection refused"**
```bash
# Make sure VectorAI DB is running
docker compose up -d
docker ps  # Should show vectoraidb container
```

**"Module not found: sentence_transformers"**
```bash
pip install sentence-transformers
```

**"OpenAI API error"**
```bash
# Check your API key is set
echo $OPENAI_API_KEY  # Linux/macOS
echo %OPENAI_API_KEY%  # Windows CMD

# Or run in local mode
python examples/rag/rag_example.py --local
```

## 🎉 Success!

You now understand how VectorAI DB integrates into AI applications! The same pattern applies to any RAG use case - just swap in your data and LLM of choice.

---

**Questions?** Open an issue or check the [main documentation](../README.md)

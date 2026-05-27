# Semantic Search: Quick Guide

## What is Semantic Search?

Finds results by **meaning** (not keywords). Understands intent and returns semantically similar content.

**Traditional:** "fix Python error" → finds exact words
**Semantic:** "fix Python error" → finds "resolve parsing issues"

---

## How It Works

1. **Text → Embeddings** (convert to number vectors)
2. **Store embeddings** in vector database
3. **Query → Embedding** (same conversion)
4. **Find similar** vectors using cosine similarity
5. **Return results** (by meaning match)

---

## Key Concepts

| Concept | Definition |
|---------|-----------|
| **Embeddings** | Numbers that represent text meaning |
| **Cosine Similarity** | Measures vector closeness (0 to 1) |
| **Chunking** | Split documents into pieces |
| **Vector DB** | Fast storage/search for embeddings |
| **RAG** | Semantic search + LLM for answers |

---

## Popular Tools

| Tool | Purpose |
|------|---------|
| `sentence-transformers` | Generate embeddings |
| `chromadb` | Vector database |
| `faiss` | Vector search |
| `langchain` | RAG pipelines |

**Install:** `pip install sentence-transformers chromadb`

---

## Quick Code

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

docs = ["Python is great", "ML is awesome", "Web dev rocks"]
embeddings = model.encode(docs)

query = "programming"
query_emb = model.encode(query)
similarity = cosine_similarity([query_emb], embeddings)[0]

print(f"Top match: {docs[similarity.argmax()]}")
```

---

## RAG Pipeline

```
User Query
    ↓
Semantic Search
    ↓
Retrieve Chunks
    ↓
LLM Generates Answer
```

Used in: AI assistants, chatbots, document search

---

## Key Takeaways

- Semantic = meaning-based search
- Embeddings = text as numbers
- Vector DB = fast similarity search
- RAG = retrieval + generation
- Hybrid search (keyword + semantic) works best
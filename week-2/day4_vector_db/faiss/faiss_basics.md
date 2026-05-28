# FAISS Basics

## What is FAISS?

FAISS (Facebook AI Similarity Search) is an open-source library for efficient vector similarity search.

It is mainly used in:

* RAG systems
* Semantic search
* AI chatbots
* Recommendation engines

---

# Core Idea

Text is converted into embeddings (vectors).

Example:

```python
"Hello world"
↓
[0.12, -0.44, 0.91, ...]
```

FAISS stores these vectors and quickly finds similar vectors.

---

# Workflow

```text
Documents
   ↓
Embeddings Model
   ↓
Vectors
   ↓
FAISS Index
   ↓
User Query
   ↓
Query Embedding
   ↓
Similarity Search
```

---

# Installation

```bash
pip install faiss-cpu sentence-transformers numpy
```

---

# Example Code

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

documents = [
    "FAISS is used for vector search",
    "Python is popular",
    "Machine learning is powerful"
]

model = SentenceTransformer('all-MiniLM-L6-v2')

embeddings = model.encode(documents)
embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

query = "What is vector search?"

query_embedding = model.encode([query])
query_embedding = np.array(query_embedding).astype("float32")

distances, indices = index.search(query_embedding, 2)

for i in indices[0]:
    print(documents[i])
```

---

# Important Index Types

| Index         | Description               |
| ------------- | ------------------------- |
| IndexFlatL2   | Exact similarity search   |
| IndexIVFFlat  | Faster approximate search |
| IndexHNSWFlat | Graph-based search        |

---

# Saving Index

```python
faiss.write_index(index, "index.faiss")
```

# Loading Index

```python
index = faiss.read_index("index.faiss")
```

---

# Advantages

* Fast similarity search
* Scales to millions of vectors
* GPU support
* Simple integration

---

# Limitations

* No advanced metadata filtering
* Not a complete database
* Manual persistence management

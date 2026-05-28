# Storing Embeddings

## What are Embeddings?

Embeddings are vector representations of data like text or images.

Example:

```python id="llk7m4"
"Hello AI"
↓
[0.12, -0.44, 0.91]
```

Embeddings capture semantic meaning.

---

# Why Store Embeddings?

Generating embeddings repeatedly is expensive and slow.

Storing embeddings helps:

* semantic search
* RAG systems
* chatbots
* recommendation systems

---

# Storage Options

| Method           | Example               |
| ---------------- | --------------------- |
| Memory           | Python lists          |
| Files            | JSON, NPY             |
| Vector Libraries | FAISS                 |
| Databases        | PostgreSQL + pgvector |
| Vector DBs       | Pinecone, Weaviate    |

---

# JSON Storage Example

```python id="2dbj0w"
import json

data = {
    "text": "FAISS basics",
    "embedding": [0.1, 0.2, 0.3]
}

with open("embeddings.json", "w") as f:
    json.dump(data, f)
```

---

# NumPy Storage Example

```python id="tm7fhk"
import numpy as np

embeddings = np.array([
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6]
])

np.save("embeddings.npy", embeddings)
```

---

# FAISS Example

```python id="lxy0w5"
import faiss
import numpy as np

embeddings = np.array([
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6]
]).astype("float32")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

faiss.write_index(index, "vectors.faiss")
```

---

# PostgreSQL + pgvector

```sql id="kew7ta"
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(384)
);
```

---

# Important Notes

* All vectors must have same dimensions
* Use float32 datatype
* Store metadata with embeddings

---

# RAG Flow

```text id="xg2bxy"
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Storage
   ↓
Similarity Search
```

---

# Advantages

* Fast retrieval
* Semantic understanding
* Better chatbot memory
* Efficient search systems

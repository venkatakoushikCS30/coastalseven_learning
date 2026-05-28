# Similarity Search

## What is Similarity Search?

Similarity search finds data that is semantically similar to a query.

Instead of matching exact keywords, it matches meaning.

---

# Workflow

```text id="7cg93f"
Documents
   ↓
Embeddings
   ↓
Store in FAISS
   ↓
User Query
   ↓
Query Embedding
   ↓
Similarity Search
```

---

# FAISS Example

```python id="d3ewju"
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

documents = [
    "FAISS enables vector search",
    "Machine learning powers AI",
    "React is a frontend library"
]

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(documents)

embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

query = "What is semantic search?"

query_embedding = model.encode([query])

query_embedding = np.array(query_embedding).astype("float32")

k = 2

distances, indices = index.search(query_embedding, k)

for i in indices[0]:
    print(documents[i])
```

---

# Important Concepts

## Embeddings

Numerical vector representation of text.

## L2 Distance

Measures distance between vectors.

## Cosine Similarity

Measures similarity angle between vectors.

---

# Common Use Cases

* RAG systems
* AI chatbots
* Semantic search
* Recommendation systems

---

# Advantages

* Fast search
* Semantic understanding
* Better than keyword search

---

# Limitations

* Requires embeddings
* Higher memory usage
* Computational cost

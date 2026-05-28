# Retrieval Pipelines

## What is a Retrieval Pipeline?

A retrieval pipeline retrieves relevant information before sending it to an LLM.

Used in:

* RAG systems
* AI chatbots
* semantic search

---

# Workflow

```text id="0lf6ij"
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Store
   ↓
User Query
   ↓
Similarity Search
   ↓
Relevant Chunks
   ↓
LLM Response
```

---

# Main Components

| Component    | Purpose                  |
| ------------ | ------------------------ |
| Loader       | Reads documents          |
| Chunker      | Splits text              |
| Embeddings   | Converts text to vectors |
| Vector Store | Stores embeddings        |
| Retriever    | Finds similar chunks     |
| LLM          | Generates answers        |

---

# Python Example

```python id="22mv26"
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

documents = [
    "FAISS supports vector search",
    "Django is a backend framework",
    "Embeddings represent semantic meaning"
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

distances, indices = index.search(query_embedding, 2)

for i in indices[0]:
    print(documents[i])
```

---

# Retrieval Types

| Type             | Description        |
| ---------------- | ------------------ |
| Dense Retrieval  | Embedding-based    |
| Sparse Retrieval | Keyword-based      |
| Hybrid Retrieval | Combined retrieval |

---

# Advantages

* Reduces hallucinations
* Uses external knowledge
* Enables semantic search

---

# Limitations

* Requires embeddings
* Retrieval may fail
* Large vector stores consume memory

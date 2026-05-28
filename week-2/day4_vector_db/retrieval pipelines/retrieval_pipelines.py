import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------
# STEP 1: Documents
# ---------------------------------------------------

documents = [
    "FAISS is used for vector similarity search",
    "Django is a Python backend framework",
    "React is used for frontend applications",
    "Embeddings represent semantic meaning",
    "Machine learning powers AI systems"
]

# ---------------------------------------------------
# STEP 2: Load Embedding Model
# ---------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------------------------------
# STEP 3: Create Embeddings
# ---------------------------------------------------

embeddings = model.encode(documents)

embeddings = np.array(embeddings).astype("float32")

# ---------------------------------------------------
# STEP 4: Create FAISS Index
# ---------------------------------------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

# ---------------------------------------------------
# STEP 5: Store Embeddings
# ---------------------------------------------------

index.add(embeddings)

# ---------------------------------------------------
# STEP 6: User Query
# ---------------------------------------------------

query = "What is semantic search?"

query_embedding = model.encode([query])

query_embedding = np.array(query_embedding).astype("float32")

# ---------------------------------------------------
# STEP 7: Similarity Search
# ---------------------------------------------------

k = 2

distances, indices = index.search(query_embedding, k)

# ---------------------------------------------------
# STEP 8: Retrieved Chunks
# ---------------------------------------------------

retrieved_chunks = []

for i in indices[0]:
    retrieved_chunks.append(documents[i])

# ---------------------------------------------------
# STEP 9: Final Context
# ---------------------------------------------------

context = "\n".join(retrieved_chunks)

print("\nRetrieved Context:\n")

print(context)
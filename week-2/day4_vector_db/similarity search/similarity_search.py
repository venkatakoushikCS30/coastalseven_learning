import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------
# STEP 1: Sample Documents
# ---------------------------------------------------

documents = [
    "FAISS is used for vector search",
    "Django is a backend framework",
    "React is used for frontend UI",
    "Machine learning powers AI systems",
    "Embeddings represent semantic meaning"
]

# ---------------------------------------------------
# STEP 2: Load Embedding Model
# ---------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------------------------------
# STEP 3: Generate Embeddings
# ---------------------------------------------------

embeddings = model.encode(documents)

# Convert to float32
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

k = 3

distances, indices = index.search(query_embedding, k)

# ---------------------------------------------------
# STEP 8: Display Results
# ---------------------------------------------------

print("\nQuery:", query)
print("\nMost Similar Results:\n")

for i in indices[0]:
    print(documents[i])
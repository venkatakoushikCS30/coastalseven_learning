import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------
# STEP 1: Sample Documents
# ---------------------------------------------------

documents = [
    "FAISS is used for vector similarity search",
    "Django is a backend framework",
    "React is used for frontend development",
    "Machine learning enables AI systems",
    "Embeddings convert text into vectors"
]

# ---------------------------------------------------
# STEP 2: Load Embedding Model
# ---------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------------------------------
# STEP 3: Generate Embeddings
# ---------------------------------------------------

embeddings = model.encode(documents)

# FAISS requires float32
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

print("Total stored embeddings:", index.ntotal)

# ---------------------------------------------------
# STEP 6: Save Index to Disk
# ---------------------------------------------------

faiss.write_index(index, "embeddings_index.faiss")

print("FAISS index saved successfully!")

# ---------------------------------------------------
# STEP 7: Load Saved Index
# ---------------------------------------------------

loaded_index = faiss.read_index("embeddings_index.faiss")

print("FAISS index loaded successfully!")

# ---------------------------------------------------
# STEP 8: Search Similar Embeddings
# ---------------------------------------------------

query = "What is vector search?"

# Convert query into embedding
query_embedding = model.encode([query])

query_embedding = np.array(query_embedding).astype("float32")

# Top K results
k = 2

distances, indices = loaded_index.search(query_embedding, k)

# ---------------------------------------------------
# STEP 9: Show Results
# ---------------------------------------------------

print("\nQuery:", query)
print("\nTop Matches:\n")

for i in indices[0]:
    print(documents[i])
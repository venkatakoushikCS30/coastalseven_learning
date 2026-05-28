import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Sample documents
documents = [
    "FAISS is a vector database library",
    "Python is a programming language",
    "Machine learning is amazing",
    "Django is used for backend development"
]

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert text to embeddings
embeddings = model.encode(documents)

# Convert to float32 (required by FAISS)
embeddings = np.array(embeddings).astype("float32")

# Get embedding dimension
dimension = embeddings.shape[1]

# Create FAISS index
index = faiss.IndexFlatL2(dimension)

# Add vectors to index
index.add(embeddings)

print("Total vectors in index:", index.ntotal)

# User query
query = "What is FAISS?"

# Convert query to embedding
query_vector = model.encode([query])
query_vector = np.array(query_vector).astype("float32")

# Search top 2 similar vectors
k = 2
distances, indices = index.search(query_vector, k)

print("\nTop Results:\n")

for i in indices[0]:
    print(documents[i])
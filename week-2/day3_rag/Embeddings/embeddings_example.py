from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Single text embedding
text = "Python is great for machine learning"
embedding = model.encode(text)

print(f"Text: {text}")
print(f"Embedding shape: {embedding.shape}")
print(f"Embedding: {embedding}")

# Multiple texts embedding
texts = [
    "Python is great",
    "Machine learning is awesome",
    "Deep learning models"
]

embeddings = model.encode(texts)
print(f"\nNumber of embeddings: {len(embeddings)}")
print(f"Each embedding dimension: {embeddings.shape[1]}")

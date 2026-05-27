import numpy as np

def embed(text: str) -> np.ndarray:
    """Fake embedding: bag-of-words over a tiny vocabulary."""
    vocab = ["fast", "quick", "dog", "cat", "pet", "animal", "slow", "pasta"]
    vec = np.array([1.0 if w in text.lower() else 0.0 for w in vocab])
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))                 

corpus = {
    "speedy dog tricks":    embed("fast quick dog"),
    "swift cat breed":      embed("fast quick cat"),
    "feline yoga poses":    embed("cat slow"),
    "pasta carbonara":      embed("pasta"),
    "animal care tips":     embed("pet animal"),
}

def semantic_search(query: str, top_k: int = 3) -> list[tuple[str, float]]:
    q_vec = embed(query)
    scores = [(doc, cosine_sim(q_vec, vec)) for doc, vec in corpus.items()]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]

query = "fast four-legged pet"
print(f"Query: '{query}'\n")
for doc, score in semantic_search(query):
    print(f"  {score:.2f}  {doc}")
def chunk_text(text, chunk_size=100):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


# Example usage
text = """Chunking is important in LLMs because they cannot process unlimited text.
We need to split large documents into smaller pieces."""

chunks = chunk_text(text, chunk_size=5)

for i, c in enumerate(chunks):
    print(f"\nChunk {i+1}:\n{c}")
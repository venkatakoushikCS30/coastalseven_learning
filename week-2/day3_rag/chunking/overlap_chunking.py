def overlapping_chunks(text, chunk_size=50, overlap=10):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
text = """Chunking is important in LLMs because they cannot process unlimited text.
We need to split large documents into smaller pieces."""

chunks = overlapping_chunks(text, chunk_size=5, overlap=2)

for i, c in enumerate(chunks):
    print(f"\nChunk {i+1}:\n{c}")
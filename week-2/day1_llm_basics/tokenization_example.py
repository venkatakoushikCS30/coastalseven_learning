from transformers import AutoTokenizer

# Load a tokenizer (same family style as LLMs)
tokenizer = AutoTokenizer.from_pretrained("gpt2")

text = "I love artificial intelligence"

# Convert text → tokens
tokens = tokenizer.tokenize(text)

# Convert text → token IDs
token_ids = tokenizer.encode(text)

print("Text:", text)
print("\nTokens:", tokens)
print("\nToken IDs:", token_ids)
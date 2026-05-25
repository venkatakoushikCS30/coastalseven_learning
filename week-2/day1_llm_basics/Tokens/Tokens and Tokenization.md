# Tokens in LLMs

---

## 1. What is a Token?

Small text chunk used by LLMs. Text breaks into tokens instead of full words.

Example: "I love AI" → ["I", " love", " AI"]

---

## 2. Types of Tokens

| Type | Example |
|------|---------|
| Word | "Hello" |
| Subword | "un", "break", "able" |
| Character | Single chars (rare) |

---

## 3. Key Rule: 1 Word ≠ 1 Token

- "unbelievable" → 3 tokens
- Common words split differently per model

---

## 4. Tokenization Flow

Text → Tokenizer → Token IDs → LLM → Output

---

## 5. Why Tokens Matter (3 Things)

**Cost:** APIs charge per token (input + output)

**Context Limit:** Max tokens limit (8K, 32K, 128K). Exceed it = response cut

**Speed:** More tokens = slower response

---

## 6. Token Estimation

- Sentence: 7-10 tokens
- Paragraph: 200-500 tokens
- Book: thousands

---

## 7. Autoregressive Generation

LLMs generate one token at a time:

"Hello" → "," → " how" → " can" → " I" → " help"

---

## 8. Input vs Output Tokens

| Type | What |
|------|------|
| Input | Your prompt |
| Output | Model response |
| Cost | Input + Output |

---

## 9. Common Mistakes

- Tokens ≠ words (wrong!)
- Ignoring context limits
- Long prompts = expensive
- Not counting output cost

---

## 10. Token Efficiency Tips

- Short prompts
- Remove repetition
- Structured format
- Concise instructions

---

## 11. Tokenizers Used

BPE, WordPiece, SentencePiece (in GPT, Gemma, Llama)

---

## 12. In RAG Systems

Query → Retrieval → Context (uses tokens) → LLM → Response

---

## 13. Local Models

Tokens matter in Ollama, Gemma for: speed, memory, context

---

## 14. Complete Pipeline

```
Input → Tokenize → Token IDs → LLM Process → 
Token Generation → Output
```

---

## 15. Summary

- Tokens = text chunks
- 1 word ≠ always 1 token
- Cost, speed, limits depend on tokens
- Generate one token at a time
- Optimize for efficiency

---

## 16. Key Takeaway

**Master tokens = understand:**
- LLM billing
- Context management
- Performance control
- Cost optimization
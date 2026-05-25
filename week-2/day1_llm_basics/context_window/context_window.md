# Context Window in LLMs

---

## 1. What is Context Window?

Max tokens an LLM can remember/process. Determines how much information fits in one conversation.

**Measured in tokens, not words.**

---

## 2. How It Works

LLM reads all context within window, generates response based on it.

Example: 4K window → 3K tokens input + 1K output = full window

---

## 3. Why It Matters

- **Long conversations:** Needs larger window
- **Document analysis:** Longer docs need larger window
- **Cost:** Larger window = more tokens = higher cost
- **Quality:** More context = better responses

---

## 4. Common Context Sizes

| Model | Window |
|-------|--------|
| GPT-3.5 | 4K |
| GPT-4 | 128K |
| Claude 3 | 200K |
| Gemma 3 | 128K |
| Llama 2 | 4K |

---

## 5. When You Exceed Context

- Response cuts off
- Old messages removed (sliding window)
- Quality degrades
- May error

---

## 6. Input vs Output Tokens

Both count toward context!

Example (4K limit):
```
Input: 3000 tokens
Output: 1000 tokens
= 4000 (at limit)
```

---

## 7. Tokens vs Words

- 1 word ≈ 1.3 tokens
- 4K context ≈ 3000 words
- 32K context ≈ 24000 words

---

## 8. Use Cases by Size

| Task | Size Needed |
|------|------------|
| Q&A | 2K-4K |
| Chat | 8K-16K |
| Docs | 32K-64K |
| RAG | 8K-32K |

---

## 9. Cost Impact

Larger window = more tokens = higher cost

GPT-4: 8K (cheap) → 32K (4x) → 128K (expensive)

Choose wisely!

---

## 10. Best Practices

- Match model to task size
- Summarize old messages
- Remove unnecessary text
- Monitor token usage
- Split large tasks if needed
- Keep prompts concise

---

## 11. Common Mistakes

- Ignoring context limits
- Using small model for big docs
- Not counting output tokens
- Exceeding window without noticing

---

## 12. Summary

- Context = max tokens in one go
- Both input + output count
- Larger = expensive but flexible
- Choose model based on needs
- Manage context to save costs

---

## 13. Key Takeaway

**Master context to:**
- Pick right model for task
- Control costs
- Process large documents
- Maintain long conversations
- Avoid overflow errors
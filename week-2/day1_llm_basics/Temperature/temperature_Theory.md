# Temperature in LLMs

---

## 1. What is Temperature?

Parameter that controls randomness and creativity in LLM outputs. Higher temperature = more creative. Lower temperature = more factual.

Range: **0.0 to 2.0** (or 0.0 to 1.0 depending on model)

---

## 2. How It Works

LLMs predict next token probabilities. Temperature scales these probabilities:
- **Low:** Sharpens distribution (picks most likely token)
- **High:** Flattens distribution (picks random tokens)

---

## 3. Low Temperature (0.0 - 0.3)

**Behavior:**
- Deterministic (predictable)
- Conservative
- Factual
- Repetitive

**Best for:**
- Coding
- Math
- Q&A
- Factual tasks
- API outputs

**Example:**
```
Q: What is 2+2?
A: 4 (always same answer)
```

---

## 4. High Temperature (0.7 - 1.0)

**Behavior:**
- Non-deterministic (unpredictable)
- Creative
- Diverse
- Random

**Best for:**
- Creative writing
- Brainstorming
- Story generation
- Dialogue
- Content creation

**Example:**
```
Q: Write a story about a cat
A: Different story every time
```

---

## 5. Temperature = 0

Completely deterministic. Always picks the most likely token. Same input = same output always.

---

## 6. Temperature = 1.0

Default for most models. Balanced between randomness and consistency.

---

## 7. Quick Comparison

| Aspect | Low (0.1) | High (0.9) |
|--------|-----------|-----------|
| Deterministic | Yes | No |
| Creative | No | Yes |
| Consistent | Yes | No |
| Reliable | Yes | No |
| Use Case | Coding | Writing |

---

## 8. Real-World Examples

**Coding (Low Temp 0.1-0.3):**
```
Input: "Write a Python function to reverse a list"
Output: Always same correct code
```

**Story Writing (High Temp 0.8):**
```
Input: "Tell me a story"
Output: Different story each time
```

---

## 9. Best Practices

- **Production APIs:** Use low (0.1-0.3)
- **Content generation:** Use medium-high (0.6-0.8)
- **Experiments:** Try different temps
- **Consistency needed:** Use 0.0-0.2

---

## 10. Common Use Cases

| Task | Temperature |
|------|-------------|
| Coding | 0.1-0.3 |
| Math | 0.1-0.3 |
| Q&A | 0.2-0.4 |
| Translation | 0.3-0.5 |
| Dialogue | 0.5-0.7 |
| Creative | 0.7-0.9 |
| Brainstorm | 0.8-1.0 |

---

## 11. How to Set Temperature

**Python (OpenAI):**
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7
)
```

**Python (Gemma/Google):**
```python
model.generate_content(
    "Your prompt",
    generation_config=GenerationConfig(temperature=0.5)
)
```

---

## 12. Temperature vs Top-P

- **Temperature:** Controls randomness
- **Top-P:** Controls diversity (picks top P% likely tokens)

Can be used together for fine control.

---

## 13. Common Mistakes

- Using high temp for coding (unpredictable)
- Using low temp for creative writing (boring)
- Ignoring temperature in production
- Not testing different temps

---

## 14. Key Insight

Temperature doesn't add knowledge. It only controls:
- How the model picks from existing probabilities
- Creativity of response style

---

## 15. Summary

- Temperature controls randomness (0.0-2.0)
- Low = factual, consistent, deterministic
- High = creative, diverse, random
- Choose based on task type
- Production = low, creative = high

---

## 16. Key Takeaway

**Master temperature to:**
- Get consistent outputs for APIs
- Generate creative content
- Control response quality
- Optimize for your use case
# AI Memory — Quick Reference

## What is Memory in AI?
Memory allows an AI system to **retain and recall information** across turns, sessions, or tasks — giving it context beyond a single prompt.

> Without memory, every request is a blank slate. With memory, the AI *remembers*.

---

## Why Memory Matters

| Without Memory | With Memory |
|---|---|
| Forgets previous messages | Maintains conversation context |
| Repeats questions | Builds on prior answers |
| No personalization | Learns user preferences |
| Stateless | Stateful |

---

## How Memory Works

```
User Message
     ↓
Load Memory  ←── Memory Store
     ↓
Build Prompt (message + memory)
     ↓
LLM generates response
     ↓
Save to Memory ──→ Memory Store
     ↓
Return Response
```

---

## Memory Types

### 1. Buffer Memory
Stores the **full conversation history** as-is.

```
Turn 1: User: "My name is Arjun"
Turn 2: User: "What's my name?" → LLM: "Arjun"
```
- Simple and accurate
- Problem: grows large, hits context limit fast

---

### 2. Summary Memory
Compresses old history into a **running summary**.

```
Summary: "User is Arjun, building a RAG chatbot in Python."
+ recent messages
```
- Handles long sessions
- Loses fine-grained detail

---

### 3. Buffer Window Memory
Keeps only the **last N messages**.

```
Window = 5 → always keeps last 5 turns
```
- Simple, predictable size
- Loses older context

---

### 4. Vector Memory
Stores messages as **embeddings**, retrieves by semantic similarity.

```
User: "What was the database I mentioned?"
→ searches memory → returns relevant past message
```
- Best for long-term, large-scale memory
- Needs a vector store (Chroma, FAISS, Pinecone)

---

### 5. Entity Memory
Tracks specific **facts about people, places, or things**.

```
Entities: { "Arjun": "developer, building RAG app, uses Python" }
```
- Great for assistants and CRM-style apps
- Structured, queryable

---

## Memory Scope

| Scope | Description | Example |
|---|---|---|
| **In-context** | Lives inside the prompt | Buffer, window |
| **External** | Lives outside, retrieved when needed | Vector, entity |
| **Short-term** | Single session only | Buffer, summary |
| **Long-term** | Persists across sessions | Vector DB, DB storage |

---

## Memory in LangChain

```python
from langchain.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from langchain.chains import ConversationChain

llm = OllamaLLM(model="llama3.2")

memory = ConversationBufferMemory()

chain = ConversationChain(llm=llm, memory=memory)

chain.invoke("My name is Arjun")
chain.invoke("What is my name?")  # → "Arjun"
```

Swap `ConversationBufferMemory` with any other type — API stays the same.

---

## LangChain Memory Classes

| Class | Type |
|---|---|
| `ConversationBufferMemory` | Full history |
| `ConversationSummaryMemory` | Compressed summary |
| `ConversationBufferWindowMemory` | Last N turns |
| `ConversationVectorStoreMemory` | Semantic retrieval |
| `ConversationEntityMemory` | Entity tracking |

---

## Choosing the Right Memory

```
Short conversation?          → Buffer Memory
Long conversation?           → Summary Memory
Very long / multi-session?   → Vector Memory
Need to track facts/people?  → Entity Memory
Simple, fixed size?          → Window Memory
```

---

## Memory in Multi-Agent Systems

```
Agent A (Researcher) ──┐
                        ├──→ Shared Memory Store ──→ Agent C (Writer)
Agent B (Coder)    ────┘
```

Agents share a common memory layer — each reads and writes to the same store.

---

## Common Problems

| Problem | Cause | Fix |
|---|---|---|
| **Context overflow** | Buffer too large | Use summary or window memory |
| **Hallucinated recall** | LLM guesses memory | Use explicit retrieval |
| **Stale memory** | Outdated facts stored | Add expiry or refresh logic |
| **Privacy risk** | Sensitive data persisted | Encrypt or scope storage |
| **No persistence** | Memory lost on restart | Save to DB or vector store |

---

## Best Practices

- Always **summarize** long sessions before context limit is hit
- Store long-term memory in a **persistent vector store**
- **Scope memory** per user — never mix between users
- **Log memory reads/writes** in production
- Use **entity memory** when tracking structured facts
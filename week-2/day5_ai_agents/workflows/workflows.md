# AI Workflows — Quick Reference

## What is a Workflow?
A sequence of steps connecting **inputs → processing → AI models → outputs** to complete a task. Used in chatbots, RAG systems, agents, and automation pipelines.

---

## Core Components

| Component | Description |
|---|---|
| **Input** | User query, file, API data |
| **Processing** | Logic, chunking, retrieval, prompting |
| **LLM** | Generates reasoning or answers |
| **Output** | Final response or action |

---

## Common Workflow Patterns

**Simple LLM:**
```
User Prompt → Prompt Template → LLM → Response
```

**RAG:**
```
Documents → Chunking → Embeddings → Vector DB → Retriever → LLM → Answer
```

**AI Agent:**
```
User Query → LLM Reasoning → Choose Tool → Execute Tool → Observe → Final Answer
```

**Automation (n8n-style):**
```
Trigger → AI Model → Database → Notification
```

---

## Workflow Types

| Type | Pattern | Use Case |
|---|---|---|
| **Sequential** | `A → B → C → D` | Most common, beginner-friendly |
| **Parallel** | `Input → [Task A, Task B]` | Performance optimization |
| **Conditional** | `Input → Condition → Path A/B` | Agents, automation |

---

## Stateless vs Stateful

- **Stateless** — no memory between requests (simple API calls)
- **Stateful** — maintains history/context (chatbots, assistants)

---

## Orchestration Tools

| Tool | Best For |
|---|---|
| **LangChain** | Prompts, retrieval, chains, memory |
| **LangGraph** | Agents, branching, multi-step reasoning |
| **n8n** | Visual automation, API integrations |
| **Airflow / Prefect** | Production pipeline scheduling |

---

## Production Concerns

- **Optimization:** caching, batching, async, streaming, retry handling
- **Monitoring:** response time, failures, token usage, retrieval quality
- **Common Problems:** too many steps, poor retrieval, latency, hallucinations, context overflow

---

## Real-World Examples

| System | Workflow |
|---|---|
| AI Chatbot | Prompt → LLM → Response |
| PDF Assistant | PDF → Chunking → Retrieval → Answer |
| AI Agent | Question → Tool Selection → Execution → Answer |
| Semantic Search | Docs → Embeddings → Vector DB → Query → Results |
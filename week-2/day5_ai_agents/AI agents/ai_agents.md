# AI Agents — Quick Reference

## What is an AI Agent?
An AI agent is an LLM that can **reason, plan, and take actions** using tools to complete a goal — not just generate text.

> Key difference: A regular LLM *responds*. An agent *acts*.

---

## Agent vs LLM vs Chain

| | LLM | Chain | Agent |
|---|---|---|---|
| **Decides steps?** | No | No | Yes |
| **Uses tools?** | No | Sometimes | Yes |
| **Dynamic flow?** | No | No | Yes |
| **Memory?** | No | Optional | Optional |

---

## How an Agent Works

```
User Goal
    ↓
LLM Reasoning  ←─────────────┐
    ↓                         │
Choose Action                 │
    ↓                         │
Execute Tool                  │
    ↓                         │
Observe Result ───────────────┘
    ↓ (when goal is complete)
Final Answer
```

This loop is called **ReAct** (Reason + Act).

---

## Core Components

| Component | Role |
|---|---|
| **LLM** | Brain — reasons and decides |
| **Tools** | Hands — search, code, APIs, DBs |
| **Memory** | History — short-term or long-term |
| **Planner** | Breaks goals into sub-tasks |
| **Executor** | Runs the chosen actions |

---

## Common Agent Tools

| Tool | Purpose |
|---|---|
| Web Search | Fetch current information |
| Code Executor | Run Python/JS code |
| Calculator | Math operations |
| Vector DB | Retrieve documents |
| API Caller | Interact with external services |
| File Reader | Read PDFs, CSVs, docs |
| Database | Query SQL/NoSQL |

---

## Agent Types

| Type | Description |
|---|---|
| **ReAct Agent** | Alternates reasoning and acting in a loop |
| **Plan-and-Execute** | Plans all steps first, then executes |
| **Multi-Agent** | Multiple agents collaborate on sub-tasks |
| **Tool-Calling Agent** | Uses structured tool/function calling |
| **Self-Reflective** | Reviews and corrects its own output |

---

## Memory Types

| Type | Description | Use Case |
|---|---|---|
| **Buffer** | Full conversation history | Short chats |
| **Summary** | Compressed history | Long sessions |
| **Vector** | Semantic memory search | Large context |
| **Entity** | Tracks specific facts/people | Assistants |

---

## Popular Frameworks

| Framework | Best For |
|---|---|
| **LangChain Agents** | Tool-calling, RAG agents |
| **LangGraph** | Stateful, multi-step, branching agents |
| **AutoGen** | Multi-agent collaboration |
| **CrewAI** | Role-based agent teams |
| **OpenAI Assistants** | Hosted tool-calling agents |

---

## Multi-Agent Architecture

```
User Goal
    ↓
Orchestrator Agent
    ├── Research Agent  → Web Search
    ├── Coding Agent    → Code Executor
    └── Writer Agent    → LLM Output
    ↓
Final Result
```

---

## Common Use Cases

| Use Case | Tools Used |
|---|---|
| Research Assistant | Web search, summarizer |
| Code Assistant | Code executor, file reader |
| PDF Q&A | Vector DB, retriever |
| Data Analyst | SQL, calculator, code |
| Customer Support | DB lookup, API, memory |
| Automation | APIs, email, calendar |

---

## Common Problems

| Problem | Cause |
|---|---|
| **Hallucination** | LLM invents tool outputs |
| **Infinite loops** | Agent can't decide to stop |
| **Tool misuse** | Wrong tool selected |
| **Context overflow** | Too much history in prompt |
| **Slow execution** | Too many sequential tool calls |

---

## Production Best Practices

- Set a **max iteration limit** to prevent loops
- Use **structured tool outputs** (JSON)
- Add **memory summarization** for long sessions
- **Log every tool call** for debugging
- Use **streaming** for better UX
- Add **fallback behavior** when tools fail
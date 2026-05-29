# AI Tools — Quick Reference

## What are Tools in AI?
Tools are **external functions** an LLM can call to interact with the real world — fetch data, run code, query databases, or trigger actions.

> Without tools, LLMs only generate text. With tools, they can *act*.

---

## How Tool Calling Works

```
User Request
     ↓
LLM decides a tool is needed
     ↓
LLM outputs structured tool call (name + args)
     ↓
System executes the tool
     ↓
Result returned to LLM
     ↓
LLM generates final response
```

---

## Tool Call Structure (JSON)

```json
{
  "tool": "web_search",
  "arguments": {
    "query": "latest AI news 2025"
  }
}
```

LLMs like GPT-4, Claude, and Gemini support this natively via **function calling**.

---

## Categories of Tools

| Category | Examples |
|---|---|
| **Search** | Web search, news search, Wikipedia |
| **Code** | Python executor, shell, REPL |
| **Data** | SQL query, CSV reader, spreadsheet |
| **Files** | PDF reader, DOCX, file system |
| **APIs** | REST calls, weather, maps, payments |
| **Memory** | Vector DB lookup, cache read/write |
| **Communication** | Email, Slack, calendar, SMS |
| **Media** | Image gen, OCR, audio transcription |

---

## Built-in LangChain Tools

| Tool | Purpose |
|---|---|
| `DuckDuckGoSearch` | Web search |
| `WikipediaQueryRun` | Wikipedia lookup |
| `PythonREPLTool` | Run Python code |
| `SQLDatabaseTool` | Query SQL databases |
| `ArxivQueryRun` | Search research papers |
| `HumanInputRun` | Ask human for input |

---

## Custom Tool (LangChain)

```python
from langchain.tools import tool

@tool
def get_word_count(text: str) -> int:
    """Returns the word count of the given text."""
    return len(text.split())
```

Three things needed:
1. **Function** — the logic
2. **Docstring** — tells LLM when to use it
3. **Type hints** — defines input/output

---

## Tool vs Chain vs Agent

| | Chain | Tool | Agent |
|---|---|---|---|
| **Fixed steps?** | Yes | No | No |
| **LLM decides?** | No | No | Yes |
| **External action?** | Sometimes | Yes | Yes |
| **Dynamic?** | No | No | Yes |

---

## Tool Selection — How LLM Chooses

LLM reads the tool's **name + description** and picks the best match.

```
Available tools:
- web_search: Search the internet for current info
- calculator: Perform math operations
- sql_query: Query a database

User: "What is 25 * 48?"
LLM picks → calculator
```

Good tool descriptions = better tool selection.

---

## Parallel vs Sequential Tool Use

**Sequential** — one tool at a time:
```
Search → Summarize → Write
```

**Parallel** — multiple tools at once:
```
Query DB ──┐
Search Web ─┼─→ LLM → Final Answer
Read PDF ──┘
```

Parallel is faster but needs careful result merging.

---

## Popular External Tool Integrations

| Service | Use |
|---|---|
| **Serper / Tavily** | Google search API |
| **Wolfram Alpha** | Math & science queries |
| **OpenWeatherMap** | Weather data |
| **Stripe** | Payment processing |
| **Notion / Airtable** | Knowledge base |
| **GitHub** | Code repo access |
| **Zapier** | 5000+ app integrations |

---

## Tool Safety & Best Practices

| Practice | Why |
|---|---|
| Validate inputs | Prevent bad/malicious args |
| Set timeouts | Avoid hanging calls |
| Handle errors gracefully | Return useful fallback |
| Limit permissions | Least-privilege principle |
| Log all tool calls | Debugging & monitoring |
| Rate limit external APIs | Avoid quota exhaustion |

---

## Common Problems

| Problem | Cause |
|---|---|
| **Wrong tool selected** | Vague tool description |
| **Hallucinated args** | LLM guesses missing inputs |
| **Tool failure ignored** | No error handling |
| **Slow pipeline** | Too many sequential calls |
| **Security risk** | Unvalidated shell/code tools |